from typing import Dict, List, Optional, Union, Literal, Any
from pydantic import BaseModel, Field, validator
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

class DataSource(BaseModel):
    type: Literal["json", "sql"]
    connection_string: Optional[str] = None
    query: Optional[str] = None
    data: Optional[Dict[str, Union[List[dict], dict]]] = None
    parameters: Optional[Dict[str, Any]] = None

    @validator("connection_string")
    def validate_connection_string(cls, v, values):
        if values.get("type") == "sql" and not v:
            raise ValueError("connection_string is required for SQL data source")
        return v

    @validator("query")
    def validate_query(cls, v, values):
        if values.get("type") == "sql" and not v:
            raise ValueError("query is required for SQL data source")
        return v

    @validator("data")
    def validate_data(cls, v, values):
        if values.get("type") == "json" and not v:
            raise ValueError("data is required for JSON data source")
        return v

class SectionConfig(BaseModel):
    section_id: str
    name: Optional[str] = None
    type: Literal["table", "graph"]
    grid: GridPosition
    config: Union[TableConfig, GraphConfig]
    data_source: Optional[DataSource] = None  # If not provided, use report-level data source

class ReportConfig(BaseModel):
    sections: List[SectionConfig]
    title: Optional[str] = None
    orientation: Literal["portrait", "landscape"] = "portrait"
    paper_size: Literal["a4"] = "a4"  # We can add more sizes like "letter", "a3" etc. as needed
    margin: float = 36  # 0.5 inch margins
    logo_path: Optional[str] = None  # Path to logo file, relative to project root
    data_source: Optional[DataSource] = None  # Default data source for all sections

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
