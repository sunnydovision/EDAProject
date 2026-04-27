"""
Investigate faithfulness issues

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/debug/investigate_faithfulness.py
"""
import json
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.configs.debug_config import (
    BASELINE_INSIGHTS_PATH,
    RESULTS_DIR
)

# Load baseline insights
with open(BASELINE_INSIGHTS_PATH, 'r') as f:
    baseline_insights = json.load(f)

# Load evaluation results
with open(f"{RESULTS_DIR}/baseline_results.json", 'r') as f:
    eval_results = json.load(f)

# Load actual data
df = pd.read_csv("data/Adidas_cleaned.csv", sep=';')

print("="*70)
print("INVESTIGATION: Baseline Faithfulness Issues")
print("="*70)
print(f"\nTotal baseline insights: {len(baseline_insights)}")
print(f"Faithfulness: {eval_results['faithfulness']['faithfulness']*100:.1f}%")
print(f"Verified: {eval_results['faithfulness']['verified_count']}")
print(f"Failed: {eval_results['faithfulness']['hallucination_count']}")

print("\n" + "="*70)
print("FAILED INSIGHTS ANALYSIS")
print("="*70)

failed_insights = eval_results['faithfulness']['_failed_insights']
print(f"\nTotal failed insights: {len(failed_insights)}")

# Categorize failures
error_types = {}
for fail in failed_insights:
    reason = fail['reason']
    if 'not found in recomputed values' in reason:
        error_type = 'Label not found in data'
    elif 'Breakdown column' in reason and 'not found in data' in reason:
        error_type = 'Breakdown column not found'
    else:
        error_type = 'Other'
    error_types[error_type] = error_types.get(error_type, 0) + 1

print("\nError types:")
for error_type, count in error_types.items():
    print(f"  - {error_type}: {count}")

print("\n" + "="*70)
print("SAMPLE FAILED INSIGHTS")
print("="*70)

for i, fail in enumerate(failed_insights[:10]):
    idx = fail['idx']
    reason = fail['reason']
    pattern = fail['pattern']
    
    print(f"\n--- Insight #{idx} ({pattern}) ---")
    print(f"Reason: {reason}")
    
    if idx < len(baseline_insights):
        insight = baseline_insights[idx]['insight']
        print(f"Breakdown: {insight.get('breakdown', 'N/A')}")
        print(f"Measure: {insight.get('measure', 'N/A')}")
        print(f"Pattern: {insight.get('pattern', 'N/A')}")
        print(f"Subspace: {insight.get('subspace', [])}")
        
        # Check if breakdown column exists in data
        breakdown = insight.get('breakdown', '')
        if breakdown:
            if breakdown in df.columns:
                print(f"✓ Breakdown column '{breakdown}' exists in data")
            else:
                print(f"✗ Breakdown column '{breakdown}' NOT found in data")

print("\n" + "="*70)
print("DATA COLUMNS")
print("="*70)
print(f"Actual columns in data: {list(df.columns)}")

print("\n" + "="*70)
print("SUCCESSFUL INSIGHTS SAMPLE")
print("="*70)

# Find some successful insights
successful_indices = [i for i in range(len(baseline_insights)) if i not in [f['idx'] for f in failed_insights]]
for i in successful_indices[:5]:
    insight = baseline_insights[i]['insight']
    print(f"\n--- Insight #{i} ---")
    print(f"Breakdown: {insight.get('breakdown', 'N/A')}")
    print(f"Measure: {insight.get('measure', 'N/A')}")
    print(f"Pattern: {insight.get('pattern', 'N/A')}")
    print(f"Subspace: {insight.get('subspace', [])}")
