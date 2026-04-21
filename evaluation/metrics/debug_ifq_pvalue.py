"""
Debug script for IFQ significance - check why p-value computation fails
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_loader import load_and_clean_data
from significance import parse_measure, resolve_column, compute_p_value
import json

# Load data
csv_path = "../data/Adidas_cleaned.csv"
df_raw, df_cleaned = load_and_clean_data(csv_path)

# Load IFQ insights
insights_ifq_path = "../insights_summary_adidas_2.json"
with open(insights_ifq_path, 'r', encoding='utf-8') as f:
    insights_ifq = json.load(f)

print(f"Total IFQ insights: {len(insights_ifq)}")
print()

p_value_failures = []
p_value_successes = []

for i, ins in enumerate(insights_ifq):
    # Access nested insight object if it exists
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
            continue
    
    # Resolve column names
    col_resolved = resolve_column(col, list(df_cleaned.columns)) or col
    breakdown_resolved = resolve_column(breakdown, list(df_cleaned.columns)) or breakdown if breakdown else None
    
    # Check columns
    if col_resolved not in df_cleaned.columns:
        continue
    if breakdown_resolved and breakdown_resolved not in df_cleaned.columns:
        continue
    
    # Compute p-value
    p_value = compute_p_value(pattern, df_cleaned, breakdown_resolved, col_resolved)
    
    if p_value is None:
        p_value_failures.append({
            'idx': i,
            'pattern': pattern,
            'measure': measure,
            'breakdown': breakdown,
            'col': col_resolved
        })
    else:
        p_value_successes.append(p_value)

print(f"P-value computation results:")
print(f"  Successes: {len(p_value_successes)}")
print(f"  Failures: {len(p_value_failures)}")
print()

if p_value_failures:
    print("Failed insights (first 10):")
    for fail in p_value_failures[:10]:
        print(f"  Insight {fail['idx']}: pattern={fail['pattern']}, measure={fail['measure']}, breakdown={fail['breakdown']}, col={fail['col']}")
