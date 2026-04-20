"""
Basic insight (paper 3.2.1): view(D, B, M), evaluate applicable patterns, return Insight(B, M, φ, P) if score > T.
"""

from __future__ import annotations

from .models import Insight, Subspace, TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE
from .views import compute_view, parse_measure
from .scoring import score_view, get_threshold_scaled


_TEMPORAL_KEYWORDS = {
    "tháng", "thang", "quý", "quy", "tuần", "tuan", "năm", "nam",
    "ngày", "ngay", "month", "quarter", "week", "year", "date",
    "period", "time", "day", "tuần_trong_tháng",
}


def _is_temporal_column(col_name: str, ser) -> bool:
    """Check if a column represents a temporal/ordinal dimension suitable for Trend."""
    import pandas as pd

    if pd.api.types.is_datetime64_any_dtype(ser):
        return True
    name_lower = col_name.lower().replace(" ", "_")
    tokens = set(name_lower.split("_"))
    if tokens & _TEMPORAL_KEYWORDS:
        return True
    if any(kw in name_lower for kw in _TEMPORAL_KEYWORDS):
        return True
    return False


def _applicable_patterns(breakdown: str, measure_str: str, df) -> list[str]:
    """Determine which patterns apply: Trend only for temporal B; OV, Attr, DD for any."""
    patterns = [OUTSTANDING_VALUE, ATTRIBUTION]
    if breakdown in df.columns:
        ser = df[breakdown]
        if _is_temporal_column(breakdown, ser):
            patterns.append(TREND)
    patterns.append(DISTRIBUTION_DIFFERENCE)
    return patterns


def extract_basic_insights(df, card: dict, max_per_card: int = 2, threshold_scale: float = 1.0) -> list[Insight]:
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
        if score >= get_threshold_scaled(p, threshold_scale=threshold_scale):
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
