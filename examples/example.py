from reportgen import Report
import json

# Example configuration
config = {
    "sections": [
        {
            "section_id": "monthly_sales",
            "name": "Monthly Sales",
            "type": "graph",
            "grid": {
                "row_start": 0,
                "row_end": 3,
                "col_start": 0,
                "col_end": 12
            },
            "config": {
                "vega_lite_spec": {
                    "mark": "line",
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
                    {"name": "Sales", "type": "number"},
                    {"name": "Revenue", "type": "number"}
                ],
                "max_results": 10
            }
        }
    ]
}

# Example data
data = {
    "data": {
        "monthly_sales": [
            {"month": "2024-01", "sales": 100},
            {"month": "2024-02", "sales": 120},
            {"month": "2024-03", "sales": 140},
            {"month": "2024-04", "sales": 160}
        ],
        "top_products": [
            {"Product": "Widget A", "Sales": 1000, "Revenue": 50000},
            {"Product": "Widget B", "Sales": 800, "Revenue": 40000},
            {"Product": "Widget C", "Sales": 600, "Revenue": 30000}
        ]
    }
}

# Create and generate the report
report = Report(config)
report.generate(data, "example_report.pdf")
