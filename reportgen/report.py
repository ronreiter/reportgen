from typing import Optional, Union, List, Dict, Any
import json
from pathlib import Path
import pandas as pd
import vl_convert as vlc
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import base64
from .models import ReportConfig, ReportData, SectionConfig, DataSource


class Report:
    config: ReportConfig

    def __init__(self, config: Union[str, Path, ReportConfig]):
        if isinstance(config, (str, Path)):
            with open(config) as f:
                config = ReportConfig.model_validate(json.load(f))
        elif isinstance(config, dict):
            config = ReportConfig.model_validate(config)

        self.config = config
        # Set up Jinja2 environment
        templates_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(templates_dir))

    async def _fetch_sql_data(self, data_source: DataSource) -> Dict[str, Any]:
        """Fetch data from SQL database"""
        if data_source.connection_id not in self.config.connections:
            raise ValueError(
                f"Connection ID '{data_source.connection_id}' not found in connections"
            )

        connection_config = self.config.connections[data_source.connection_id]
        engine = create_async_engine(connection_config.connection_string)

        async with engine.connect() as conn:
            query = text(data_source.query)
            # Use global parameters if available
            parameters = self.config.parameters or {}
            result = await conn.execute(query, parameters)
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def _get_section_data(
        self, section: SectionConfig, data: Optional[ReportData] = None
    ) -> Any:
        """Get data for a section from either SQL or JSON source"""
        # Use section-specific data source if available, otherwise use report-level data source
        data_source = section.data_source or self.config.data_source

        if not data_source:
            if not data or section.section_id not in data.data:
                return None
            return data.data[section.section_id]

        if data_source.type == "sql":
            return await self._fetch_sql_data(data_source)
        else:  # json
            return data_source.data.get(section.section_id)

    async def _generate_html(self, data: Optional[ReportData] = None) -> List[str]:
        """Generate HTML content for the report"""
        sections_html: List[str] = []

        for section in self.config.sections:
            section_data = await self._get_section_data(section, data)
            if not section_data:
                continue

            section_style = (
                f"grid-row: {section.grid.row_start + 1} / {section.grid.row_end + 1}; "
                f"grid-column: {section.grid.col_start + 1} / {section.grid.col_end + 1};"
            )

            if section.type == "graph":
                # Convert Vega-Lite spec to SVG
                chart_spec = (
                    section.config.vega_lite_spec.copy()
                )  # Make a copy to avoid modifying the original
                chart_spec["data"] = {"values": section_data}  # Always set the data
                svg_data = vlc.vegalite_to_svg(chart_spec)

                section_html = f"""
                <div class="section graph" style="{section_style}">
                    {f'<h3>{section.name}</h3>' if section.name else ''}
                    {svg_data}
                </div>
                """

            elif section.type == "table":
                # Create DataFrame and generate table HTML
                df = pd.DataFrame(section_data)
                if len(df) > section.config.max_results:
                    df = df.head(section.config.max_results)

                # Format the columns based on configuration
                formatters = {}
                classes = {}
                for col in section.config.columns:
                    if col.type == "number":
                        if col.format and col.format == "0,0":
                            formatters[col.name] = lambda x: f"{int(x):,}"
                            classes[col.name] = "number"
                        elif col.format and col.format.startswith("$"):
                            formatters[col.name] = lambda x: f"${float(x):,.2f}"
                            classes[col.name] = "currency"
                        else:
                            formatters[col.name] = lambda x: f"{float(x):,}"
                            classes[col.name] = "number"

                def format_td(value, column):
                    css_class = classes.get(column, "")
                    formatter = formatters.get(column)
                    try:
                        formatted_value = formatter(value) if formatter else value
                    except (ValueError, TypeError):
                        formatted_value = value
                    return f'<td class="{css_class}">{formatted_value}</td>'

                # Generate custom HTML with proper formatting
                headers = [f"<th>{col}</th>" for col in df.columns]
                header_row = f"<tr>{''.join(headers)}</tr>"

                rows = []
                for _, row in df.iterrows():
                    cells = [format_td(row[col], col) for col in df.columns]
                    rows.append(f"<tr>{''.join(cells)}</tr>")

                table_html = f"""
                <table class="data-table">
                    <thead>{header_row}</thead>
                    <tbody>{''.join(rows)}</tbody>
                </table>
                """

                section_html = f"""
                <div class="section table" style="{section_style}">
                    {f'<h3>{section.name}</h3>' if section.name else ''}
                    {table_html}
                </div>
                """
            else:
                raise Exception(f"Unsupported section type: {section.type}")

            sections_html.append(section_html)

        return sections_html

    def _render_section(self, section: Dict[str, Any]) -> str:
        template = self.jinja_env.get_template(f"{section['type']}.html")
        return template.render(**section)

    def _render_html(self, sections_html: List[str]) -> str:
        # Prepare logo data if present
        logo_data = None
        if self.config.logo_path:
            logo_path = Path(self.config.logo_path)
            if logo_path.exists():
                with open(logo_path, "rb") as f:
                    logo_bytes = f.read()
                    logo_data = (
                        f"data:image/png;base64,{base64.b64encode(logo_bytes).decode()}"
                    )

        # Render main template with sections
        template = self.jinja_env.get_template("report.html")
        return template.render(
            title=self.config.title, logo_data=logo_data, sections_html=sections_html
        )

    async def render_html(self):
        """Generate HTML report using the configuration and data"""

        sections_html = await self._generate_html(self.config)
        return self._render_html(sections_html)

    async def save_pdf(self, output_path: Union[str, Path] = None):
        """Generate a PDF report using the configuration and data"""
        # Convert HTML to PDF using WeasyPrint with custom margins

        html_content = await self.render_html()

        margin = f"{self.config.margin}px"
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[
                CSS(
                    string=f"""
                @page {{
                    margin: {margin};
                    size: {self.config.paper_size} {self.config.orientation};
                }}
            """
                )
            ],
        )
