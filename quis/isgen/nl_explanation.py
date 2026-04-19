"""
Natural language explanation for each insight (paper 3.2.3): template per pattern.
"""

from __future__ import annotations

from .models import Insight, TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE


def explain_insight(insight: Insight, language: str = "en") -> str:
    """Generate short NL description from template + insight data."""
    lang = (language or "en").strip().lower()
    use_vi = lang.startswith("vi")
    B, M, S, P = insight.breakdown, insight.measure, insight.subspace, insight.pattern
    if insight.subspace.filters:
        filters_desc = ", ".join(f"{c}={v}" for c, v in insight.subspace.filters)
    else:
        filters_desc = "toàn bộ dữ liệu" if use_vi else "overall data"
    if P == TREND:
        if use_vi:
            return (
                f"Có xu hướng rõ ở {M} theo {B}. Với phân khúc {filters_desc}, các giá trị biến đổi theo một chiều (tăng hoặc giảm liên tục)."
            )
        return f"There is a notable trend in {M} across {B}. For the segment {filters_desc}, the values show a monotonic trend."
    if P == OUTSTANDING_VALUE:
        if use_vi:
            return (
                f"Giá trị nổi bật: với {filters_desc}, một nhóm trong {B} có giá trị {M} lớn hơn hoặc nhỏ hơn hẳn so với các nhóm còn lại."
            )
        return f"Outstanding value: for {filters_desc}, one category in {B} has a value much larger (or smaller) than the others when measuring {M}."
    if P == ATTRIBUTION:
        if use_vi:
            return f"Đóng góp: với {filters_desc}, một nhóm trong {B} chiếm phần lớn tổng {M}."
        return f"Attribution: for {filters_desc}, a single category in {B} accounts for a large share of total {M}."
    if P == DISTRIBUTION_DIFFERENCE:
        if use_vi:
            return (
                f"Khác biệt phân phối: phân bố của {B} thay đổi rõ khi lọc theo {filters_desc} (so với toàn bộ dữ liệu)."
            )
        return f"Distribution difference: the distribution of {B} changes notably when filtering by {filters_desc} (compared to overall data)."
    if use_vi:
        return f"Loại insight: {P}. Chiều phân tích: {B}, Đo lường: {M}, Phân khúc: {filters_desc}."
    return f"Insight type: {P}. Breakdown: {B}, Measure: {M}, Subspace: {filters_desc}."
