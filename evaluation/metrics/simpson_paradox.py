"""
Simpson's Paradox Detection Metric.

Detects when the direction of an association or trend reverses between the global
dataset and a subspace (filtered subset). This is a formalization of Simpson's
Paradox (Simpson, 1951) for automated EDA evaluation.

Simpson's Paradox occurs when:
- A trend or association observed in the aggregate data reverses direction
  when the data is partitioned into subgroups.

Examples:
  TREND: Global sales increase over time (τ > 0), but decrease in Region=West (τ < 0)
  ATTRIBUTION: Product A dominates globally, but Product B dominates in Region=East
  CORRELATION: Price positively correlates with sales globally, but negatively in a segment

References:
  Simpson, E. H. (1951). The Interpretation of Interaction in Contingency Tables.
    Journal of the Royal Statistical Society, Series B, 13(2), 238-241.
  Teng, X. and Lin, Y.-R. (2026). De-paradox Tree: Breaking Down Simpson's Paradox
    via A Kernel-Based Partition Algorithm. arXiv:2603.02174.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from scipy import stats
from scipy.stats import chi2_contingency, ks_2samp

from .significance import parse_measure, resolve_column, compute_insight_score
from .breakdown_measure import _load_column_classes, _is_categorical


def _apply_subspace_filter(df: pd.DataFrame, subspace: list) -> pd.DataFrame:
    """Apply subspace conditions (list of [col, val] pairs) to filter the dataframe."""
    df_f = df.copy()
    for item in subspace:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            col_f, val = item
            if col_f in df_f.columns:
                df_f = df_f[df_f[col_f].astype(str) == str(val)]
    return df_f


def _detect_trend_reversal(
    df_global: pd.DataFrame,
    df_subspace: pd.DataFrame,
    breakdown: str,
    measure_col: str,
) -> Tuple[bool, Optional[float], Optional[float], Optional[float], Optional[float], bool]:
    """
    Detect trend direction reversal between global and subspace.
    
    Uses Mann-Kendall test to measure trend direction (consistent with significance.py).
    Reversal = sign(tau_global) != sign(tau_subspace) and both are non-zero.
    
    Returns:
        (is_reversal, tau_global, tau_subspace, p_global, p_subspace, is_significant)
    """
    try:
        # Convert breakdown to datetime
        x_global = pd.to_datetime(df_global[breakdown], errors='coerce')
        x_subspace = pd.to_datetime(df_subspace[breakdown], errors='coerce')
        
        # Get numeric measure
        y_global = pd.to_numeric(df_global[measure_col], errors='coerce')
        y_subspace = pd.to_numeric(df_subspace[measure_col], errors='coerce')
        
        # Clean data
        mask_global = x_global.notna() & y_global.notna()
        mask_subspace = x_subspace.notna() & y_subspace.notna()
        
        if mask_global.sum() < 3 or mask_subspace.sum() < 3:
            return False, None, None, None, None, False
        
        y_global_clean = y_global[mask_global].values
        y_subspace_clean = y_subspace[mask_subspace].values
        
        # Use Mann-Kendall test (consistent with significance.py)
        try:
            import pymannkendall as mk
            res_global = mk.original_test(y_global_clean)
            res_subspace = mk.original_test(y_subspace_clean)
            
            tau_global = float(res_global.Tau)
            tau_subspace = float(res_subspace.Tau)
            p_global = float(res_global.p)
            p_subspace = float(res_subspace.p)
        except ImportError:
            # Fallback to Kendall's tau if pymannkendall not available
            x_global_num = x_global[mask_global].astype(np.int64) / 10**9
            x_subspace_num = x_subspace[mask_subspace].astype(np.int64) / 10**9
            tau_global, p_global = stats.kendalltau(x_global_num, y_global_clean)
            tau_subspace, p_subspace = stats.kendalltau(x_subspace_num, y_subspace_clean)
        
        # Check for reversal: signs must be opposite and both non-negligible
        eps = 0.05  # Minimum tau magnitude to consider
        if abs(tau_global) < eps or abs(tau_subspace) < eps:
            return False, tau_global, tau_subspace, p_global, p_subspace, False
        
        # Reversal if signs are opposite
        is_reversal = (tau_global > 0) != (tau_subspace > 0)
        
        # Statistical significance: both trends must be significant (p < 0.05)
        alpha = 0.05
        is_significant = (p_global < alpha) and (p_subspace < alpha)
        
        return is_reversal, tau_global, tau_subspace, p_global, p_subspace, is_significant
        
    except Exception:
        return False, None, None, None, None, False


def _detect_attribution_reversal(
    df_global: pd.DataFrame,
    df_subspace: pd.DataFrame,
    breakdown: str,
    measure_col: str,
    agg: str = 'mean',
) -> Tuple[bool, Optional[str], Optional[str], Optional[float], bool]:
    """
    Detect attribution reversal: dominant category changes between global and subspace.
    
    Returns:
        (is_reversal, top_category_global, top_category_subspace, p_value, is_significant)
    """
    try:
        agg_func = (agg or 'mean').lower()
        
        # Compute aggregated values by breakdown category
        if agg_func == 'count':
            global_agg = df_global.groupby(breakdown).size()
            subspace_agg = df_subspace.groupby(breakdown).size()
        elif agg_func == 'sum':
            global_agg = df_global.groupby(breakdown)[measure_col].sum()
            subspace_agg = df_subspace.groupby(breakdown)[measure_col].sum()
        elif agg_func == 'min':
            global_agg = df_global.groupby(breakdown)[measure_col].min()
            subspace_agg = df_subspace.groupby(breakdown)[measure_col].min()
        elif agg_func == 'max':
            global_agg = df_global.groupby(breakdown)[measure_col].max()
            subspace_agg = df_subspace.groupby(breakdown)[measure_col].max()
        else:  # mean
            global_agg = df_global.groupby(breakdown)[measure_col].mean()
            subspace_agg = df_subspace.groupby(breakdown)[measure_col].mean()
        
        if len(global_agg) < 2 or len(subspace_agg) < 2:
            return False, None, None, None, False
        
        # Find top category in each
        top_global = global_agg.idxmax()
        top_subspace = subspace_agg.idxmax()
        
        # Reversal if different top categories
        is_reversal = (top_global != top_subspace)
        
        # Statistical significance: test if distributions are significantly different
        # Use chi-square test or ANOVA depending on data type
        p_value = None
        is_significant = False
        
        try:
            # Get all categories that appear in both global and subspace
            common_categories = set(global_agg.index) & set(subspace_agg.index)
            if len(common_categories) >= 2:
                # Perform one-way ANOVA or Kruskal-Wallis test
                # Compare if the top categories have significantly different values
                top_global_values = df_global[df_global[breakdown] == top_global][measure_col]
                top_subspace_values = df_subspace[df_subspace[breakdown] == top_subspace][measure_col]
                
                top_global_numeric = pd.to_numeric(top_global_values, errors='coerce').dropna()
                top_subspace_numeric = pd.to_numeric(top_subspace_values, errors='coerce').dropna()
                
                if len(top_global_numeric) >= 3 and len(top_subspace_numeric) >= 3:
                    # Use Mann-Whitney U test (non-parametric)
                    _, p_value = stats.mannwhitneyu(top_global_numeric, top_subspace_numeric, alternative='two-sided')
                    is_significant = (p_value < 0.05)
        except Exception:
            pass
        
        return is_reversal, str(top_global), str(top_subspace), p_value, is_significant
        
    except Exception:
        return False, None, None, None, False


def _detect_outstanding_value_reversal(
    df_global: pd.DataFrame,
    df_subspace: pd.DataFrame,
    breakdown: str,
    measure_col: str,
    agg: str = 'mean',
) -> Tuple[bool, Optional[str], Optional[str], Optional[float], bool]:
    """
    Detect outstanding value reversal: the outstanding category changes.
    
    Similar to attribution reversal - finds which category has the most extreme value.
    
    Returns:
        (is_reversal, outstanding_category_global, outstanding_category_subspace, p_value, is_significant)
    """
    # For outstanding value, we use the same logic as attribution
    return _detect_attribution_reversal(df_global, df_subspace, breakdown, measure_col, agg)


def _detect_distribution_reversal(
    df_global: pd.DataFrame,
    df_subspace: pd.DataFrame,
    breakdown: str,
    measure_col: str,
) -> Tuple[bool, Optional[float], Optional[float], Optional[float], bool]:
    """
    Detect distribution difference reversal.
    
    Compares the distribution of measure_col across two groups defined by breakdown.
    Reversal occurs if the relative ordering of groups flips.
    Uses KS test (consistent with significance.py).
    
    Returns:
        (is_reversal, mean_diff_global, mean_diff_subspace, p_value, is_significant)
    """
    try:
        # Get unique breakdown values
        categories = df_global[breakdown].unique()
        if len(categories) != 2:
            # For simplicity, only handle binary breakdown
            return False, None, None, None, False
        
        cat1, cat2 = categories[0], categories[1]
        
        # Global comparison
        global_cat1 = pd.to_numeric(df_global[df_global[breakdown] == cat1][measure_col], errors='coerce').dropna()
        global_cat2 = pd.to_numeric(df_global[df_global[breakdown] == cat2][measure_col], errors='coerce').dropna()
        
        if len(global_cat1) < 2 or len(global_cat2) < 2:
            return False, None, None, None, False
        
        mean_diff_global = global_cat1.mean() - global_cat2.mean()
        
        # Subspace comparison
        subspace_cat1 = pd.to_numeric(df_subspace[df_subspace[breakdown] == cat1][measure_col], errors='coerce').dropna()
        subspace_cat2 = pd.to_numeric(df_subspace[df_subspace[breakdown] == cat2][measure_col], errors='coerce').dropna()
        
        if len(subspace_cat1) < 2 or len(subspace_cat2) < 2:
            return False, None, None, None, False
        
        mean_diff_subspace = subspace_cat1.mean() - subspace_cat2.mean()
        
        # Reversal if signs are opposite
        eps = 1e-6
        if abs(mean_diff_global) < eps or abs(mean_diff_subspace) < eps:
            return False, mean_diff_global, mean_diff_subspace, None, False
        
        is_reversal = (mean_diff_global > 0) != (mean_diff_subspace > 0)
        
        # Statistical significance: use KS test (consistent with significance.py)
        p_value = None
        is_significant = False
        
        try:
            if len(subspace_cat1) >= 3 and len(subspace_cat2) >= 3:
                # Use Kolmogorov-Smirnov test (same as significance.py)
                _, p_value = ks_2samp(subspace_cat1, subspace_cat2)
                is_significant = (p_value < 0.05)
        except Exception:
            pass
        
        return is_reversal, mean_diff_global, mean_diff_subspace, p_value, is_significant
        
    except Exception:
        return False, None, None, None, False


def detect_simpson_paradox_single(
    insight: Dict[str, Any],
    df_cleaned: pd.DataFrame,
    profile_path: str = None,
) -> Dict[str, Any]:
    """
    Detect Simpson's Paradox for a single insight with subspace.
    
    Args:
        insight: Insight dictionary with pattern, breakdown, measure, subspace
        df_cleaned: Full cleaned dataframe
        profile_path: Path to profile.json for column type checking
    
    Returns:
        Dictionary with:
            - is_paradox: bool (True if reversal detected)
            - pattern: str (pattern type)
            - global_metric: float or str (global trend/category)
            - subspace_metric: float or str (subspace trend/category)
            - reversal_type: str (description of reversal)
    """
    result = {
        'is_paradox': bool(False),
        'is_significant': bool(False),
        'pattern': None,
        'global_metric': None,
        'subspace_metric': None,
        'p_value': None,
        'reversal_type': None,
        'subspace_size': 0,
    }
    
    insight_data = insight.get('insight', insight)
    pattern = insight_data.get('pattern', '').upper().replace(' ', '_')
    breakdown = insight_data.get('breakdown', '')
    measure = insight_data.get('measure', '')
    subspace = insight_data.get('subspace', [])
    
    # Only check insights with subspace
    if not subspace or not breakdown or not measure:
        return result
    
    result['pattern'] = pattern
    
    # Parse measure
    parsed = parse_measure(measure)
    if parsed is None:
        return result
    
    agg, col = parsed
    if not col or col == '*':
        col = breakdown if breakdown in df_cleaned.columns else None
    if not col:
        return result
    
    # Resolve column names
    col_r = resolve_column(col, list(df_cleaned.columns))
    b_r = resolve_column(breakdown, list(df_cleaned.columns))
    
    if not col_r or col_r not in df_cleaned.columns:
        return result
    if not b_r or b_r not in df_cleaned.columns:
        return result
    
    # Apply subspace filter
    df_subspace = _apply_subspace_filter(df_cleaned, subspace)
    
    if len(df_subspace) < 3:
        return result
    
    result['subspace_size'] = len(df_subspace)
    
    # Detect reversal based on pattern type
    if pattern == 'TREND':
        is_reversal, tau_global, tau_subspace, p_global, p_subspace, is_significant = _detect_trend_reversal(
            df_cleaned, df_subspace, b_r, col_r
        )
        if is_reversal:
            result['is_paradox'] = bool(True)
            result['is_significant'] = bool(is_significant)
            result['global_metric'] = float(tau_global) if tau_global is not None else None
            result['subspace_metric'] = float(tau_subspace) if tau_subspace is not None else None
            result['p_value'] = float(min(p_global, p_subspace)) if p_global and p_subspace else None
            direction_global = "increasing" if tau_global > 0 else "decreasing"
            direction_subspace = "increasing" if tau_subspace > 0 else "decreasing"
            sig_str = " [SIGNIFICANT]" if is_significant else " [not significant]"
            result['reversal_type'] = f"Trend reversal: global {direction_global} (τ={tau_global:.3f}, p={p_global:.4f}), subspace {direction_subspace} (τ={tau_subspace:.3f}, p={p_subspace:.4f}){sig_str}"
    
    elif pattern == 'ATTRIBUTION':
        is_reversal, top_global, top_subspace, p_value, is_significant = _detect_attribution_reversal(
            df_cleaned, df_subspace, b_r, col_r, agg
        )
        if is_reversal:
            result['is_paradox'] = bool(True)
            result['is_significant'] = bool(is_significant)
            result['global_metric'] = top_global
            result['subspace_metric'] = top_subspace
            result['p_value'] = float(p_value) if p_value is not None else None
            sig_str = " [SIGNIFICANT]" if is_significant else " [not significant]"
            p_str = f", p={p_value:.4f}" if p_value else ""
            result['reversal_type'] = f"Attribution reversal: global top={top_global}, subspace top={top_subspace}{p_str}{sig_str}"
    
    elif pattern == 'OUTSTANDING_VALUE':
        is_reversal, top_global, top_subspace, p_value, is_significant = _detect_outstanding_value_reversal(
            df_cleaned, df_subspace, b_r, col_r, agg
        )
        if is_reversal:
            result['is_paradox'] = bool(True)
            result['is_significant'] = bool(is_significant)
            result['global_metric'] = top_global
            result['subspace_metric'] = top_subspace
            result['p_value'] = float(p_value) if p_value is not None else None
            sig_str = " [SIGNIFICANT]" if is_significant else " [not significant]"
            p_str = f", p={p_value:.4f}" if p_value else ""
            result['reversal_type'] = f"Outstanding value reversal: global={top_global}, subspace={top_subspace}{p_str}{sig_str}"
    
    elif pattern == 'DISTRIBUTION_DIFFERENCE':
        is_reversal, diff_global, diff_subspace, p_value, is_significant = _detect_distribution_reversal(
            df_cleaned, df_subspace, b_r, col_r
        )
        if is_reversal:
            result['is_paradox'] = bool(True)
            result['is_significant'] = bool(is_significant)
            result['global_metric'] = float(diff_global) if diff_global is not None else None
            result['subspace_metric'] = float(diff_subspace) if diff_subspace is not None else None
            result['p_value'] = float(p_value) if p_value is not None else None
            sig_str = " [SIGNIFICANT]" if is_significant else " [not significant]"
            p_str = f", p={p_value:.4f}" if p_value else ""
            result['reversal_type'] = f"Distribution reversal: global diff={diff_global:.3f}, subspace diff={diff_subspace:.3f}{p_str}{sig_str}"
    
    return result


def compute_simpson_paradox_rate(
    insights: List[Dict[str, Any]],
    df_cleaned: pd.DataFrame = None,
    profile_path: str = None,
) -> Dict[str, Any]:
    """
    Compute Simpson's Paradox Rate across all insights.
    
    Simpson's Paradox Rate (SPR) = (# insights with paradox) / (# insights with subspace)
    
    Args:
        insights: List of insight dictionaries
        df_cleaned: Cleaned dataframe for computation
        profile_path: Path to profile.json
    
    Returns:
        Dictionary with:
            - simpson_paradox_rate: float [0, 1]
            - paradox_count: int
            - subspace_count: int
            - total_insights: int
            - paradoxes: list of paradox details
            - by_pattern: dict of rates by pattern type
    """
    empty = {
        'simpson_paradox_rate': 0.0,
        'significant_paradox_rate': 0.0,
        'paradox_count': 0,
        'significant_paradox_count': 0,
        'subspace_count': 0,
        'total_insights': len(insights),
        'paradoxes': [],
        'by_pattern': {},
    }
    
    if df_cleaned is None or len(insights) == 0:
        return empty
    
    paradoxes = []
    subspace_count = 0
    pattern_stats = {}
    
    for idx, ins in enumerate(insights):
        insight_data = ins.get('insight', ins)
        subspace = insight_data.get('subspace', [])
        pattern = insight_data.get('pattern', '').upper().replace(' ', '_')
        
        # Only evaluate insights with subspace
        if not subspace:
            continue
        
        subspace_count += 1
        
        # Initialize pattern stats
        if pattern not in pattern_stats:
            pattern_stats[pattern] = {
                'paradox_count': 0,
                'significant_paradox_count': 0,
                'subspace_count': 0
            }
        pattern_stats[pattern]['subspace_count'] += 1
        
        # Detect paradox
        result = detect_simpson_paradox_single(ins, df_cleaned, profile_path)
        
        if result['is_paradox']:
            paradoxes.append({
                'insight_index': idx,
                'pattern': result['pattern'],
                'breakdown': insight_data.get('breakdown', ''),
                'measure': insight_data.get('measure', ''),
                'subspace': subspace,
                'global_metric': result['global_metric'],
                'subspace_metric': result['subspace_metric'],
                'p_value': result['p_value'],
                'is_significant': result['is_significant'],
                'reversal_type': result['reversal_type'],
                'subspace_size': result['subspace_size'],
            })
            pattern_stats[pattern]['paradox_count'] += 1
            if result['is_significant']:
                pattern_stats[pattern]['significant_paradox_count'] += 1
    
    # Compute rates
    paradox_count = len(paradoxes)
    significant_paradox_count = sum(1 for p in paradoxes if p['is_significant'])
    simpson_paradox_rate = paradox_count / subspace_count if subspace_count > 0 else 0.0
    significant_paradox_rate = significant_paradox_count / subspace_count if subspace_count > 0 else 0.0
    
    # Compute by-pattern rates
    by_pattern = {}
    for pattern, stats in pattern_stats.items():
        rate = stats['paradox_count'] / stats['subspace_count'] if stats['subspace_count'] > 0 else 0.0
        sig_rate = stats['significant_paradox_count'] / stats['subspace_count'] if stats['subspace_count'] > 0 else 0.0
        by_pattern[pattern] = {
            'paradox_count': stats['paradox_count'],
            'significant_paradox_count': stats['significant_paradox_count'],
            'subspace_count': stats['subspace_count'],
            'simpson_paradox_rate': round(rate, 4),
            'significant_paradox_rate': round(sig_rate, 4),
        }
    
    return {
        'simpson_paradox_rate': round(simpson_paradox_rate, 4),
        'significant_paradox_rate': round(significant_paradox_rate, 4),
        'paradox_count': paradox_count,
        'significant_paradox_count': significant_paradox_count,
        'subspace_count': subspace_count,
        'total_insights': len(insights),
        'paradoxes': paradoxes,
        'by_pattern': by_pattern,
    }
