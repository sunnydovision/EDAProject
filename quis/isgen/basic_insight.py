"""
Basic insight (paper 3.2.1): view(D, B, M), evaluate applicable patterns, return Insight(B, M, φ, P) if score > T.
"""

from __future__ import annotations

from .models import Insight, Subspace, TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE
from .views import compute_view, parse_measure
from .scoring import score_view, get_threshold


def _applicable_patterns(breakdown: str, measure_str: str, df) -> list[str]:
    """Determine which patterns apply: Trend for ordinal/numeric B; OV, Attr for any; DD only for COUNT."""
    agg_name, measure_col = parse_measure(measure_str)
    patterns = [OUTSTANDING_VALUE, ATTRIBUTION]
    if breakdown in df.columns:
        ser = df[breakdown]
        if ser.dtype.kind in ("i", "u", "f") or (ser.nunique() > 2 and ser.dtype.name == "object"):
            patterns.append(TREND)
    if agg_name == "count":
        patterns.append(DISTRIBUTION_DIFFERENCE)
    return patterns


def extract_basic_insights(df, card: dict, max_per_card: int = 2) -> list[Insight]:
    """
    For one Insight Card (breakdown, measure), compute view(D, B, M), score each applicable pattern,
    return list of Insight(B, M, φ, P) with score above threshold.
    Thu thập tối đa 1 insight per pattern (để Trend/DD không bị OV–Attr chèn), rồi lấy top max_per_card theo score.
    """
    breakdown = card.get("breakdown", "").strip()
    measure = card.get("measure", "").strip()
    if not breakdown or not measure:
        return []
    labels, values = compute_view(df, breakdown, measure, Subspace.empty())
    if len(values) < 2:
        return []

    patterns = _applicable_patterns(breakdown, measure, df)
    best_per_pattern: dict[str, Insight] = {}
    for p in patterns:
        if p == DISTRIBUTION_DIFFERENCE:
            continue  # DD cần hai view (full vs subspace), xử lý ở subspace
        score = score_view(p, values)
        if score >= get_threshold(p):
            ins = Insight(
                breakdown=breakdown,
                measure=measure,
                subspace=Subspace.empty(),
                pattern=p,
                score=score,
                view_values=values,
                view_labels=labels,
                question=card.get("question", ""),
                reason=card.get("reason", ""),
            )
            if p not in best_per_pattern or ins.score > best_per_pattern[p].score:
                best_per_pattern[p] = ins
    out = sorted(best_per_pattern.values(), key=lambda i: -i.score)
    return out[:max_per_card]
