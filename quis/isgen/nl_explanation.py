"""
Natural language explanation for each insight (paper 3.2.3): template per pattern.
"""

from __future__ import annotations

from .models import Insight, TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE


def explain_insight(insight: Insight) -> str:
    """Generate short NL description from template + insight data."""
    B, M, S, P = insight.breakdown, insight.measure, insight.subspace, insight.pattern
    filters_desc = ", ".join(f"{c}={v}" for c, v in insight.subspace.filters) if insight.subspace.filters else "overall data"
    if P == TREND:
        return f"There is a notable trend in {M} across {B}. For the segment {filters_desc}, the values show a monotonic trend."
    if P == OUTSTANDING_VALUE:
        return f"Outstanding value: for {filters_desc}, one category in {B} has a value much larger (or smaller) than the others when measuring {M}."
    if P == ATTRIBUTION:
        return f"Attribution: for {filters_desc}, a single category in {B} accounts for a large share of total {M}."
    if P == DISTRIBUTION_DIFFERENCE:
        return f"Distribution difference: the distribution of {B} changes notably when filtering by {filters_desc} (compared to overall data)."
    return f"Insight type: {P}. Breakdown: {B}, Measure: {M}, Subspace: {filters_desc}."
