# ReportGen

A flexible Python library for generating beautiful PDF reports from JSON configurations and data. ReportGen makes it easy to create professional-looking reports with graphs, tables, and custom layouts.

## Features

- **Dynamic Graphs**: Create interactive graphs using Vega-Lite specifications
- **Customizable Tables**: Generate tables with custom columns and formatting
- **Grid Layout System**: Position elements precisely using a 12-column grid
- **Professional Styling**: Clean, modern design with customizable themes
- **Logo Support**: Add your company logo to reports
- **Standard Paper Sizes**: Support for A4 in portrait and landscape orientations
- **CLI Tool**: Generate reports directly from the command line

## Installation

```bash
pip install reportgen
```

Or using Poetry:

```bash
poetry add reportgen
```

## Quick Start

1. Create a configuration file (`sales_report_config.json`):

```json
{
    "title": "Sales Performance Report",
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
                        "x": {
                            "field": "month",
                            "type": "temporal",
                            "title": "Month"
                        },
                        "y": {
                            "field": "sales",
                            "type": "quantitative",
                            "title": "Sales ($)"
                        }
                    }
                }
            }
        }
    ],
    "orientation": "portrait",
    "paper_size": "a4",
    "margin": 36,
    "logo_path": "assets/logo.png"
}
```

2. Create a data file (`sales_report_data.json`):

```json
{
    "data": {
        "monthly_sales": [
            {"month": "2024-01", "sales": 45000},
            {"month": "2024-02", "sales": 52000}
        ]
    }
}
```

3. Generate the report using the CLI:

```bash
reportgen sales_report_config.json sales_report_data.json -o report.pdf
```

Or using the Python API:

```python
from reportgen import Report

report = Report("sales_report_config.json")
report.generate("sales_report_data.json", "report.pdf")
```

## Configuration

### Report Configuration

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `title` | string | Report title | None |
| `sections` | array | List of report sections | Required |
| `orientation` | string | "portrait" or "landscape" | "portrait" |
| `paper_size` | string | Paper size (currently "a4") | "a4" |
| `margin` | number | Page margin in points | 36 |
| `logo_path` | string | Path to logo file | None |

### Section Configuration

| Field | Type | Description |
|-------|------|-------------|
| `section_id` | string | Unique identifier for the section |
| `name` | string | Section title (optional) |
| `type` | string | "graph" or "table" |
| `grid` | object | Grid position configuration |
| `config` | object | Section-specific configuration |

## Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reportgen.git
cd reportgen
```

2. Install dependencies:
```bash
poetry install
```

3. Run tasks using Task:
```bash
# Generate example sales report
task sales-report

# Run tests
task test

# Format code
task format

# Clean generated files
task clean
```

## Requirements

- Python 3.9 or later
- WeasyPrint dependencies (see [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html))

## License

MIT License
