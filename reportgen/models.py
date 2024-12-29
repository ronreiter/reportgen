from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from pathlib import Path

class GridPosition(BaseModel):
    row_start: int
    row_end: int
    col_start: int
    col_end: int

class TableColumnConfig(BaseModel):
    name: str
    type: str  # could be 'string', 'number', 'date', etc.

class TableConfig(BaseModel):
    columns: List[TableColumnConfig]
    max_results: int = 100

class GraphConfig(BaseModel):
    vega_lite_spec: dict

class SectionConfig(BaseModel):
    section_id: str
    name: Optional[str] = None
    type: Literal["table", "graph"]
    grid: GridPosition
    config: Union[TableConfig, GraphConfig]

class ReportConfig(BaseModel):
    sections: List[SectionConfig]
    orientation: Literal["portrait", "landscape"] = "portrait"
    paper_size: Literal["a4"] = "a4"  # We can add more sizes like "letter", "a3" etc. as needed
    margin: float = 36  # 0.5 inch margins
    logo_path: Optional[str] = None  # Path to logo file, relative to project root

    @property
    def page_dimensions(self) -> tuple[float, float]:
        """Return page dimensions in points (1/72 inch)"""
        # A4 dimensions in points (595.276 x 841.890)
        if self.paper_size == "a4":
            width, height = 595.276, 841.890
            return (width, height) if self.orientation == "portrait" else (height, width)
        raise ValueError(f"Unsupported paper size: {self.paper_size}")

class ReportData(BaseModel):
    data: Dict[str, Union[List[dict], dict]]  # section_id -> data
