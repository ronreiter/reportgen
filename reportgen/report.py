from typing import Optional, Union, List
import json
from pathlib import Path
import pandas as pd
import altair as alt
import vl_convert as vlc
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from .models import ReportConfig, ReportData, SectionConfig
import base64

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
        
    def _generate_html(self, data: ReportData) -> str:
        """Generate HTML content for the report"""
        sections_html = []
        
        for section in self.config.sections:
            section_data = data.data.get(section.section_id)
            if not section_data:
                continue
                
            section_style = (
                f"grid-row: {section.grid.row_start + 1} / {section.grid.row_end + 1}; "
                f"grid-column: {section.grid.col_start + 1} / {section.grid.col_end + 1};"
            )
            
            if section.type == "graph":
                # Convert Vega-Lite spec to SVG
                chart_spec = section.config.vega_lite_spec
                if "data" in chart_spec:
                    chart_spec["data"]["values"] = section_data
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
            logo_data=logo_data
        )
        
        return html_content
        
    def generate(self, data: Union[str, Path, ReportData], output_path: Union[str, Path]):
        """Generate a PDF report using the configuration and data"""
        if isinstance(data, (str, Path)):
            with open(data) as f:
                data = ReportData.model_validate(json.load(f))
        elif isinstance(data, dict):
            data = ReportData.model_validate(data)
            
        sections_html = self._generate_html(data)
        html_content = self._render_html(sections_html)
        
        # Convert HTML to PDF using WeasyPrint
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[],
            presentational_hints=True
        )

    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'Report':
        """Create a Report instance from a configuration file"""
        return cls(config_path)
