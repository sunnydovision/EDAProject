"""
Score uplift metrics for subspace insights.

This metric quantifies whether insights that use subspace filters tend to have
higher effect-size score than insights without subspace filters.

Score used = effect-size per insight, computed by significance.compute_insight_score().
Effect-size is independent of sample size and does NOT saturate on large datasets,
unlike (1 - p_value) which approaches 1.0 for all insights with n > ~1000.

  OUTSTANDING_VALUE  : score = z / (z+1)     where z = (max-μ)/σ    ∈ [0, 1)
  TREND              : score = |Kendall τ|                            ∈ [0, 1]
  ATTRIBUTION        : score = Cramér's V                             ∈ [0, 1]
  DISTRIBUTION_DIFF  : score = KS statistic                          ∈ [0, 1]

  uplift_abs   = mean(score | subspace != []) - mean(score | subspace == [])
  uplift_ratio = mean(score | subspace != []) / mean(score | subspace == [])
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd

from .significance import compute_insight_score, resolve_column, parse_measure


def _has_subspace(insight_item: Dict[str, Any]) -> bool:
    insight = insight_item.get("insight", insight_item)
    return bool(insight.get("subspace"))


def _effect_size_score(insight_item: Dict[str, Any], df: pd.DataFrame, profile_path: str = None) -> Optional[float]:
    """
    Compute per-insight effect-size score via significance.compute_insight_score().
    Returns None if the insight cannot be evaluated (missing columns, wrong pattern, etc.)
    """
    insight = insight_item.get("insight", insight_item)
    pattern = insight.get("pattern", "")
    measure = insight.get("measure", "")
    breakdown = insight.get("breakdown", "")

    parsed = parse_measure(measure)
    if parsed is None:
        return None  # Unknown aggregation type
    agg, col = parsed
    if not col or col == "*":
        col = breakdown if breakdown and breakdown in df.columns else None
    if not col:
        return None

    col_r = resolve_column(col, list(df.columns))
    b_r = resolve_column(breakdown, list(df.columns)) if breakdown else None

    if not col_r or col_r not in df.columns:
        return None
    if b_r and b_r not in df.columns:
        return None

    result = compute_insight_score(pattern, df, b_r, col_r, agg, profile_path=profile_path)
    return result.get("score")  # None if pattern could not be evaluated


def _uplift_direction(delta: float | None, eps: float = 1e-9) -> str | None:
    if delta is None:
        return None
    if delta > eps:
        return "up"
    if delta < -eps:
        return "down"
    return "flat"


def compute_score_uplift_from_subspace(
    insights: List[Dict[str, Any]],
    df_cleaned: pd.DataFrame = None,
    profile_path: str = None,
) -> Dict[str, Any]:
    """
    Compute score uplift from using subspace.

    Score = (1 - p_value) per insight, computed via significance.py.
    Requires df_cleaned to evaluate p-values; returns zeros if not provided.

    uplift_abs   = mean(score | subspace != []) - mean(score | subspace == [])
    uplift_ratio = mean(score | subspace != []) / mean(score | subspace == [])
    """
    empty = {
        "num_with_subspace_scored": 0,
        "num_without_subspace_scored": 0,
        "mean_score_with_subspace": None,
        "mean_score_without_subspace": None,
        "score_uplift_abs": None,
        "score_uplift_ratio": None,
        "score_uplift_direction": None,
    }

    if df_cleaned is None or len(insights) == 0:
        return empty

    with_scores: list[float] = []
    without_scores: list[float] = []

    for ins in insights:
        score = _effect_size_score(ins, df_cleaned, profile_path)
        if score is None:
            continue
        if _has_subspace(ins):
            with_scores.append(score)
        else:
            without_scores.append(score)

    mean_with = sum(with_scores) / len(with_scores) if with_scores else None
    mean_without = sum(without_scores) / len(without_scores) if without_scores else None

    uplift_abs = None
    uplift_ratio = None
    if mean_with is not None and mean_without is not None:
        uplift_abs = mean_with - mean_without
        if mean_without != 0:
            uplift_ratio = mean_with / mean_without

    return {
        "num_with_subspace_scored": len(with_scores),
        "num_without_subspace_scored": len(without_scores),
        "mean_score_with_subspace": round(mean_with, 4) if mean_with is not None else None,
        "mean_score_without_subspace": round(mean_without, 4) if mean_without is not None else None,
        "score_uplift_abs": round(uplift_abs, 4) if uplift_abs is not None else None,
        "score_uplift_ratio": round(uplift_ratio, 4) if uplift_ratio is not None else None,
        "score_uplift_direction": _uplift_direction(uplift_abs),
    }

