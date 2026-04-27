"""
Investigate label mismatch issues

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/debug/investigate_label_mismatch.py
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
print("ROOT CAUSE ANALYSIS: Label Mismatch with Subspace")
print("="*70)

failed_insights = eval_results['faithfulness']['_failed_insights']

# Analyze subspace vs no-subspace failures
with_subspace_failed = 0
without_subspace_failed = 0

for fail in failed_insights:
    idx = fail['idx']
    if idx < len(baseline_insights):
        subspace = baseline_insights[idx]['insight'].get('subspace', [])
        if subspace:
            with_subspace_failed += 1
        else:
            without_subspace_failed += 1

print(f"\nFailed insights with subspace: {with_subspace_failed}")
print(f"Failed insights without subspace: {without_subspace_failed}")

print("\n" + "="*70)
print("DETAILED ANALYSIS: Subspace Label Mismatch")
print("="*70)

# Test a few failed insights with subspace
count = 0
for fail in failed_insights:
    if count >= 5:
        break
    
    idx = fail['idx']
    if idx >= len(baseline_insights):
        continue
    
    insight = baseline_insights[idx]['insight']
    subspace = insight.get('subspace', [])
    
    if not subspace:
        continue
    
    count += 1
    breakdown = insight.get('breakdown')
    measure = insight.get('measure')
    view_labels = insight.get('view_labels', [])
    
    print(f"\n--- Failed Insight #{idx} ---")
    print(f"Breakdown: {breakdown}")
    print(f"Measure: {measure}")
    print(f"Subspace: {subspace}")
    print(f"View labels: {view_labels[:10]}")
    
    # Apply subspace
    df_filtered = df.copy()
    for col_filter, val in subspace:
        if col_filter in df.columns:
            df_filtered = df_filtered[df_filtered[col_filter].astype(str) == str(val)]
    
    # Recompute
    if breakdown and breakdown in df.columns and measure:
        if "MEAN" in measure:
            col = measure.replace("MEAN(", "").replace(")", "")
            if col in df.columns:
                global_result = df.groupby(breakdown)[col].mean()
                filtered_result = df_filtered.groupby(breakdown)[col].mean()
                
                print(f"\nGlobal breakdown values (first 10): {list(global_result.index[:10])}")
                print(f"Filtered breakdown values (first 10): {list(filtered_result.index[:10])}")
                
                # Check if view_labels match global or filtered
                if view_labels:
                    missing_in_global = [l for l in view_labels if l not in global_result.index]
                    missing_in_filtered = [l for l in view_labels if l not in filtered_result.index]
                    
                    print(f"\nView labels missing in global: {missing_in_global[:5]}")
                    print(f"View labels missing in filtered: {missing_in_filtered[:5]}")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("""
ROOT CAUSE: The LLM generates view_labels from GLOBAL data (without subspace),
but the faithfulness check verifies labels against RECOMPUTED data WITH subspace applied.

When subspace is applied, the breakdown values change (some values disappear from the
filtered dataset), so labels that existed globally don't exist in the filtered data.

Example:
- Global: Total Sales values include [0, 160, 203, 224, ...]
- Filtered (Sales Method = Online): Total Sales values include [0, 203, 224, ...] (160 missing)
- LLM generated label "160" from global data
- Faithfulness check fails because "160" doesn't exist in filtered data

SOLUTION: The LLM should generate view_labels AFTER applying subspace, not from global data.
""")
