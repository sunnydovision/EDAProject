"""
Scoring functions and thresholds for ISGEN (paper Appendix A).
view = (labels, values) or list of values; we use values for scoring.
"""

from __future__ import annotations

from .models import TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE

# Thresholds (Appendix A)
T_TREND = 0.95
T_OV = 1.4
T_ATTR = 0.5
T_DD = 0.2


def score_trend(values: list[float]) -> float:
    """SCOREFUNC_Trend(v) = 1 - p_value(Mann-Kendall). Only views with p < 0.05 pass T_Trend."""
    if len(values) < 3:
        return 0.0
    try:
        import pymannkendall as mk
        result = mk.test(values)
        p = result.p
        return 1.0 - p if p is not None else 0.0
    except Exception:
        return 0.0


def score_outstanding_value(values: list[float]) -> float:
    """SCOREFUNC_OV = vmax1 / vmax2 (two largest absolute values)."""
    if len(values) < 2:
        return 0.0
    abs_vals = sorted([abs(v) for v in values if v != 0], reverse=True)
    if len(abs_vals) < 2:
        return 0.0
    if abs_vals[1] == 0:
        return float(abs_vals[0]) if abs_vals[0] > 0 else 0.0
    return abs_vals[0] / abs_vals[1]


def score_attribution(values: list[float]) -> float:
    """SCOREFUNC_Attr = max(v) / sum(v)."""
    if not values:
        return 0.0
    s = sum(values)
    if s == 0:
        return 0.0
    return max(values) / s


def score_distribution_difference(values_initial: list[float], values_final: list[float]) -> float:
    """Jensen-Shannon divergence between normalized distributions (paper Appendix A)."""
    import numpy as np
    def norm(v):
        v = np.array(v, dtype=float)
        s = v.sum()
        return v / s if s > 0 else v
    p = norm(values_initial)
    q = norm(values_final)
    # Align length (pad with 0); JSD typically for same support
    if len(p) != len(q):
        n = max(len(p), len(q))
        pp = np.zeros(n)
        qq = np.zeros(n)
        pp[:len(p)] = p
        qq[:len(q)] = q
        p, q = pp, qq
    try:
        from scipy.spatial.distance import jensenshannon
        return float(jensenshannon(p, q))
    except ImportError:
        m = (p + q) / 2
        eps = 1e-12
        jsd = 0.5 * (np.sum(p * np.log(p + eps)) + np.sum(q * np.log(q + eps))) - np.sum(m * np.log(m + eps))
        return float(max(0, jsd))


def get_threshold(pattern: str) -> float:
    if pattern == TREND:
        return T_TREND
    if pattern == OUTSTANDING_VALUE:
        return T_OV
    if pattern == ATTRIBUTION:
        return T_ATTR
    if pattern == DISTRIBUTION_DIFFERENCE:
        return T_DD
    return 0.0


def score_view(pattern: str, values: list[float], values_initial: list[float] | None = None) -> float:
    """Return score for a view given pattern. For DD, pass both initial and final view values."""
    if pattern == TREND:
        return score_trend(values)
    if pattern == OUTSTANDING_VALUE:
        return score_outstanding_value(values)
    if pattern == ATTRIBUTION:
        return score_attribution(values)
    if pattern == DISTRIBUTION_DIFFERENCE and values_initial is not None:
        return score_distribution_difference(values_initial, values)
    return 0.0
