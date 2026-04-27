"""
Debug script for significance.py - check why 0 insights are evaluated

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/debug/debug_significance.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.data_loader import load_and_clean_data
from evaluation.metrics.significance import parse_measure
from evaluation.configs.debug_config import (
    DATA_PATH,
    BASELINE_INSIGHTS_PATH
)
import json

# Load data
csv_path = DATA_PATH
df_raw, df_cleaned = load_and_clean_data(csv_path)

# Load Baseline insights
insights_baseline_path = BASELINE_INSIGHTS_PATH
with open(insights_baseline_path, 'r', encoding='utf-8') as f:
    insights_baseline = json.load(f)

print(f"Total insights: {len(insights_baseline)}")
print(f"Columns in data: {list(df_cleaned.columns)}")
print()

# Check first few insights
for i, ins in enumerate(insights_baseline[:5]):
    # Access nested insight object if it exists
    insight_data = ins.get('insight', ins)
    pattern = insight_data.get('pattern', '')
    measure = insight_data.get('measure', '')
    agg, col = parse_measure(measure)
    breakdown = insight_data.get('breakdown', '')
    
    print(f"Insight {i}:")
    print(f"  Pattern: {pattern}")
    print(f"  Measure: {measure} -> agg={agg}, col={col}")
    print(f"  Breakdown: {breakdown}")
    print(f"  Column in data: {col in df_cleaned.columns}")
    print(f"  Breakdown in data: {breakdown in df_cleaned.columns if breakdown else 'N/A'}")
    print()
