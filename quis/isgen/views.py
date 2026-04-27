"""
Compute view(D, B, M) and apply subspace S (paper Section 2).
Parse measure string: SUM(Col), MEAN(Col), COUNT(*), etc.
"""

from __future__ import annotations

import re
from typing import Any

from .models import Subspace


def resolve_column(name: str, df_columns: list[str]) -> str | None:
    """
    Map column name from Insight Card to actual DataFrame column.
    Card may use spaces (e.g. 'Tổng doanh thu sản phẩm') while CSV uses underscores ('Tổng_doanh_thu_sản_phẩm').
    Tries: exact → normalized (spaces to _) → case-insensitive → partial → best token overlap.
    """
    if not name or not df_columns:
        return None
    cols = list(df_columns)
    if name in cols:
        return name
    normalized = name.replace(" ", "_")
    if normalized in cols:
        return normalized
    name_lower = name.lower()
    for c in cols:
        if c.replace(" ", "_") == normalized or c.lower() == name_lower:
            return c
    for c in cols:
        c_norm = c.replace(" ", "_")
        if name in c or c in name or normalized in c or c_norm in normalized:
            return c
    # Token overlap: "Tổng doanh thu sản phẩm" vs "Tổng_doanh_thu_sản_phẩm" (tokens match when normalized)
    name_tokens = set(normalized.lower().split("_"))
    best_col, best_score = None, 0
    for c in cols:
        col_tokens = set(c.replace(" ", "_").lower().split("_"))
        overlap = len(name_tokens & col_tokens) / max(len(name_tokens), 1)
        if overlap >= 0.33 and overlap > best_score:
            best_score = overlap
            best_col = c
    return best_col


def parse_measure(measure_str: str) -> tuple[str, str]:
    """
    Parse measure string into (agg, column).
    Examples: "SUM(Col)" -> ("sum", "Col"), "MEAN(X)" -> ("mean", "X"), "COUNT(*)" -> ("count", "*").
    Returns (agg_lower, column_name).
    """
    s = measure_str.strip()
    m = re.match(r"(SUM|MEAN|AVG|COUNT|MIN|MAX)\s*\(\s*([^)]+)\s*\)", s, re.IGNORECASE)
    if m:
        return m.group(1).lower(), m.group(2).strip()
    if re.match(r"COUNT\s*\(\s*\*\s*\)", s, re.IGNORECASE):
        return "count", "*"
    return "mean", s


def apply_subspace(df, subspace: Subspace):
    """Return DataFrame filtered by subspace (all conditions AND)."""
    if not subspace.filters:
        return df
    out = df
    for col, val in subspace.filters:
        if col in out.columns:
            out = out[out[col].astype(str) == str(val)]
    return out


def compute_view(df, breakdown: str, measure_str: str, subspace: Subspace | None = None):
    """
    Compute view(D_S, B, M): filter by subspace then group by B and apply measure.
    Resolves breakdown/measure column names to actual df columns if needed (card vs CSV naming).
    Returns (labels: index/breakdown values, values: aggregate values).
    """
    import pandas as pd
    agg_name, measure_col = parse_measure(measure_str)
    if subspace:
        df = apply_subspace(df, subspace)
    if df.empty:
        return [], []

    breakdown_resolved = resolve_column(breakdown, list(df.columns)) or breakdown
    if breakdown_resolved not in df.columns:
        return [], []

    def _agg_numeric_safe(frame, bcol: str, mcol: str, how: str):
        """Coerce measure to numeric before mean/sum/min/max so object dates/strings don't break groupby."""
        import pandas as pd

        h = how
        if h == "avg":
            h = "mean"
        if h in ("mean", "sum", "min", "max", "median", "std"):
            work = frame[[bcol, mcol]].copy()
            work[mcol] = pd.to_numeric(work[mcol], errors="coerce")
            return work.groupby(bcol)[mcol].agg(h)
        return frame.groupby(bcol)[mcol].agg(h)

    if measure_col == "*" or agg_name == "count":
        if measure_col != "*":
            measure_resolved = resolve_column(measure_col, list(df.columns)) or measure_col
            if measure_resolved in df.columns:
                ser = _agg_numeric_safe(df, breakdown_resolved, measure_resolved, agg_name)
            else:
                ser = df.groupby(breakdown_resolved).size()
        else:
            ser = df.groupby(breakdown_resolved).size()
    else:
        measure_resolved = resolve_column(measure_col, list(df.columns)) or measure_col
        if measure_resolved not in df.columns:
            return [], []
        ser = _agg_numeric_safe(df, breakdown_resolved, measure_resolved, agg_name)

    ser = ser.dropna()
    # Aggregates may be non-numeric if measure targeted date/text (e.g. MEAN on Invoice Date as string).
    v = pd.to_numeric(ser, errors="coerce")
    valid = v.notna()
    if not valid.any():
        return [], []
    v = v[valid]
    # Convert datetime index to YYYY-MM-DD string format to match evaluation format
    if pd.api.types.is_datetime64_any_dtype(ser.index):
        labels = [str(x.date()) for x in ser.index.tolist()]
    else:
        labels = [str(x) for x in v.index.tolist()]
    values = v.astype(float).tolist()
    return labels, values


def resolve_card_columns(card: dict, df_columns: list[str]) -> dict | None:
    """
    Return card with breakdown and measure resolved to actual df column names, or None if cannot resolve.
    Modifies measure string so the column inside SUM(...)/MEAN(...) is resolved.
    """
    import re
    breakdown = (card.get("breakdown") or "").strip()
    measure = (card.get("measure") or "").strip()
    if not breakdown or not measure:
        return None
    b_resolved = resolve_column(breakdown, df_columns)
    if not b_resolved:
        return None
    agg_name, measure_col = parse_measure(measure)
    if measure_col == "*":
        m_resolved_str = measure
    else:
        m_resolved = resolve_column(measure_col, df_columns)
        if not m_resolved:
            return None
        m_resolved_str = re.sub(r"\(\s*[^)]+\s*\)", f"({m_resolved})", measure, count=1)
    return {
        **card,
        "breakdown": b_resolved,
        "measure": m_resolved_str,
    }
