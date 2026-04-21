"""
Debug script for Baseline significance - check why only 99/154 insights are evaluated
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_loader import load_and_clean_data
from significance import parse_measure, resolve_column
import json

# Load data
csv_path = "../data/Adidas_cleaned.csv"
df_raw, df_cleaned = load_and_clean_data(csv_path)

# Load Baseline insights
insights_baseline_path = "../baseline/auto_eda_agent/ifq_compatible_output/insights_summary.json"
with open(insights_baseline_path, 'r', encoding='utf-8') as f:
    insights_baseline = json.load(f)

print(f"Total Baseline insights: {len(insights_baseline)}")
print(f"Columns in data: {list(df_cleaned.columns)}")
print()

# Check why insights are skipped
skipped_count = 0
evaluated_count = 0
skip_reasons = {}

for i, ins in enumerate(insights_baseline):
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
            reason = "no_valid_column"
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
            skipped_count += 1
            continue
    
    # Resolve column names to match cleaned dataframe
    col_resolved = resolve_column(col, list(df_cleaned.columns)) or col
    breakdown_resolved = resolve_column(breakdown, list(df_cleaned.columns)) or breakdown if breakdown else None
    
    # Check if required columns exist
    if col_resolved not in df_cleaned.columns:
        reason = f"col_not_found:{col}"
        skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
        skipped_count += 1
        continue
    
    if breakdown_resolved and breakdown_resolved not in df_cleaned.columns:
        reason = f"breakdown_not_found:{breakdown}"
        skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
        skipped_count += 1
        continue
    
    evaluated_count += 1

print(f"\nSummary:")
print(f"  Evaluated: {evaluated_count}")
print(f"  Skipped: {skipped_count}")
print(f"  Total: {len(insights_baseline)}")
print()
print("Skip reasons:")
for reason, count in skip_reasons.items():
    print(f"  {reason}: {count}")
