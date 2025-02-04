from typing import Optional, Union, List, Dict, Any
import json
from pathlib import Path
import pandas as pd
import altair as alt
import vl_convert as vlc
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import asyncio
import base64
from .models import ReportConfig, ReportData, SectionConfig, DataSource

class Report:
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
            raise ValueError(f"Connection ID '{data_source.connection_id}' not found in connections")
            
        connection_config = self.config.connections[data_source.connection_id]
        engine = create_async_engine(connection_config.connection_string)
        
        async with engine.connect() as conn:
            query = text(data_source.query)
            # Use global parameters if available
            parameters = self.config.parameters or {}
            result = await conn.execute(query, parameters)
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def _get_section_data(self, section: SectionConfig, data: Optional[ReportData] = None) -> Any:
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
        sections_html = []
        
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
                chart_spec = section.config.vega_lite_spec.copy()  # Make a copy to avoid modifying the original
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
            
            sections_html.append(section_html)
        
        return sections_html
        
    def _render_html(self, sections_html: List[str]) -> str:
        """Render the final HTML report."""
        template = self.jinja_env.get_template("report.html")
        
        logo_data = None
        if self.config.logo_path:
            logo_path = Path(self.config.logo_path)
            if logo_path.exists():
                with open(logo_path, "rb") as f:
                    logo_data = base64.b64encode(f.read()).decode()

        html_content = template.render(
            sections_html=sections_html,
            page_width=self.config.page_dimensions[0] - 2 * self.config.margin,
            page_height=self.config.page_dimensions[1] - 2 * self.config.margin,
            logo_data=logo_data,
            title=self.config.title
        )
        
        return html_content
        
    async def generate(self, data: Optional[Union[str, Path, ReportData]] = None, output_path: Union[str, Path] = None):
        """Generate a PDF report using the configuration and data"""
        if isinstance(data, (str, Path)):
            with open(data) as f:
                data = ReportData.model_validate(json.load(f))
        elif isinstance(data, dict):
            data = ReportData.model_validate(data)
            
        sections_html = await self._generate_html(data)
        html_content = self._render_html(sections_html)
        
        # Convert HTML to PDF using WeasyPrint
        HTML(string=html_content).write_pdf(output_path)
