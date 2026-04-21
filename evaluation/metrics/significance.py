"""
Statistical significance metric computation.

Measures whether insights are statistically significant (not random noise).
"""

import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any
from scipy import stats
from scipy.stats import chi2_contingency, ks_2samp


def parse_measure(measure_str: str) -> tuple[str, str]:
    """Parse measure string into (agg, column)."""
    s = measure_str.strip()
    m = re.match(r"(SUM|MEAN|AVG|COUNT|MIN|MAX)\s*\(\s*([^)]+)\s*\)", s, re.IGNORECASE)
    if m:
        return m.group(1).lower(), m.group(2).strip()
    if re.match(r"COUNT\s*\(\s*\*\s*\)", s, re.IGNORECASE):
        return "count", "*"
    return "mean", s


def compute_significance(
    insights: List[Dict], 
    df_cleaned: pd.DataFrame,
    csv_path: str = None
) -> Dict[str, Any]:
    """
    Compute statistical significance of insights using pattern-specific p-value calculation.
    
    For each insight, compute p-value based on its pattern:
    - Trend: Linear regression p-value
    - Outstanding Value: Z-test p-value
    - Attribution: Chi-square test p-value
    - Distribution Difference: KS-test p-value
    
    Significance Rate = (1/N) * Sigma 1(p_i < alpha) where alpha = 0.05
    
    Args:
        insights: List of insight dictionaries
        df_cleaned: Cleaned dataframe for computation
        csv_path: Path to CSV file (for detecting separator)
        
    Returns:
        Dictionary with significance metrics
    """
    if len(insights) == 0:
        return {
            'avg_zscore': 0.0,
            'significant_count': 0,
            'significant_rate': 0.0,
            'max_zscore': 0.0,
            'total_evaluated': 0
        }
    
    try:
        from .faithfulness import parse_measure
        
        p_values = []
        significant_count = 0
        alpha = 0.05
        
        for ins in insights:
            # Access nested insight object if it exists
            insight_data = ins.get('insight', ins)
            pattern = insight_data.get('pattern', '')
            measure = insight_data.get('measure', '')
            agg, col = parse_measure(measure)
            breakdown = insight_data.get('breakdown', '')
            
            # For COUNT(*), use breakdown column if available
            if not col or col == "*":
                if breakdown and breakdown in df_cleaned.columns:
                    col = breakdown  # Use breakdown for COUNT(*) cases
                else:
                    continue
            
            # Resolve column names to match cleaned dataframe
            col_resolved = resolve_column(col, list(df_cleaned.columns)) or col
            
            breakdown_resolved = resolve_column(breakdown, list(df_cleaned.columns)) or breakdown if breakdown else None
            
            # Check if required columns exist
            if col_resolved not in df_cleaned.columns:
                continue
            
            if breakdown_resolved and breakdown_resolved not in df_cleaned.columns:
                continue
            
            # Compute p-value based on pattern
            p_value = compute_p_value(
                pattern, 
                df_cleaned, 
                breakdown_resolved, 
                col_resolved
            )
            
            if p_value is not None:
                p_values.append(p_value)
                if p_value < alpha:
                    significant_count += 1
        
        if not p_values:
            return {
                'avg_zscore': 0.0,
                'significant_count': 0,
                'significant_rate': 0.0,
                'max_zscore': 0.0,
                'total_evaluated': 0
            }
        
        # Convert p-values to z-scores for reporting
        z_scores = []
        for p in p_values:
            if p > 0:
                z = stats.norm.ppf(1 - p/2)
                z_scores.append(abs(z))
        
        return {
            'avg_zscore': np.mean(z_scores) if z_scores else 0.0,
            'significant_count': significant_count,
            'significant_rate': significant_count / len(p_values),
            'max_zscore': max(z_scores) if z_scores else 0.0,
            'total_evaluated': len(p_values)
        }
    except Exception as e:
        print(f"Significance computation failed: {e}")
        return {
            'avg_zscore': 0.0,
            'significant_count': 0,
            'significant_rate': 0.0,
            'max_zscore': 0.0,
            'total_evaluated': 0,
            'error': str(e)
        }


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


def compute_p_value(pattern: str, df: pd.DataFrame, breakdown: str, col: str):
    """Compute p-value based on pattern type (ISGEN pattern types)."""
    pattern_upper = pattern.upper()
    
    if pattern_upper == 'TREND':
        # Linear regression p-value: y = βx + ε
        if not (breakdown and breakdown in df.columns and col in df.columns):
            return None
        
        # Skip if breakdown equals col (invalid regression)
        if breakdown == col:
            return None
        
        # Check if breakdown is categorical (string/datetime) and col is numeric
        # This is typical for COUNT measures: COUNT(numeric_col) GROUP BY categorical_col
        breakdown_dtype = str(df[breakdown].dtype)
        col_dtype = str(df[col].dtype)
        
        if 'str' in breakdown_dtype or 'object' in breakdown_dtype or 'datetime' in breakdown_dtype or breakdown_dtype.startswith('datetime'):
            # Try to convert datetime/string breakdown to numeric
            try:
                # Try datetime conversion first
                x_data = pd.to_datetime(df[breakdown], errors='coerce')
                if x_data.notna().sum() >= 3:
                    # Convert to timestamp (numeric)
                    x_data_numeric = x_data.astype('int64') / 10**9  # Convert to seconds
                    y_data = pd.to_numeric(df[col], errors='coerce')
                    mask = x_data_numeric.notna() & y_data.notna()
                    if mask.sum() >= 3:
                        x_clean = x_data_numeric[mask].values
                        y_clean = y_data[mask].values
                        _, _, _, p_value, _ = stats.linregress(x_clean, y_clean)
                        return p_value
            except:
                pass
            
            # Fallback: Aggregate by breakdown
            try:
                grouped = df.groupby(breakdown)[col].count()
                x_data = pd.to_numeric(grouped.index, errors='coerce')
                y_data = pd.Series(grouped.values)
            except:
                return None
        elif 'str' in col_dtype or 'object' in col_dtype:
            # Aggregate COUNT by breakdown first
            try:
                grouped = df.groupby(breakdown)[col].count()
                x_data = pd.to_numeric(grouped.index, errors='coerce')
                y_data = pd.Series(grouped.values)
            except:
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
        _, _, _, p_value, _ = stats.linregress(x_clean, y_clean)
        return p_value
    
    elif pattern_upper == 'OUTSTANDING_VALUE':
        # Z-test p-value: z = (v_max - μ) / σ, p = 1 - Φ(z)
        if col not in df.columns:
            return None
        
        # Aggregate by breakdown using the correct aggregation function from measure
        if breakdown and breakdown in df.columns:
            try:
                agg_func = agg.lower()  # Get aggregation function from measure string
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
            except:
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
            except:
                return None
        else:
            # Convert col to numeric for binning
            col_numeric = pd.to_numeric(df[col], errors='coerce')
            if col_numeric.isna().all():
                return None
            
            try:
                contingency_table = pd.crosstab(df[breakdown], pd.cut(col_numeric, bins=5, duplicates='drop'))
            except:
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
        except:
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
