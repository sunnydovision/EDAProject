"""
Debug script for significance.py - check why 0 insights are evaluated
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_loader import load_and_clean_data
from significance import parse_measure
import json

# Load data
csv_path = "../data/Adidas_cleaned.csv"
df_raw, df_cleaned = load_and_clean_data(csv_path)

# Load Baseline insights
insights_baseline_path = "../baseline/auto_eda_agent/ifq_compatible_output/insights_summary.json"
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
