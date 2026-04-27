"""
Test script for subspace.py - compares QUIS vs Baseline

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_subspace.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.subspace import compute_subspace_count
from evaluation.configs.test_config import (
    QUIS_INSIGHTS_PATH,
    BASELINE_INSIGHTS_PATH
)
import json

# Test subspace count
print("Testing subspace.py - QUIS vs Baseline")
print("="*70)

insights_ifq_path = QUIS_INSIGHTS_PATH
insights_baseline_path = BASELINE_INSIGHTS_PATH

print(f"Loading QUIS insights from: {insights_ifq_path}")
print(f"Loading Baseline insights from: {insights_baseline_path}")

try:
    # Load QUIS insights
    with open(insights_ifq_path, 'r', encoding='utf-8') as f:
        insights_ifq = json.load(f)
    print(f"QUIS insights loaded: {len(insights_ifq)} insights")
    
    # Load Baseline insights
    with open(insights_baseline_path, 'r', encoding='utf-8') as f:
        insights_baseline = json.load(f)
    print(f"Baseline insights loaded: {len(insights_baseline)} insights")
    
    # Compute subspace count for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Subspace Count...")
    print("-"*70)
    result_ifq = compute_subspace_count(insights_ifq)
    
    print(f"QUIS Results:")
    print(f"  - Total subspaces: {result_ifq['total_subspaces']}")
    print(f"  - Total insights: {result_ifq['total_insights']}")
    print(f"  - Insights with subspace: {result_ifq['insights_with_subspace']}")
    print(f"  - Insights without subspace: {result_ifq['insights_without_subspace']}")
    print(f"\n  - Subspaces by pattern:")
    for pattern, count in sorted(result_ifq['subspaces_by_pattern'].items()):
        print(f"    {pattern}: {count}")
    print(f"\n  - Pattern distribution:")
    for pattern, count in sorted(result_ifq['pattern_distribution'].items()):
        print(f"    {pattern}: {count}")
    
    # Compute subspace count for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Subspace Count...")
    print("-"*70)
    result_baseline = compute_subspace_count(insights_baseline)
    
    print(f"Baseline Results:")
    print(f"  - Total subspaces: {result_baseline['total_subspaces']}")
    print(f"  - Total insights: {result_baseline['total_insights']}")
    print(f"  - Insights with subspace: {result_baseline['insights_with_subspace']}")
    print(f"  - Insights without subspace: {result_baseline['insights_without_subspace']}")
    print(f"\n  - Subspaces by pattern:")
    for pattern, count in sorted(result_baseline['subspaces_by_pattern'].items()):
        print(f"    {pattern}: {count}")
    print(f"\n  - Pattern distribution:")
    for pattern, count in sorted(result_baseline['pattern_distribution'].items()):
        print(f"    {pattern}: {count}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"QUIS Total Subspaces: {result_ifq['total_subspaces']}")
    print(f"Baseline Total Subspaces: {result_baseline['total_subspaces']}")
    
    if result_ifq['total_subspaces'] > result_baseline['total_subspaces']:
        winner = "QUIS"
        diff = result_ifq['total_subspaces'] - result_baseline['total_subspaces']
    else:
        winner = "Baseline"
        diff = result_baseline['total_subspaces'] - result_ifq['total_subspaces']
    
    print(f"Winner: {winner} (by {diff} subspaces)")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
