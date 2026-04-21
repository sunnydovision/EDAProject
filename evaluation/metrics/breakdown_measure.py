"""
Breakdown-Measure (BM) Quality Metrics.

Two complementary metrics for evaluating the quality of (Breakdown, Measure) pairs
chosen by an insight generation system:

1. NMI — Normalized Mutual Information
   Measures how much information B and M share.
   Not biased by the number of categories in B.
   Reference: Cover & Thomas (2006) "Elements of Information Theory", 2nd ed.

2. Interestingness — Coverage × Effect Size
   Standard Subgroup Discovery interestingness measure.
   Coverage: fraction of data covered by a non-trivial breakdown.
   Effect size: Cohen's d (for 2-group B) or η² (for k-group B), normalised to [0,1].
   Reference: Atzmueller (2015) "Subgroup Discovery", ACM CSUR 42(1).

NMI and Interestingness are restricted to categorical-B pairs to avoid numeric-vs-
numeric tautologies (e.g. Operating Profit as B explaining Total Sales as M).

3. BM Actionability — % pairs with categorical B
   In EDA/Subgroup Discovery, breakdown must be a categorical descriptor to produce
   actionable insights. Using a numeric column as B yields trivially high effect sizes.
   Reference: Fayyad et al. (1996) "From Data Mining to Knowledge Discovery",
              AI Magazine 17(3); Lavrac et al. (1999) Subgroup Discovery.

4. BM Diversity — unique (B, M) pairs / total insights
   Measures breadth: how much of the insight budget explores distinct breakdowns
   and measures rather than repeating the same pair.

COUNT(*) pairs are excluded throughout.
"""

import json
import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import re


# ─── helpers ────────────────────────────────────────────────────────────────

# data_type_class values from profile.json that are valid EDA breakdown descriptors
_VALID_BREAKDOWN_CLASSES = {'Categorical', 'Temporal', 'ID'}

# Default profile path relative to this file (can be overridden via compute_bm_quality)
_DEFAULT_PROFILE_PATH = os.path.join(
    os.path.dirname(__file__),
    '../../baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json'
)


def _load_column_classes(profile_path: str) -> Dict[str, str]:
    """
    Load column → data_type_class mapping from a profile.json produced by the
    baseline LLM profiling step.
    Returns empty dict if the file is missing or malformed.
    """
    try:
        with open(profile_path, encoding='utf-8') as f:
            profile = json.load(f)
        return {
            col: meta.get('data_type_class', '')
            for col, meta in profile.get('columns', {}).items()
        }
    except Exception:
        return {}


def _is_categorical(series: pd.Series,
                    col_name: str = '',
                    col_classes: Dict[str, str] = None) -> bool:
    """
    A column is a valid EDA breakdown (descriptor) if its data_type_class in
    profile.json is Categorical, Temporal, or ID.
    Falls back to dtype heuristic when no profile is available.
    """
    if col_classes:
        cls = col_classes.get(col_name, '')
        if cls:
            return cls in _VALID_BREAKDOWN_CLASSES
    # fallback: string/object dtype only
    return series.dtype == object or str(series.dtype) == 'string'


def _parse_measure(measure_str: str) -> Tuple[str, str]:
    """Parse 'AGG(col)' → (agg_lower, col). Returns ('mean', measure_str) on failure."""
    m = re.match(r'(\w+)\((.+)\)', measure_str.strip(), re.IGNORECASE)
    if m:
        return m.group(1).lower(), m.group(2).strip()
    return 'mean', measure_str.strip()


def _resolve_col(name: str, df: pd.DataFrame) -> Optional[str]:
    """Case-insensitive column name resolution."""
    if name in df.columns:
        return name
    name_lower = name.lower()
    for col in df.columns:
        if col.lower() == name_lower:
            return col
    return None


def _numeric_values(df: pd.DataFrame, col: str) -> pd.Series:
    """Return numeric Series for col, dropping NaN."""
    return pd.to_numeric(df[col], errors='coerce').dropna()


# ─── NMI ────────────────────────────────────────────────────────────────────

def _auto_bins(n: int) -> int:
    """Number of histogram bins using sqrt rule (minimum 10)."""
    return max(10, int(np.sqrt(n)))


def _entropy(series: pd.Series, n_bins: int = None) -> float:
    """Differential entropy of a numeric series via equal-width binning."""
    if len(series) < 2:
        return 0.0
    bins = n_bins if n_bins is not None else _auto_bins(len(series))
    counts, _ = np.histogram(series, bins=bins)
    counts = counts[counts > 0]
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log2(probs + 1e-12)))


def _conditional_entropy(y: pd.Series, b: pd.Series, n_bins: int = None) -> float:
    """H(M|B) via weighted per-group entropy."""
    n = len(y)
    # Use global bin edges so all groups are on the same scale
    global_bins = n_bins if n_bins is not None else _auto_bins(n)
    bin_edges = np.histogram_bin_edges(y, bins=global_bins)
    h_cond = 0.0
    for group_val in b.unique():
        group_y = y[b == group_val]
        if len(group_y) < 1:
            continue
        weight = len(group_y) / n
        counts, _ = np.histogram(group_y, bins=bin_edges)
        counts = counts[counts > 0]
        if counts.sum() == 0:
            continue
        probs = counts / counts.sum()
        h_cond += weight * float(-np.sum(probs * np.log2(probs + 1e-12)))
    return h_cond


def compute_nmi_pair(df: pd.DataFrame, breakdown: str, col: str) -> Optional[float]:
    """
    Compute Normalized Mutual Information for one (B, M) pair.

    NMI(B; M) = MI(B; M) / sqrt(H(B) * H(M))
    MI(B; M)  = H(M) - H(M|B)
    H(B)      = entropy of the breakdown column (categorical)

    Bins are set automatically via sqrt(n) rule to avoid under/over-smoothing.

    Returns NMI ∈ [0, 1], or None on failure.
    """
    y = _numeric_values(df, col)
    if len(y) < 2:
        return None

    b = df[breakdown].loc[y.index].astype(str)
    if b.nunique() < 2:
        return None

    n_bins = _auto_bins(len(y))
    h_m = _entropy(y, n_bins)
    if h_m == 0:
        return None

    h_m_given_b = _conditional_entropy(y, b, n_bins)
    mi = max(h_m - h_m_given_b, 0.0)

    # H(B) — categorical entropy
    b_counts = b.value_counts(normalize=True)
    h_b = float(-np.sum(b_counts * np.log2(b_counts + 1e-12)))

    denom = np.sqrt(h_b * h_m)
    if denom == 0:
        return None

    nmi = mi / denom
    return float(min(max(nmi, 0.0), 1.0))


# ─── Interestingness = Coverage × Effect Size ───────────────────────────────

def _cohens_d(g1: np.ndarray, g2: np.ndarray) -> float:
    """Cohen's d for two groups, mapped to [0,1] via d/(d+1)."""
    n1, n2 = len(g1), len(g2)
    if n1 < 2 or n2 < 2:
        return 0.0
    pooled_std = np.sqrt(((n1 - 1) * g1.std(ddof=1) ** 2 +
                          (n2 - 1) * g2.std(ddof=1) ** 2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    d = abs(g1.mean() - g2.mean()) / pooled_std
    return float(d / (d + 1))  # map [0, ∞) → [0, 1)


def _eta_squared(y: pd.Series, b: pd.Series) -> float:
    """η² = SS_between / SS_total for k groups."""
    grand_mean = y.mean()
    ss_total = float(((y - grand_mean) ** 2).sum())
    if ss_total == 0:
        return 0.0
    group_means = y.groupby(b).mean()
    group_counts = y.groupby(b).count()
    ss_between = float((group_counts * (group_means - grand_mean) ** 2).sum())
    return min(max(ss_between / ss_total, 0.0), 1.0)


def compute_interestingness_pair(df: pd.DataFrame, breakdown: str,
                                 col: str) -> Optional[float]:
    """
    Compute Interestingness = Coverage × Effect_Size for one (B, M) pair.

    Coverage   = fraction of rows where breakdown is non-null/non-trivial
    Effect_Size = Cohen's d (2 groups) or η² (k > 2 groups), both in [0,1]

    Returns Interestingness ∈ [0, 1], or None on failure.
    """
    y = _numeric_values(df, col)
    if len(y) < 2:
        return None

    b = df[breakdown].loc[y.index].astype(str)
    k = b.nunique()
    if k < 2:
        return None

    # Coverage: non-null breakdown rows / total rows
    coverage = len(y) / len(df)

    # Effect size
    if k == 2:
        groups = [y[b == v].values for v in b.unique()]
        effect_size = _cohens_d(groups[0], groups[1])
    else:
        effect_size = _eta_squared(y, b)

    return float(coverage * effect_size)


# ─── per-system aggregation ──────────────────────────────────────────────────

def compute_bm_quality(
    insights: List[Dict],
    df_cleaned: pd.DataFrame,
    profile_path: str = _DEFAULT_PROFILE_PATH,
) -> Dict[str, Any]:
    """
    Compute BM Quality metrics for a list of insights.

    Per unique (B, M) pair (COUNT excluded):
      - categorical_b    : whether B is a valid categorical breakdown
      - NMI(B, M)        : only for categorical-B pairs
      - Interestingness  : Coverage x Effect_Size, only for categorical-B pairs

    Aggregate:
      - nmi_mean         : mean NMI over categorical-B pairs
      - int_mean         : mean Interestingness over categorical-B pairs
      - actionability    : fraction of pairs with categorical B  [0,1]
      - bm_diversity     : unique (B,M) pairs / total insights   [0,1]
      - total_evaluated  : unique (B,M) pairs attempted
      - total_categorical: pairs with categorical B
      - total_insights   : total insights passed in

    Args:
        insights   : list of insight dicts
        df_cleaned : cleaned dataframe
    """
    col_classes = _load_column_classes(profile_path)
    total_insights = len(insights)
    empty: Dict[str, Any] = {
        'nmi_mean': 0.0,
        'int_mean': 0.0,
        'actionability': 0.0,
        'bm_diversity': 0.0,
        'total_evaluated': 0,
        'total_categorical': 0,
        'total_insights': total_insights,
        'pairs': [],
    }
    if not insights:
        return empty

    seen: set = set()
    pairs: List[Dict] = []
    total_evaluated = 0

    for ins in insights:
        idata = ins.get('insight', ins)
        breakdown = idata.get('breakdown', '')
        measure = idata.get('measure', '')
        if not breakdown or not measure:
            continue

        agg, col = _parse_measure(measure)

        if agg == 'count' or col == '*':
            continue

        col_r = _resolve_col(col, df_cleaned)
        b_r = _resolve_col(breakdown, df_cleaned)
        if col_r is None or b_r is None:
            continue

        key = (b_r, col_r, agg)
        if key in seen:
            continue
        seen.add(key)
        total_evaluated += 1

        cat_b = _is_categorical(df_cleaned[b_r], b_r, col_classes)

        if cat_b:
            nmi = compute_nmi_pair(df_cleaned, b_r, col_r)
            interestingness = compute_interestingness_pair(df_cleaned, b_r, col_r)
        else:
            nmi = None
            interestingness = None

        pairs.append({
            'breakdown': b_r,
            'col': col_r,
            'agg': agg,
            'categorical_b': cat_b,
            'nmi': round(nmi, 4) if nmi is not None else None,
            'interestingness': round(interestingness, 4) if interestingness is not None else None,
        })

    if not pairs:
        return {**empty, 'total_evaluated': total_evaluated}

    cat_pairs = [p for p in pairs if p['categorical_b']]
    nmi_vals  = [p['nmi'] for p in cat_pairs if p['nmi'] is not None]
    int_vals  = [p['interestingness'] for p in cat_pairs if p['interestingness'] is not None]

    actionability = len(cat_pairs) / len(pairs) if pairs else 0.0
    bm_diversity  = len(pairs) / total_insights if total_insights > 0 else 0.0

    return {
        'nmi_mean':          round(float(np.mean(nmi_vals)), 4) if nmi_vals else 0.0,
        'int_mean':          round(float(np.mean(int_vals)), 4) if int_vals else 0.0,
        'actionability':     round(actionability, 4),
        'bm_diversity':      round(bm_diversity, 4),
        'total_evaluated':   total_evaluated,
        'total_categorical': len(cat_pairs),
        'total_insights':    total_insights,
        'pairs':             pairs,
    }
