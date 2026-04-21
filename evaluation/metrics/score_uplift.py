"""
Score uplift metrics for subspace insights.

This metric quantifies whether insights that use subspace filters tend to have
higher internal insight score than insights without subspace filters.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _extract_score(insight_item: Dict[str, Any]) -> float | None:
    insight = insight_item.get("insight", insight_item)
    raw = insight.get("score")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _has_subspace(insight_item: Dict[str, Any]) -> bool:
    insight = insight_item.get("insight", insight_item)
    return bool(insight.get("subspace"))


def _uplift_direction(delta: float | None, eps: float = 1e-9) -> str | None:
    if delta is None:
        return None
    if delta > eps:
        return "up"
    if delta < -eps:
        return "down"
    return "flat"


def compute_score_uplift_from_subspace(insights: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute score uplift from using subspace.

    uplift_abs   = mean(score | subspace != []) - mean(score | subspace == [])
    uplift_ratio = mean(score | subspace != []) / mean(score | subspace == [])
    """
    with_subspace_scores: list[float] = []
    without_subspace_scores: list[float] = []

    for ins in insights:
        score = _extract_score(ins)
        if score is None:
            continue
        if _has_subspace(ins):
            with_subspace_scores.append(score)
        else:
            without_subspace_scores.append(score)

    mean_with = (
        sum(with_subspace_scores) / len(with_subspace_scores)
        if with_subspace_scores
        else None
    )
    mean_without = (
        sum(without_subspace_scores) / len(without_subspace_scores)
        if without_subspace_scores
        else None
    )

    uplift_abs = None
    uplift_ratio = None
    if mean_with is not None and mean_without is not None:
        uplift_abs = mean_with - mean_without
        if mean_without != 0:
            uplift_ratio = mean_with / mean_without

    direction = _uplift_direction(uplift_abs)

    return {
        "num_with_subspace_scored": len(with_subspace_scores),
        "num_without_subspace_scored": len(without_subspace_scores),
        "mean_score_with_subspace": mean_with,
        "mean_score_without_subspace": mean_without,
        "score_uplift_abs": uplift_abs,
        "score_uplift_ratio": uplift_ratio,
        "score_uplift_direction": direction,
    }

