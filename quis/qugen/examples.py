"""
Default few-shot examples for QUGEN prompt (paper: example table schemas and sample Insight Cards).
"""

from .models import InsightCard, TableSchema

# Example from paper Figure 2 (Employee performance)
EXAMPLE_SCHEMA_1 = TableSchema(
    table_name="Employee",
    columns=[
        {"name": "Year", "dtype": "INT"},
        {"name": "Department", "dtype": "CHAR"},
        {"name": "Performance", "dtype": "DOUBLE"},
    ],
)

EXAMPLE_CARDS_1 = [
    InsightCard(
        reason="To analyse whether there are any trends in the average performance of employees over time.",
        question="How has employee performance varied over the years?",
        breakdown="Year",
        measure="MEAN(Performance)",
    ),
]

# Second example: Sales-like schema
EXAMPLE_SCHEMA_2 = TableSchema(
    table_name="Sales",
    columns=[
        {"name": "Region", "dtype": "CHAR"},
        {"name": "Product", "dtype": "CHAR"},
        {"name": "TotalSales", "dtype": "INT"},
        {"name": "UnitsSold", "dtype": "INT"},
    ],
)

EXAMPLE_CARDS_2 = [
    InsightCard(
        reason="To compare sales performance across regions.",
        question="Which region has the highest total sales?",
        breakdown="Region",
        measure="SUM(TotalSales)",
    ),
]


def get_default_few_shot_examples() -> list[tuple[TableSchema, list[InsightCard]]]:
    """Return default few-shot (schema, cards) for QUGEN prompt (paper: in-context examples)."""
    return [
        (EXAMPLE_SCHEMA_1, EXAMPLE_CARDS_1),
        (EXAMPLE_SCHEMA_2, EXAMPLE_CARDS_2),
    ]
