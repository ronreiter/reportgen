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
        engine = create_async_engine(data_source.connection_string)
        async with engine.connect() as conn:
            query = text(data_source.query)
            parameters = data_source.parameters or {}
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
                
                table_html = df.to_html(classes="data-table", index=False)
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
