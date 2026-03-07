"""
Data models for QUGEN: Insight Card and Table Schema (per paper Section 2, Figure 2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TableSchema:
    """Schema of the table: name, columns with types (and optional descriptions)."""

    table_name: str
    columns: list[dict]  # [{"name": str, "dtype": str, "description": Optional[str]}]

    def to_prompt_string(self) -> str:
        lines = [f"{self.table_name} ("]
        for col in self.columns:
            name = col.get("name", "")
            dtype = col.get("dtype", "")
            desc = col.get("description")
            if desc:
                lines.append(f"  {name} {dtype}  # {desc}")
            else:
                lines.append(f"  {name} {dtype}")
        lines.append(")")
        return "\n".join(lines)


@dataclass
class InsightCard:
    """
    Insight Card (Figure 2): Question, Reason, Breakdown B, Measure M.
    Used by both QUGEN (for iteration/coverage) and ISGEN (for insight search).
    """

    question: str
    reason: str
    breakdown: str  # B: breakdown dimension
    measure: str    # M: e.g. MEAN(Performance), COUNT(*)

    def to_prompt_string(self) -> str:
        return (
            f"REASON: {self.reason}\n"
            f"QUESTION: {self.question}\n"
            f"BREAKDOWN: {self.breakdown}\n"
            f"MEASURE: {self.measure}"
        )

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "reason": self.reason,
            "breakdown": self.breakdown,
            "measure": self.measure,
        }

    @classmethod
    def from_dict(cls, d: dict) -> InsightCard:
        return cls(
            question=d.get("question", "").strip(),
            reason=d.get("reason", "").strip(),
            breakdown=d.get("breakdown", "").strip(),
            measure=d.get("measure", "").strip(),
        )


def schema_from_dataframe(df, table_name: str = "Table") -> TableSchema:
    """Build TableSchema from a pandas DataFrame (column names and dtypes)."""
    import pandas as pd
    columns = []
    for name in df.columns:
        s = df[name]
        if pd.api.types.is_integer_dtype(s):
            dtype = "INT"
        elif pd.api.types.is_float_dtype(s):
            dtype = "DOUBLE"
        else:
            dtype = "CHAR"
        columns.append({"name": str(name), "dtype": dtype})
    return TableSchema(table_name=table_name, columns=columns)
