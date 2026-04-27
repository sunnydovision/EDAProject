"""
Test script for score_uplift.py - compares QUIS vs Baseline

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_score_uplift.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.data_loader import load_and_clean_data
from evaluation.metrics.score_uplift import compute_score_uplift_from_subspace
from evaluation.configs.test_config import (
    DATA_PATH,
    QUIS_INSIGHTS_PATH,
    BASELINE_INSIGHTS_PATH
)
import json

# Test score uplift
print("Testing score_uplift.py - QUIS vs Baseline")
print("="*70)

csv_path = DATA_PATH
insights_ifq_path = QUIS_INSIGHTS_PATH
insights_baseline_path = BASELINE_INSIGHTS_PATH

print(f"Loading data from: {csv_path}")

try:
    df_raw, df_cleaned = load_and_clean_data(csv_path)
    print(f"Data loaded: {len(df_raw)} rows, {len(df_cleaned)} columns")
    
    # Load QUIS insights
    print(f"\nLoading QUIS insights from: {insights_ifq_path}")
    with open(insights_ifq_path, 'r', encoding='utf-8') as f:
        insights_ifq = json.load(f)
    print(f"QUIS insights loaded: {len(insights_ifq)} insights")
    
    # Load Baseline insights
    print(f"Loading Baseline insights from: {insights_baseline_path}")
    with open(insights_baseline_path, 'r', encoding='utf-8') as f:
        insights_baseline = json.load(f)
    print(f"Baseline insights loaded: {len(insights_baseline)} insights")
    
    # Compute score uplift for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Score Uplift from Subspace...")
    print("-"*70)
    result_ifq = compute_score_uplift_from_subspace(insights_ifq, df_cleaned)
    
    print(f"QUIS Results:")
    print(f"  - Insights with subspace (scored): {result_ifq['num_with_subspace_scored']}")
    print(f"  - Insights without subspace (scored): {result_ifq['num_without_subspace_scored']}")
    print(f"  - Mean score with subspace: {result_ifq['mean_score_with_subspace']}")
    print(f"  - Mean score without subspace: {result_ifq['mean_score_without_subspace']}")
    print(f"  - Score uplift (abs): {result_ifq['score_uplift_abs']}")
    print(f"  - Score uplift (ratio): {result_ifq['score_uplift_ratio']}")
    print(f"  - Score uplift direction: {result_ifq['score_uplift_direction']}")
    
    # Compute score uplift for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Score Uplift from Subspace...")
    print("-"*70)
    result_baseline = compute_score_uplift_from_subspace(insights_baseline, df_cleaned)
    
    print(f"Baseline Results:")
    print(f"  - Insights with subspace (scored): {result_baseline['num_with_subspace_scored']}")
    print(f"  - Insights without subspace (scored): {result_baseline['num_without_subspace_scored']}")
    print(f"  - Mean score with subspace: {result_baseline['mean_score_with_subspace']}")
    print(f"  - Mean score without subspace: {result_baseline['mean_score_without_subspace']}")
    print(f"  - Score uplift (abs): {result_baseline['score_uplift_abs']}")
    print(f"  - Score uplift (ratio): {result_baseline['score_uplift_ratio']}")
    print(f"  - Score uplift direction: {result_baseline['score_uplift_direction']}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"QUIS Score Uplift (abs): {result_ifq['score_uplift_abs']}")
    print(f"Baseline Score Uplift (abs): {result_baseline['score_uplift_abs']}")
    
    if result_ifq['score_uplift_abs'] is not None and result_baseline['score_uplift_abs'] is not None:
        if result_ifq['score_uplift_abs'] > result_baseline['score_uplift_abs']:
            winner = "QUIS"
            diff = result_ifq['score_uplift_abs'] - result_baseline['score_uplift_abs']
        else:
            winner = "Baseline"
            diff = result_baseline['score_uplift_abs'] - result_ifq['score_uplift_abs']
        
        print(f"Winner: {winner} (by {diff:.4f})")
    else:
        print("Cannot compare - one or both values are None")
    
    print(f"\nQUIS Score Uplift (ratio): {result_ifq['score_uplift_ratio']}")
    print(f"Baseline Score Uplift (ratio): {result_baseline['score_uplift_ratio']}")
    
    if result_ifq['score_uplift_ratio'] is not None and result_baseline['score_uplift_ratio'] is not None:
        if result_ifq['score_uplift_ratio'] > result_baseline['score_uplift_ratio']:
            ratio_winner = "QUIS"
            ratio_diff = result_ifq['score_uplift_ratio'] - result_baseline['score_uplift_ratio']
        else:
            ratio_winner = "Baseline"
            ratio_diff = result_baseline['score_uplift_ratio'] - result_ifq['score_uplift_ratio']
        
        print(f"Ratio Winner: {ratio_winner} (by {ratio_diff:.4f})")
    else:
        print("Cannot compare ratios - one or both values are None")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
