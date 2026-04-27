"""
Debug script for QUIS significance - check why only 56/89 insights are evaluated

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/debug/debug_ifq_significance.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.data_loader import load_and_clean_data
from evaluation.metrics.significance import parse_measure, resolve_column
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

print(f"Total QUIS insights: {len(insights_ifq)}")
print(f"Columns in data: {list(df_cleaned.columns)}")
print()

# Check why insights are skipped
skipped_count = 0
evaluated_count = 0

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
            col = breakdown  # Use breakdown for COUNT(*) cases
        else:
            print(f"Insight {i}: SKIP - no valid column (COUNT(*) without breakdown)")
            skipped_count += 1
            continue
    
    # Resolve column names to match cleaned dataframe
    col_resolved = resolve_column(col, list(df_cleaned.columns)) or col
    breakdown_resolved = resolve_column(breakdown, list(df_cleaned.columns)) or breakdown if breakdown else None
    
    # Check if required columns exist
    if col_resolved not in df_cleaned.columns:
        print(f"Insight {i}: SKIP - column '{col}' not found in data")
        skipped_count += 1
        continue
    
    if breakdown_resolved and breakdown_resolved not in df_cleaned.columns:
        print(f"Insight {i}: SKIP - breakdown '{breakdown}' not found in data")
        skipped_count += 1
        continue
    
    evaluated_count += 1

print(f"\nSummary:")
print(f"  Evaluated: {evaluated_count}")
print(f"  Skipped: {skipped_count}")
print(f"  Total: {len(insights_ifq)}")
