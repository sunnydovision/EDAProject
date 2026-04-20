"""
Basic statistics for QUGEN input (paper Section 3.1.1, Figure 7).
Generate basic statistical questions via LLM, optionally run on dataset and turn into NL descriptions.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .llm_client import BaseLLMClient, get_default_llm_client
from .prompts import build_stats_prompt
from .models import TableSchema

if TYPE_CHECKING:
    import pandas as pd


def parse_stat_questions(llm_output: str) -> list[str]:
    """Parse [STAT]...[/STAT] lines from Figure 7 prompt response."""
    questions = []
    pattern = re.compile(r"\[STAT\](.*?)\[/STAT\]", re.DOTALL | re.IGNORECASE)
    for m in pattern.finditer(llm_output):
        q = m.group(1).strip()
        if q:
            questions.append(q)
    return questions


class BasicStatsGenerator:
    """
    Generates natural language statistics for the table (paper: prompt LLM with Figure 7,
    then transform to SQL, apply to dataset, translate to NL).
    """

    def __init__(self, llm_client: BaseLLMClient | None = None):
        self.llm = llm_client or get_default_llm_client()

    def generate_stat_questions(self, table_schema: TableSchema) -> list[str]:
        """Step 1: LLM generates basic statistical questions (Figure 7)."""
        prompt = build_stats_prompt(table_schema)
        response = self.llm.complete(prompt, temperature=0.3, max_tokens=512)
        return parse_stat_questions(response)

    def stats_to_natural_language(
        self,
        stat_questions: list[str],
        table_schema: TableSchema,
        df: "pd.DataFrame | None" = None,
    ) -> str:
        """
        Turn stat questions into natural language summary lines.
        If df is provided, we can run simple aggregations and append results (e.g. " - Two payment methods").
        Otherwise we just list the questions as bullet points.
        """
        if not stat_questions:
            return "No basic statistics generated."

        lines = []
        if df is not None:
            try:
                lines = _compute_simple_stats(df, table_schema, stat_questions[:15])
            except Exception:
                pass
        if not lines:
            lines = [f"- {q}" for q in stat_questions[:20]]
        return "\n".join(lines)

    def generate(
        self,
        table_schema: TableSchema,
        df: "pd.DataFrame | None" = None,
    ) -> str:
        """
        Full flow: generate stat questions, then produce NL stats string for QUGEN prompt.
        """
        questions = self.generate_stat_questions(table_schema)
        return self.stats_to_natural_language(questions, table_schema, df)


def _compute_simple_stats(
    df: "pd.DataFrame",
    schema: TableSchema,
    stat_questions: list[str],
) -> list[str]:
    """
    Compute simple stats from dataframe to produce NL lines (e.g. " - Two payment methods").
    Does not run full text2sql; uses column names and simple heuristics.
    """
    import pandas as pd
    lines = []
    col_names = [c.get("name") for c in schema.columns if c.get("name") in df.columns]
    for col in col_names:
        if col not in df.columns:
            continue
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            lines.append(f"- Column {col}: min={s.min():.2f}, max={s.max():.2f}, mean={s.mean():.2f}")
        else:
            n_unique = s.nunique()
            lines.append(f"- Column {col}: {n_unique} unique values")
    return lines[:25]
