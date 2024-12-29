# ReportGen

A Python library for generating PDF reports from JSON configurations. Define your report layout using a grid system and create beautiful reports with tables and graphs using Vega-Lite specifications.

## Features

- Grid-based layout system using CSS Grid
- Support for tables and graphs
- Vega-Lite specification for creating beautiful visualizations
- Configurable table columns and row limits
- Flexible page size and margins
- Modern HTML/CSS rendering with WeasyPrint

## Installation

ReportGen requires Python 3.9 or later. Install using Poetry:

```bash
poetry install
```

## Usage

### Command Line Interface

```bash
# Generate a report from JSON configuration and data files
poetry run reportgen config.json data.json -o output.pdf
```

### Python API

```python
from reportgen import Report

# Create a report from configuration
report = Report("config.json")

# Generate PDF using data
report.generate("data.json", "output.pdf")
```

### Configuration Format

The report configuration is defined in JSON:

```json
{
    "sections": [
        {
            "section_id": "monthly_sales",
            "name": "Monthly Sales Trend",
            "type": "graph",
            "grid": {
                "row_start": 0,
                "row_end": 3,
                "col_start": 0,
                "col_end": 12
            },
            "config": {
                "vega_lite_spec": {
                    "mark": {"type": "line", "point": true},
                    "encoding": {
                        "x": {"field": "month", "type": "temporal"},
                        "y": {"field": "sales", "type": "quantitative"}
                    }
                }
            }
        },
        {
            "section_id": "top_products",
            "name": "Top Products",
            "type": "table",
            "grid": {
                "row_start": 3,
                "row_end": 6,
                "col_start": 0,
                "col_end": 12
            },
            "config": {
                "columns": [
                    {"name": "Product", "type": "string"},
                    {"name": "Units Sold", "type": "number"},
                    {"name": "Revenue", "type": "number"}
                ],
                "max_results": 10
            }
        }
    ],
    "grid_size": [12, 12],
    "page_size": [612, 792],
    "margin": 36
}
```

### Data Format

The data file should provide data for each section using section IDs:

```json
{
    "data": {
        "monthly_sales": [
            {"month": "2024-01", "sales": 45000},
            {"month": "2024-02", "sales": 52000}
        ],
        "top_products": [
            {
                "Product": "Premium Coffee Maker",
                "Units Sold": 1200,
                "Revenue": 360000
            }
        ]
    }
}
```

## Development

ReportGen uses Poetry for dependency management. Here are some useful commands:

```bash
# Install dependencies including development tools
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Build package
poetry build

# Publish to PyPI
poetry publish
```

## Examples

Check out the `examples` directory for sample configurations and data files:
- `examples/sales_report_config.json`: Example report configuration
- `examples/sales_report_data.json`: Example data file

## License

MIT License
