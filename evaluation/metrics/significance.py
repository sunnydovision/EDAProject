"""
Statistical significance metric computation.

Measures whether insights are statistically significant (not random noise).
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, Optional
from scipy import stats
from scipy.stats import chi2_contingency, ks_2samp

from .breakdown_measure import _load_column_classes, _is_categorical


def parse_measure(measure_str: str) -> tuple[str, str] | None:
    """
    Parse measure string into (agg, column).
    Returns None if aggregation type is not recognized.
    """
    s = measure_str.strip()
    # Support more aggregation types
    m = re.match(r"(SUM|MEAN|AVG|AVERAGE|COUNT|MIN|MAX|MEDIAN|STD|STDEV|TOTAL)\s*\(\s*([^)]+)\s*\)", s, re.IGNORECASE)
    if m:
        agg = m.group(1).lower()
        col = m.group(2).strip()
        # Normalize aliases
        if agg in ("average", "avg"):
            agg = "mean"
        elif agg in ("total",):
            agg = "sum"
        elif agg in ("stdev",):
            agg = "std"
        return agg, col
    if re.match(r"COUNT\s*\(\s*\*\s*\)", s, re.IGNORECASE):
        return "count", "*"
    return None  # Unknown aggregation — reject


def compute_significance(
    insights: List[Dict],
    df_cleaned: pd.DataFrame,
    csv_path: str = None,
    profile_path: str = None,
) -> Dict[str, Any]:
    """
    Compute statistical significance of insights using pattern-specific p-value calculation.

    For each insight, compute p-value based on its pattern:
    - Trend: Mann-Kendall trend test p-value
    - Outstanding Value: Z-test p-value
    - Attribution: Chi-square test p-value
    - Distribution Difference: KS-test p-value

    Significance Rate = (1/N) * Sigma 1(p_i < alpha) where alpha = 0.05

    Args:
        insights: List of insight dictionaries
        df_cleaned: Cleaned dataframe for computation
        csv_path: Path to CSV file (for detecting separator)

    Returns:
        Dictionary with significance metrics (overall and per pattern type)
    """
    _PATTERNS_ZERO = ['TREND', 'OUTSTANDING_VALUE', 'ATTRIBUTION', 'DISTRIBUTION_DIFFERENCE']
    if len(insights) == 0:
        return {
            'avg_effect_size': 0.0,
            'significant_count': 0,
            'significant_rate': 0.0,
            'max_effect_size': 0.0,
            'total_evaluated': 0,
            'by_pattern': {p: {'significant_count': 0, 'total_count': 0, 'significant_rate': 0.0} for p in _PATTERNS_ZERO},
        }

    _PATTERNS = ['TREND', 'OUTSTANDING_VALUE', 'ATTRIBUTION', 'DISTRIBUTION_DIFFERENCE']
    _empty = {
        'avg_effect_size': 0.0,
        'significant_count': 0,
        'significant_rate': 0.0,
        'max_effect_size': 0.0,
        'total_evaluated': 0,
        'by_pattern': {p: {'significant_count': 0, 'total_count': 0, 'significant_rate': 0.0} for p in _PATTERNS},
    }

    try:
        alpha = 0.05
        effect_sizes = []
        significant_count = 0

        pattern_stats = {p: {'significant_count': 0, 'total_count': 0, 'insights': []} for p in _PATTERNS}

        for ins in insights:
            insight_data = ins.get('insight', ins)
            pattern = insight_data.get('pattern', '')
            measure = insight_data.get('measure', '')
            parsed = parse_measure(measure)
            if parsed is None:
                continue  # Unknown aggregation type
            agg, col = parsed
            breakdown = insight_data.get('breakdown', '')

            pattern_upper = pattern.upper().replace(' ', '_')

            # For COUNT(*), use breakdown column if available
            if not col or col == "*":
                if breakdown and breakdown in df_cleaned.columns:
                    col = breakdown
                else:
                    continue

            col_resolved = resolve_column(col, list(df_cleaned.columns)) or col
            breakdown_resolved = (
                resolve_column(breakdown, list(df_cleaned.columns)) or breakdown
            ) if breakdown else None

            if col_resolved not in df_cleaned.columns:
                continue
            if breakdown_resolved and breakdown_resolved not in df_cleaned.columns:
                continue

            # ── single source of truth ──────────────────────────────────
            scored = compute_insight_score(
                pattern, df_cleaned, breakdown_resolved, col_resolved, agg,
                profile_path=profile_path,
            )
            p_value = scored.get('p_value')
            effect  = scored.get('score')
            significant = scored.get('significant')

            if p_value is None or effect is None:
                continue

            effect_sizes.append(effect)
            if significant:
                significant_count += 1

            if pattern_upper in pattern_stats:
                pattern_stats[pattern_upper]['total_count'] += 1
                if significant:
                    pattern_stats[pattern_upper]['significant_count'] += 1
                pattern_stats[pattern_upper]['insights'].append({
                    'breakdown': breakdown_resolved,
                    'col': col_resolved,
                    'p_value': p_value,
                    'effect_size': effect,
                    'significant': str(significant),
                })

        if not effect_sizes:
            return _empty

        by_pattern = {}
        pattern_rates = []
        for p, data in pattern_stats.items():
            total = data['total_count']
            sig   = data['significant_count']
            rate = sig / total if total > 0 else 0.0
            by_pattern[p] = {
                'significant_count': sig,
                'total_count': total,
                'significant_rate': rate,
                'insights': data['insights'],
            }
            pattern_rates.append(rate)

        # Pattern-averaged significance: average of pattern-specific rates
        pattern_avg_significance = float(np.mean(pattern_rates)) if pattern_rates else 0.0

        return {
            'avg_effect_size': float(np.mean(effect_sizes)),
            'significant_count': significant_count,
            'significant_rate': significant_count / len(effect_sizes),
            'pattern_avg_significance': pattern_avg_significance,  # New metric
            'max_effect_size': float(max(effect_sizes)),
            'total_evaluated': len(effect_sizes),
            'by_pattern': by_pattern,
        }
    except Exception as e:
        print(f"Significance computation failed: {e}")
        return {**_empty, 'error': str(e)}


def resolve_column(name: str, df_columns: list[str]) -> str | None:
    """
    Map column name from Insight Card to actual DataFrame column.
    """
    if not name or not df_columns:
        return None
    cols = list(df_columns)
    if name in cols:
        return name
    normalized = name.replace(" ", "_")
    if normalized in cols:
        return normalized
    name_lower = name.lower()
    for c in cols:
        if c.replace(" ", "_") == normalized or c.lower() == name_lower:
            return c
    for c in cols:
        c_norm = c.replace(" ", "_")
        if name in c or c in name or normalized in c or c_norm in normalized:
            return c
    # Token overlap
    name_tokens = set(normalized.lower().split("_"))
    best_col, best_score = None, 0
    for c in cols:
        col_tokens = set(c.replace(" ", "_").lower().split("_"))
        overlap = len(name_tokens & col_tokens) / max(len(name_tokens), 1)
        if overlap >= 0.33 and overlap > best_score:
            best_score = overlap
            best_col = c
    return best_col


def compute_insight_score(
    pattern: str,
    df: pd.DataFrame,
    breakdown: str,
    col: str,
    agg: str = None,
    profile_path: str = None,
) -> Dict[str, Any]:
    """
    Compute a normalised effect-size score AND p-value for one insight.

    Score is an effect-size measure in [0, 1] — independent of sample size,
    so it does NOT saturate like (1 - p_value) does for large datasets.

    Pattern → score formula:
      OUTSTANDING_VALUE  : z / (z + 1)        where z = (max - μ) / σ
      TREND              : |Kendall τ|         from Mann-Kendall test  [0, 1]
      ATTRIBUTION        : Cramér's V          from Chi-square          [0, 1]
      DISTRIBUTION_DIFF  : KS statistic        from KS test             [0, 1]

    Returns dict:
      {
        'score':   float in [0, 1] or None,
        'p_value': float or None,
        'significant': bool or None   (p_value < 0.05)
      }
    """
    result: Dict[str, Any] = {'score': None, 'p_value': None, 'significant': None}
    alpha = 0.05
    pattern_upper = pattern.upper().replace(' ', '_')
    col_classes = _load_column_classes(profile_path) if profile_path else {}

    if pattern_upper == 'OUTSTANDING_VALUE':
        if col not in df.columns:
            return result
        if breakdown and breakdown in df.columns:
            try:
                agg_func = (agg or 'mean').lower()
                if agg_func == 'count':
                    grouped = df.groupby(breakdown).size()
                elif agg_func == 'min':
                    grouped = df.groupby(breakdown)[col].min()
                elif agg_func == 'max':
                    grouped = df.groupby(breakdown)[col].max()
                elif agg_func == 'sum':
                    grouped = df.groupby(breakdown)[col].sum()
                else:
                    grouped = df.groupby(breakdown)[col].mean()
                values = grouped.values
            except Exception:
                values = pd.to_numeric(df[col], errors='coerce').dropna().values
        else:
            values = pd.to_numeric(df[col], errors='coerce').dropna().values
        if len(values) < 3:
            return result
        mean_val = values.mean()
        std_val = values.std()
        if std_val == 0:
            return result
        z = abs((values.max() - mean_val) / std_val)
        p = float(1 - stats.norm.cdf(z))
        score = float(z / (z + 1))          # maps [0, ∞) → [0, 1)
        result['score'] = round(score, 4)
        result['p_value'] = round(p, 6)
        result['significant'] = p < alpha

    elif pattern_upper == 'TREND':
        if not (breakdown and breakdown in df.columns and col in df.columns):
            return result
        # TREND requires datetime breakdown — numeric breakdown is not a time axis
        if not _is_categorical(df[breakdown], breakdown, col_classes or None):
            return result
        try:
            x_dt = pd.to_datetime(df[breakdown], errors='coerce')
        except Exception:
            return result
        if x_dt.notna().sum() < 3:
            return result
        y = pd.to_numeric(df[col], errors='coerce')
        mask = x_dt.notna() & y.notna()
        if mask.sum() < 3:
            return result
        y_clean = y[mask].values
        try:
            import pymannkendall as mk
            res = mk.original_test(y_clean)
            # Kendall τ is the normalised effect size for TREND
            score = float(abs(res.Tau))      # [0, 1]
            p = float(res.p)
            result['score'] = round(score, 4)
            result['p_value'] = round(p, 6)
            result['significant'] = p < alpha
        except Exception:
            return result

    elif pattern_upper == 'ATTRIBUTION':
        if not (breakdown and breakdown in df.columns and col in df.columns):
            return result
        # ATTRIBUTION requires categorical breakdown (grouping descriptor)
        if not _is_categorical(df[breakdown], breakdown, col_classes or None):
            return result
        try:
            col_numeric = pd.to_numeric(df[col], errors='coerce')
            if col_numeric.isna().all():
                ct = pd.crosstab(df[breakdown], df[col])
            else:
                ct = pd.crosstab(df[breakdown], pd.cut(col_numeric, bins=5, duplicates='drop'))
            if ct.size == 0 or ct.sum().sum() == 0:
                return result
            chi2_stat, p, dof, _ = chi2_contingency(ct)
            n = ct.sum().sum()
            # Cramér's V = sqrt(χ² / (n * (min(r,c) - 1)))
            min_dim = min(ct.shape) - 1
            if min_dim <= 0 or n == 0:
                return result
            cramers_v = float(np.sqrt(chi2_stat / (n * min_dim)))
            cramers_v = min(max(cramers_v, 0.0), 1.0)
            result['score'] = round(cramers_v, 4)
            result['p_value'] = round(float(p), 6)
            result['significant'] = p < alpha
        except Exception:
            return result

    elif pattern_upper == 'DISTRIBUTION_DIFFERENCE':
        if not (breakdown and breakdown in df.columns and col in df.columns):
            return result
        if breakdown == col:
            return result
        # DISTRIBUTION_DIFFERENCE requires categorical breakdown (two groups to compare)
        if not _is_categorical(df[breakdown], breakdown, col_classes or None):
            return result
        cats = df[breakdown].unique()
        if len(cats) < 2:
            return result
        g1 = pd.to_numeric(df[df[breakdown] == cats[0]][col], errors='coerce').dropna()
        g2 = pd.to_numeric(df[df[breakdown] == cats[1]][col], errors='coerce').dropna()
        if len(g1) < 3 or len(g2) < 3:
            return result
        ks_stat, p = ks_2samp(g1, g2)
        result['score'] = round(float(ks_stat), 4)   # KS statistic ∈ [0, 1]
        result['p_value'] = round(float(p), 6)
        result['significant'] = p < alpha

    return result


def compute_p_value(pattern: str, df: pd.DataFrame, breakdown: str, col: str, agg: str = None):
    """Compute p-value based on pattern type (ISGEN pattern types)."""
    pattern_upper = pattern.upper()
    
    if pattern_upper == 'TREND':
        # Mann-Kendall trend test p-value
        if not (breakdown and breakdown in df.columns and col in df.columns):
            return None
        
        # Skip if breakdown equals col (invalid test)
        if breakdown == col:
            return None
        
        # Check if breakdown is categorical (string/datetime) and col is numeric
        # This is typical for COUNT measures: COUNT(numeric_col) GROUP BY categorical_col
        breakdown_dtype = str(df[breakdown].dtype)
        col_dtype = str(df[col].dtype)
        
        if 'str' in breakdown_dtype or 'object' in breakdown_dtype or 'datetime' in breakdown_dtype or breakdown_dtype.startswith('datetime'):
            # Try to convert datetime/string breakdown to numeric
            try:
                # Infer format from first non-null value to avoid warning
                sample_value = df[breakdown].dropna().iloc[0] if df[breakdown].dropna().shape[0] > 0 else None
                if sample_value and isinstance(sample_value, str):
                    # Try to infer format from sample
                    from datetime import datetime
                    # Try common formats
                    formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
                    for fmt in formats:
                        try:
                            datetime.strptime(sample_value, fmt)
                            # If successful, use this format
                            x_data = pd.to_datetime(df[breakdown], errors='coerce', format=fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # No format matched, let pandas infer
                        x_data = pd.to_datetime(df[breakdown], errors='coerce')
                else:
                    # Not a string, let pandas infer
                    x_data = pd.to_datetime(df[breakdown], errors='coerce')
                if x_data.notna().sum() >= 3:
                    # Convert to timestamp (numeric)
                    x_data_numeric = x_data.astype('int64') / 10**9  # Convert to seconds
                    y_data = pd.to_numeric(df[col], errors='coerce')
                    mask = x_data_numeric.notna() & y_data.notna()
                    if mask.sum() >= 3:
                        x_clean = x_data_numeric[mask].values
                        y_clean = y_data[mask].values
                        # Use Mann-Kendall test
                        import pymannkendall as mk
                        mk_result = mk.original_test(y_clean)

                        # Logistic regression
                        try:
                            from sklearn.linear_model import LogisticRegression
                            import numpy as np

                            X = x_clean.reshape(-1, 1)
                            y_binary = (y_clean > np.median(y_clean)).astype(int)

                            lr = LogisticRegression()
                            lr.fit(X, y_binary)
                            lr_coef = lr.coef_[0, 0]

                            return {'mann_kendall_p': mk_result.p, 'logistic_regression_coef': lr_coef}
                        except Exception as e:
                            print(f'TREND logistic regression failed: {e}')
                            return {'mann_kendall_p': mk_result.p, 'logistic_regression_coef': None}
            except Exception as e:
                print(f'TREND datetime conversion failed: {e}')
            
            # Fallback: Aggregate by breakdown
            try:
                grouped = df.groupby(breakdown)[col].count()
                x_data = pd.to_numeric(grouped.index, errors='coerce')
                y_data = pd.Series(grouped.values)
            except Exception as e:
                print(f'TREND aggregation fallback failed: {e}')
                return None
        elif 'str' in col_dtype or 'object' in col_dtype:
            # Aggregate COUNT by breakdown first
            try:
                grouped = df.groupby(breakdown)[col].count()
                x_data = pd.to_numeric(grouped.index, errors='coerce')
                y_data = pd.Series(grouped.values)
            except Exception as e:
                print(f'TREND categorical aggregation failed: {e}')
                return None
        else:
            # Convert to numeric, handling errors
            x_data = pd.to_numeric(df[breakdown], errors='coerce')
            y_data = pd.to_numeric(df[col], errors='coerce')
        
        mask = x_data.notna() & y_data.notna()
        if mask.sum() < 3:
            return None
        
        x_clean = x_data[mask].values
        y_clean = y_data[mask].values

        # Mann-Kendall test
        import pymannkendall as mk
        mk_result = mk.original_test(y_clean)

        # Logistic regression
        try:
            from sklearn.linear_model import LogisticRegression
            import numpy as np

            X = x_clean.reshape(-1, 1)
            y_binary = (y_clean > np.median(y_clean)).astype(int)

            lr = LogisticRegression()
            lr.fit(X, y_binary)
            lr_coef = lr.coef_[0, 0]

            return {'mann_kendall_p': mk_result.p, 'logistic_regression_coef': lr_coef}
        except Exception as e:
            print(f'TREND logistic regression (else path) failed: {e}')
            return {'mann_kendall_p': mk_result.p, 'logistic_regression_coef': None}
    
    elif pattern_upper == 'OUTSTANDING_VALUE':
        # Z-test p-value: z = (v_max - μ) / σ, p = 1 - Φ(z)
        if col not in df.columns:
            return None

        # Aggregate by breakdown using the correct aggregation function from measure
        if breakdown and breakdown in df.columns:
            try:
                agg_func = agg.lower()
                if agg_func == 'count':
                    # For COUNT, use groupby().size() to count rows
                    grouped = df.groupby(breakdown).size()
                elif agg_func == 'min':
                    grouped = df.groupby(breakdown)[col].min()
                elif agg_func == 'max':
                    grouped = df.groupby(breakdown)[col].max()
                elif agg_func == 'sum':
                    grouped = df.groupby(breakdown)[col].sum()
                elif agg_func == 'mean' or agg_func == 'avg':
                    grouped = df.groupby(breakdown)[col].mean()
                else:
                    # Fallback to count for unknown aggregation
                    grouped = df.groupby(breakdown)[col].count()
                values = grouped.values
            except Exception as e:
                print(f'OUTSTANDING_VALUE aggregation failed: {e}')
                # Fallback to direct column values
                values = pd.to_numeric(df[col], errors='coerce').dropna()
        else:
            values = pd.to_numeric(df[col], errors='coerce').dropna()

        if len(values) < 3:
            return None

        mean_val = values.mean()
        std_val = values.std()
        if std_val == 0:
            return None

        extreme_val = values.max()
        z_score = (extreme_val - mean_val) / std_val
        p_value = 1 - stats.norm.cdf(z_score)
        return p_value
    
    elif pattern_upper == 'ATTRIBUTION':
        # Chi-square test p-value: χ² = Σ (O - E)² / E
        if not (breakdown and breakdown in df.columns and col in df.columns):
            return None
        
        # Check if col is categorical (likely COUNT measure)
        col_dtype = str(df[col].dtype)
        if 'str' in col_dtype or 'object' in col_dtype:
            # For categorical columns, use count-based chi-square
            try:
                contingency_table = pd.crosstab(df[breakdown], df[col])
            except Exception as e:
                print(f'ATTRIBUTION contingency table failed: {e}')
                return None
        else:
            # Convert col to numeric for binning
            col_numeric = pd.to_numeric(df[col], errors='coerce')
            if col_numeric.isna().all():
                return None
            
            try:
                contingency_table = pd.crosstab(df[breakdown], pd.cut(col_numeric, bins=5, duplicates='drop'))
            except Exception as e:
                print(f'ATTRIBUTION binning with 5 bins failed: {e}')
                # Fallback to fewer bins
                contingency_table = pd.crosstab(df[breakdown], pd.cut(col_numeric, bins=3, duplicates='drop'))
        
        if contingency_table.size == 0 or contingency_table.sum().sum() == 0:
            return None
        
        # Check if table is too sparse (many cells with expected < 5)
        try:
            _, p_value, _, expected = chi2_contingency(contingency_table)
            # If more than 20% of cells have expected < 5, p-value might be unreliable
            if (expected < 5).sum() / expected.size > 0.2:
                # Use Fisher's exact test for small tables (2x2)
                if contingency_table.shape == (2, 2):
                    from scipy.stats import fisher_exact
                    _, p_value = fisher_exact(contingency_table)
                else:
                    # For larger sparse tables, still return chi-square but note it's approximate
                    pass
        except Exception as e:
            print(f'ATTRIBUTION chi-square test failed: {e}')
            return None
        return p_value
    
    elif pattern_upper == 'DISTRIBUTION_DIFFERENCE':
        # KS-test p-value: p = KS(p, q)
        if not (breakdown and breakdown in df.columns and col in df.columns):
            return None
        
        # Skip if breakdown equals col (invalid KS-test)
        if breakdown == col:
            return None
        
        categories = df[breakdown].unique()
        if len(categories) < 2:
            return None
        
        cat1_data = pd.to_numeric(df[df[breakdown] == categories[0]][col], errors='coerce').dropna()
        cat2_data = pd.to_numeric(df[df[breakdown] == categories[1]][col], errors='coerce').dropna()
        
        if len(cat1_data) < 3 or len(cat2_data) < 3:
            return None
        
        _, p_value = ks_2samp(cat1_data, cat2_data)
        return p_value
    
    else:
        # Fallback: try to infer pattern from name
        pattern_lower = pattern.lower()
        if 'trend' in pattern_lower:
            return compute_p_value('TREND', df, breakdown, col)
        elif 'outstanding' in pattern_lower or 'outlier' in pattern_lower:
            return compute_p_value('OUTSTANDING_VALUE', df, breakdown, col)
        elif 'attribution' in pattern_lower or 'correlation' in pattern_lower:
            return compute_p_value('ATTRIBUTION', df, breakdown, col)
        else:
            return compute_p_value('DISTRIBUTION_DIFFERENCE', df, breakdown, col)
