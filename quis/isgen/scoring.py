"""
Scoring functions and thresholds for ISGEN (paper Appendix A).
view = (labels, values) or list of values; we use values for scoring.
"""

from __future__ import annotations

from .models import TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE

# Thresholds (Appendix A). T_TREND 0.90 = p < 0.10 để Trend dễ xuất hiện hơn
T_TREND = 0.90
T_OV = 1.4
T_ATTR = 0.5
T_DD = 0.2


def score_trend(values: list[float]) -> float:
    """SCOREFUNC_Trend(v) = 1 - p_value(Mann-Kendall). Dùng original_test (pymannkendall >= 1.4)."""
    if len(values) < 3:
        return 0.0
    try:
        import pymannkendall as mk
        result = mk.original_test(values)
        p = result.p
        return 1.0 - float(p) if p is not None else 0.0
    except ImportError:
        # Fallback: Spearman rank correlation nếu không có pymannkendall
        try:
            from scipy.stats import spearmanr
            rho, p = spearmanr(range(len(values)), values)
            return 1.0 - float(p) if p is not None else 0.0
        except Exception:
            return 0.0
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


def score_dd_for_subspace(df, breakdown: str, measure: str, subspace) -> float:
    """
    JSD giữa view(D, B, M) và view(D_S, B, M). Dùng cho subspace search khi pattern = Distribution Difference.
    Cần align theo label (union) rồi gọi score_distribution_difference.
    """
    from .views import compute_view
    from .models import Subspace
    S_empty = Subspace.empty()
    labels_full, values_full = compute_view(df, breakdown, measure, S_empty)
    labels_S, values_S = compute_view(df, breakdown, measure, subspace)
    if len(values_full) < 2 or len(values_S) < 2:
        return 0.0
    d_full = dict(zip(labels_full, values_full))
    d_S = dict(zip(labels_S, values_S))
    all_labels = sorted(set(d_full) | set(d_S))
    v_initial = [float(d_full.get(l, 0)) for l in all_labels]
    v_final = [float(d_S.get(l, 0)) for l in all_labels]
    return score_distribution_difference(v_initial, v_final)
