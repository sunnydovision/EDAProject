"""
Debug script for QUIS significance - check detailed failure reasons

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/debug/debug_ifq_detailed.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.data_loader import load_and_clean_data
from evaluation.metrics.significance import parse_measure, resolve_column, compute_p_value
from evaluation.configs.debug_config import (
    DATA_PATH,
    QUIS_INSIGHTS_PATH
)
import json

# Load data
csv_path = DATA_PATH
df_raw, df_cleaned = load_and_clean_data(csv_path)

# Load QUIS insights
insights_ifq_path = QUIS_INSIGHTS_PATH
with open(insights_ifq_path, 'r', encoding='utf-8') as f:
    insights_ifq = json.load(f)

# Check specific failing insights
failing_indices = [53, 54, 62, 63, 64, 65, 75, 83, 85, 86]

for idx in failing_indices:
    ins = insights_ifq[idx]
    insight_data = ins.get('insight', ins)
    pattern = insight_data.get('pattern', '')
    measure = insight_data.get('measure', '')
    agg, col = parse_measure(measure)
    breakdown = insight_data.get('breakdown', '')
    
    # For COUNT(*), use breakdown column if available
    if not col or col == "*":
        if breakdown and breakdown in df_cleaned.columns:
            col = breakdown
        else:
            print(f"Insight {idx}: SKIP - no valid column")
            continue
    
    # Resolve column names
    col_resolved = resolve_column(col, list(df_cleaned.columns)) or col
    breakdown_resolved = resolve_column(breakdown, list(df_cleaned.columns)) or breakdown if breakdown else None
    
    print(f"Insight {idx}:")
    print(f"  Pattern: {pattern}")
    print(f"  Measure: {measure}")
    print(f"  Breakdown: {breakdown} -> resolved: {breakdown_resolved}")
    print(f"  Col: {col} -> resolved: {col_resolved}")
    print(f"  breakdown == col: {breakdown == col}")
    print(f"  breakdown_resolved == col_resolved: {breakdown_resolved == col_resolved}")
    print(f"  df[{col_resolved}].dtype: {df_cleaned[col_resolved].dtype if col_resolved in df_cleaned.columns else 'N/A'}")
    
    # Try compute p-value with more detail
    try:
        p_value = compute_p_value(pattern, df_cleaned, breakdown_resolved, col_resolved)
        print(f"  P-value: {p_value}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
