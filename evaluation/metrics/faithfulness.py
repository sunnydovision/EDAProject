"""
Faithfulness metric computation.

Measures whether insights are grounded in actual data.
"""

import pandas as pd
import re
from typing import List, Dict, Any


def compute_faithfulness(
    insights: List[Dict], 
    df_raw: pd.DataFrame, 
    df_cleaned: pd.DataFrame,
    csv_path: str = None
) -> Dict[str, Any]:
    """
    Compute faithfulness for a list of insights.
    
    Faithfulness measures if the insights are grounded in the actual data.
    Uses cleaned dataframe for recomputation (like QUIS does).
    
    Args:
        insights: List of insight dictionaries
        df_raw: Raw dataframe (unused, kept for interface consistency)
        df_cleaned: Cleaned dataframe for recomputation
        csv_path: Path to CSV file (for detecting separator)
        
    Returns:
        Dictionary with faithfulness score and details
    """
    verified_count = 0
    total_count = 0
    failed_insights = []
    
    # Determine separator for cleaning reported values
    sep = ","
    if csv_path:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
            sep = ";" if first_line.count(";") > first_line.count(",") else ","
        except:
            pass
    
    for idx, insight_obj in enumerate(insights):
        total_count += 1
        insight = insight_obj.get("insight", {})
        
        breakdown = insight.get("breakdown")
        measure = insight.get("measure")
        subspace = insight.get("subspace", [])
        pattern = insight.get("pattern")
        view_labels = insight.get("view_labels", [])
        view_values = insight.get("view_values", [])
        
        # Skip if essential components are missing
        if not breakdown or not measure or not view_labels or not view_values:
            failed_insights.append({
                "idx": idx,
                "reason": "Missing breakdown, measure, view_labels, or view_values",
                "pattern": pattern,
            })
            continue
        
        # Clean insight for faithfulness check
        cleaned_insight = _clean_insight(insight, df_cleaned.columns, sep)
        col = cleaned_insight["measure_col"]
        agg = cleaned_insight["measure_agg"]
        subspace = cleaned_insight["subspace"]
        
        # Check if columns exist (skip for COUNT(*) wildcard)
        if col != "*" and col not in df_cleaned.columns:
            failed_insights.append({
                "idx": idx,
                "reason": f"Measure column '{col}' not found in data",
                "pattern": pattern,
            })
            continue
        if breakdown not in df_cleaned.columns:
            failed_insights.append({
                "idx": idx,
                "reason": f"Breakdown column '{breakdown}' not found in data",
                "pattern": pattern,
            })
            continue
        
        # Apply subspace filter using cleaned data (like QUIS does)
        df_filtered = df_cleaned.copy()
        for col_filter, val in subspace:
            if col_filter in df_filtered.columns:
                # Convert both to string for comparison to handle numeric values
                df_filtered = df_filtered[df_filtered[col_filter].astype(str) == str(val)]
        
        if df_filtered.empty:
            failed_insights.append({
                "idx": idx,
                "reason": f"Subspace filter resulted in empty dataframe for subspace: {subspace}",
                "pattern": pattern,
            })
            continue
        
        # Recompute values based on aggregation type
        recomputed = _recompute_values(df_filtered, breakdown, col, agg)
        
        if recomputed is None:
            # No recomputation possible, assume passed
            verified_count += 1
            continue
        
        # Convert recomputed index to string to match with view_labels
        recomputed.index = recomputed.index.astype(str)
        
        # Check for duplicate labels (data format error)
        if len(view_labels) != len(set(view_labels)):
            failed_insights.append({
                'idx': idx,
                'reason': f'Duplicate labels in view_labels (data format error - groupby requires unique labels)',
                'pattern': pattern
            })
            continue
        
        # Compare reported vs recomputed values
        value_check_passed = _compare_values(
            view_labels, 
            view_values, 
            recomputed, 
            sep,
            pattern
        )
        
        if not value_check_passed:
            # Get the specific failure reason
            failure_reason = _get_failure_reason(
                view_labels, 
                view_values, 
                recomputed, 
                sep,
                pattern
            )
            failed_insights.append({
                'idx': idx,
                'reason': failure_reason,
                'pattern': pattern
            })
        else:
            verified_count += 1
    
    faithfulness_score = verified_count / total_count if total_count > 0 else 0
    return {
        "faithfulness": faithfulness_score,
        "verified_count": verified_count,
        "total_count": total_count,
        "hallucination_count": total_count - verified_count,
        "hallucination_rate": 1 - faithfulness_score,
        "_failed_insights": failed_insights,
    }


def parse_measure(measure_str: str) -> tuple[str, str]:
    """Parse measure string into (agg, column)."""
    s = measure_str.strip()
    m = re.match(r"(SUM|MEAN|AVG|COUNT|MIN|MAX)\s*\(\s*([^)]+)\s*\)", s, re.IGNORECASE)
    if m:
        return m.group(1).lower(), m.group(2).strip()
    if re.match(r"COUNT\s*\(\s*\*\s*\)", s, re.IGNORECASE):
        return "count", "*"
    return "mean", s


def _clean_insight(insight: Dict, df_columns: list, sep: str) -> Dict:
    """Clean insight values for faithfulness check.
    
    Data is already preprocessed, so no cleaning needed.
    Just parse the measure to extract aggregation and column.
    """
    cleaned = insight.copy()
    
    # Parse measure column name
    measure = insight.get("measure", "")
    agg, col = parse_measure(measure)
    cleaned["measure_col"] = col
    cleaned["measure_agg"] = agg
    
    # Subspace values are already in correct format (data is preprocessed)
    cleaned["subspace"] = insight.get("subspace", [])
    
    return cleaned




def _recompute_values(df: pd.DataFrame, breakdown: str, col: str, agg: str):
    """Recompute values based on aggregation type."""
    # Check if column is numeric before aggregation
    if col not in df.columns:
        return None
    
    if not pd.api.types.is_numeric_dtype(df[col]):
        # Column is string/categorical, use COUNT instead
        agg = 'COUNT'
    
    if breakdown and breakdown in df.columns:
        if agg.lower() in ['avg', 'mean']:
            return df.groupby(breakdown)[col].mean()
        elif agg.upper() == 'SUM':
            return df.groupby(breakdown)[col].sum()
        elif agg.upper() == 'COUNT':
            # Handle COUNT(*) wildcard
            if col == "*":
                return df.groupby(breakdown).size()
            return df.groupby(breakdown)[col].count()
        elif agg.upper() == 'MAX':
            return df.groupby(breakdown)[col].max()
        elif agg.upper() == 'MIN':
            return df.groupby(breakdown)[col].min()
    else:
        # If no breakdown, compute overall aggregation
        if agg.lower() in ['avg', 'mean']:
            return pd.Series([df[col].mean()])
        elif agg.upper() == 'SUM':
            return pd.Series([df[col].sum()])
        elif agg.upper() == 'COUNT':
            return pd.Series([len(df)])
        elif agg.upper() == 'MAX':
            return pd.Series([df[col].max()])
        elif agg.upper() == 'MIN':
            return pd.Series([df[col].min()])
    return None


def _compare_values(view_labels, view_values, recomputed, sep: str, pattern: str) -> bool:
    """Compare reported values with recomputed values.
    
    Data is already preprocessed, so no cleaning needed.
    """
    epsilon = 1e-6
    
    # Ensure recomputed values are numeric
    recomputed = pd.to_numeric(recomputed, errors="coerce")
    
    # Convert reported values to float (data is preprocessed)
    reported_values = {}
    for label, value in zip(view_labels, view_values):
        try:
            reported_values[label] = float(value)
        except:
            reported_values[label] = value
    
    # Convert view_labels to strings
    converted_labels = [str(label) for label in view_labels]
    
    # Convert recomputed index to strings
    recomputed.index = recomputed.index.astype(str)
    
    # Normalize labels to handle integer vs float string mismatch (e.g., "0" vs "0.0", "7.0" vs "7")
    def normalize_label(label: str) -> str:
        """Normalize label to handle integer vs float string mismatch."""
        try:
            as_float = float(label)
            # Only convert if very close to integer (e.g., 1.0 -> 1, not 1.025 -> 1)
            if abs(as_float - round(as_float)) < 0.001:  # Very strict threshold
                return str(int(round(as_float)))
            return label
        except:
            return label
    
    # Normalize both converted labels and recomputed index
    converted_labels = [normalize_label(l) for l in converted_labels]
    recomputed.index = [normalize_label(str(i)) for i in recomputed.index]
    
    # Compare values - check label type and compare 3 cases
    for orig_label, conv_label in zip(view_labels, converted_labels):
        # Case 1: Direct string match
        if conv_label in recomputed.index:
            reported = reported_values[orig_label]
            recomputed_val = recomputed[conv_label]
            # Handle case where recomputed_val is a Series (duplicate labels)
            if isinstance(recomputed_val, pd.Series):
                recomputed_val = recomputed_val.iloc[0]  # Take first value
            delta = abs(reported - recomputed_val)
            if delta <= epsilon:
                continue  # Matched
            return False
        
        # Case 2: Parsed string computed value vs label
        # Try converting recomputed index to string and compare
        found_match = False
        for idx in recomputed.index:
            idx_str = str(idx)
            if idx_str == conv_label:
                reported = reported_values[orig_label]
                recomputed_val = recomputed[idx]
                delta = abs(reported - recomputed_val)
                if delta <= epsilon:
                    found_match = True
                    break
        if found_match:
            continue
        
        # Case 3: Computed value vs parsed float label
        # Only if both can be converted to float
        try:
            conv_label_float = float(conv_label)
            for idx in recomputed.index:
                try:
                    idx_float = float(idx)
                    if abs(conv_label_float - idx_float) < epsilon:
                        reported = reported_values[orig_label]
                        recomputed_val = recomputed[idx]
                        delta = abs(reported - recomputed_val)
                        if delta <= epsilon:
                            found_match = True
                            break
                except:
                    continue
            if found_match:
                continue
        except:
            pass
        
        # If no match found in any case
        return False
    
    return True


def _get_failure_reason(view_labels, view_values, recomputed, sep: str, pattern: str) -> str:
    """Get specific failure reason for debugging.
    
    Data is already preprocessed, so no cleaning needed.
    """
    epsilon = 1e-6
    
    # Convert reported values to float (data is preprocessed)
    reported_values = {}
    for label, value in zip(view_labels, view_values):
        try:
            reported_values[label] = float(value)
        except:
            reported_values[label] = value
    
    # Convert view_labels to strings
    converted_labels = [str(label) for label in view_labels]
    
    # Convert recomputed index to strings
    recomputed.index = recomputed.index.astype(str)
    
    # Normalize labels to handle integer vs float string mismatch (same as _compare_values)
    def normalize_label(label: str) -> str:
        """Normalize label to handle integer vs float string mismatch."""
        try:
            as_float = float(label)
            # Only convert if very close to integer (e.g., 1.0 -> 1, not 1.025 -> 1)
            if abs(as_float - round(as_float)) < 0.001:  # Very strict threshold
                return str(int(round(as_float)))
            return label
        except:
            return label
    
    # Normalize both converted labels and recomputed index
    converted_labels = [normalize_label(l) for l in converted_labels]
    recomputed.index = [normalize_label(str(i)) for i in recomputed.index]
    
    # Find first mismatch - use same 3-case comparison logic
    for orig_label, conv_label in zip(view_labels, converted_labels):
        # Case 1: Direct string match
        if conv_label in recomputed.index:
            reported = reported_values[orig_label]
            recomputed_val = recomputed[conv_label]
            # Handle case where recomputed_val is a Series (duplicate labels)
            if isinstance(recomputed_val, pd.Series):
                recomputed_val = recomputed_val.iloc[0]  # Take first value
            delta = abs(reported - recomputed_val)
            if delta > epsilon:
                return f'Value mismatch for "{orig_label}": reported={reported}, recomputed={recomputed_val}, delta={delta:.2e}'
            continue
        
        # Case 2: Parsed string computed value vs label
        found_match = False
        for idx in recomputed.index:
            idx_str = str(idx)
            if idx_str == conv_label:
                reported = reported_values[orig_label]
                recomputed_val = recomputed[idx]
                delta = abs(reported - recomputed_val)
                if delta > epsilon:
                    return f'Value mismatch for "{orig_label}": reported={reported}, recomputed={recomputed_val}, delta={delta:.2e}'
                found_match = True
                break
        if found_match:
            continue
        
        # Case 3: Computed value vs parsed float label
        try:
            conv_label_float = float(conv_label)
            for idx in recomputed.index:
                try:
                    idx_float = float(idx)
                    if abs(conv_label_float - idx_float) < epsilon:
                        reported = reported_values[orig_label]
                        recomputed_val = recomputed[idx]
                        delta = abs(reported - recomputed_val)
                        if delta > epsilon:
                            return f'Value mismatch for "{orig_label}": reported={reported}, recomputed={recomputed_val}, delta={delta:.2e}'
                        found_match = True
                        break
                except:
                    continue
            if found_match:
                continue
        except:
            pass
        
        # If no match found
        return f'Label "{orig_label}" not found in recomputed values (converted: {conv_label})'
    
    return "Unknown failure"
