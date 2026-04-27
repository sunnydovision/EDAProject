"""
Test script for pattern_coverage.py - compares QUIS vs Baseline

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_pattern_coverage.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.data_loader import load_and_clean_data
from evaluation.metrics.pattern_coverage import compute_pattern_coverage, compute_structural_validity
from evaluation.configs.test_config import (
    DATA_PATH,
    QUIS_INSIGHTS_PATH,
    BASELINE_INSIGHTS_PATH
)
import json

# Test pattern coverage
print("Testing pattern_coverage.py - QUIS vs Baseline")
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
    
    # Compute pattern coverage for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Pattern Coverage...")
    print("-"*70)
    result_ifq = compute_pattern_coverage(insights_ifq, df_cleaned)
    
    print(f"QUIS Results:")
    print(f"  - Pattern Coverage: {result_ifq['pattern_coverage']:.2%}")
    print(f"  - Covered Patterns: {result_ifq['covered_count']}/{result_ifq['total_patterns']}")
    print(f"  - Covered Patterns: {result_ifq['covered_patterns']}")
    print(f"  - Uncovered Patterns: {result_ifq['uncovered_patterns']}")
    print(f"\n  - By Pattern:")
    for pattern, data in result_ifq['by_pattern'].items():
        print(f"    {pattern}: {data['valid_count']} valid / {data['total_count']} total ({data['valid_rate']:.2%})")
    
    # Compute pattern coverage for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Pattern Coverage...")
    print("-"*70)
    result_baseline = compute_pattern_coverage(insights_baseline, df_cleaned)
    
    print(f"Baseline Results:")
    print(f"  - Pattern Coverage: {result_baseline['pattern_coverage']:.2%}")
    print(f"  - Covered Patterns: {result_baseline['covered_count']}/{result_baseline['total_patterns']}")
    print(f"  - Covered Patterns: {result_baseline['covered_patterns']}")
    print(f"  - Uncovered Patterns: {result_baseline['uncovered_patterns']}")
    print(f"\n  - By Pattern:")
    for pattern, data in result_baseline['by_pattern'].items():
        print(f"    {pattern}: {data['valid_count']} valid / {data['total_count']} total ({data['valid_rate']:.2%})")
    
    # Compute structural validity for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Structural Validity Rate...")
    print("-"*70)
    svr_ifq = compute_structural_validity(insights_ifq, df_cleaned)
    
    print(f"QUIS SVR Results:")
    print(f"  - Structural Validity Rate: {svr_ifq['structural_validity_rate']:.2%}")
    print(f"  - Valid Count: {svr_ifq['valid_count']}")
    print(f"  - Invalid Count: {svr_ifq['invalid_count']}")
    print(f"  - Total Count: {svr_ifq['total_count']}")
    
    # Compute structural validity for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Structural Validity Rate...")
    print("-"*70)
    svr_baseline = compute_structural_validity(insights_baseline, df_cleaned)
    
    print(f"Baseline SVR Results:")
    print(f"  - Structural Validity Rate: {svr_baseline['structural_validity_rate']:.2%}")
    print(f"  - Valid Count: {svr_baseline['valid_count']}")
    print(f"  - Invalid Count: {svr_baseline['invalid_count']}")
    print(f"  - Total Count: {svr_baseline['total_count']}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"QUIS Pattern Coverage: {result_ifq['pattern_coverage']:.2%}")
    print(f"Baseline Pattern Coverage: {result_baseline['pattern_coverage']:.2%}")
    
    if result_ifq['pattern_coverage'] > result_baseline['pattern_coverage']:
        winner = "QUIS"
        diff = result_ifq['pattern_coverage'] - result_baseline['pattern_coverage']
    else:
        winner = "Baseline"
        diff = result_baseline['pattern_coverage'] - result_ifq['pattern_coverage']
    
    print(f"Winner: {winner} (by {diff:.2%})")
    
    print(f"\nQUIS SVR: {svr_ifq['structural_validity_rate']:.2%}")
    print(f"Baseline SVR: {svr_baseline['structural_validity_rate']:.2%}")
    
    if svr_ifq['structural_validity_rate'] > svr_baseline['structural_validity_rate']:
        svr_winner = "QUIS"
        svr_diff = svr_ifq['structural_validity_rate'] - svr_baseline['structural_validity_rate']
    else:
        svr_winner = "Baseline"
        svr_diff = svr_baseline['structural_validity_rate'] - svr_ifq['structural_validity_rate']
    
    print(f"SVR Winner: {svr_winner} (by {svr_diff:.2%})")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
