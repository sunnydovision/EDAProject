"""
Test script for novelty.py - compares IFQ vs Baseline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from novelty import compute_novelty
import json

# Test novelty
print("Testing novelty.py - IFQ vs Baseline")
print("="*70)

insights_ifq_path = "../insights_summary_adidas_2.json"
insights_baseline_path = "../baseline/auto_eda_agent/ifq_compatible_output/insights_summary.json"

print(f"Loading IFQ insights from: {insights_ifq_path}")
print(f"Loading Baseline insights from: {insights_baseline_path}")

try:
    with open(insights_ifq_path, 'r', encoding='utf-8') as f:
        insights_ifq = json.load(f)
    print(f"IFQ insights loaded: {len(insights_ifq)} insights")
    
    with open(insights_baseline_path, 'r', encoding='utf-8') as f:
        insights_baseline = json.load(f)
    print(f"Baseline insights loaded: {len(insights_baseline)} insights")
    
    # Compute IFQ novelty vs Baseline
    print("\n" + "-"*70)
    print("Computing IFQ Novelty vs Baseline...")
    print("-"*70)
    result_ifq = compute_novelty(insights_ifq, insights_baseline)
    
    print(f"IFQ Novelty Results:")
    print(f"  - Novelty: {result_ifq['novelty']*100:.1f}%")
    print(f"  - Novel count: {result_ifq['novel_count']}")
    print(f"  - Total count: {result_ifq['total_count']}")
    print(f"  - Avg max similarity: {result_ifq['avg_max_similarity']:.3f}")
    
    # Compute Baseline novelty vs IFQ
    print("\n" + "-"*70)
    print("Computing Baseline Novelty vs IFQ...")
    print("-"*70)
    result_baseline = compute_novelty(insights_baseline, insights_ifq)
    
    print(f"Baseline Novelty Results:")
    print(f"  - Novelty: {result_baseline['novelty']*100:.1f}%")
    print(f"  - Novel count: {result_baseline['novel_count']}")
    print(f"  - Total count: {result_baseline['total_count']}")
    print(f"  - Avg max similarity: {result_baseline['avg_max_similarity']:.3f}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"IFQ Novelty: {result_ifq['novelty']*100:.1f}%")
    print(f"Baseline Novelty: {result_baseline['novelty']*100:.1f}%")
    
    if result_ifq['novelty'] > result_baseline['novelty']:
        winner = "IFQ"
        diff = result_ifq['novelty'] - result_baseline['novelty']
    else:
        winner = "Baseline"
        diff = result_baseline['novelty'] - result_ifq['novelty']
    
    print(f"Winner: {winner} (by {diff*100:.1f}%)")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
