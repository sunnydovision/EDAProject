"""
Test script for diversity.py - compares IFQ vs Baseline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from diversity import compute_diversity
import json

# Test diversity
print("Testing diversity.py - IFQ vs Baseline")
print("="*70)

insights_ifq_path = "../insights_summary_adidas_2.json"
insights_baseline_path = "../baseline/auto_eda_agent/ifq_compatible_output/insights_summary.json"

print(f"Loading IFQ insights from: {insights_ifq_path}")
print(f"Loading Baseline insights from: {insights_baseline_path}")

try:
    # Load IFQ insights
    with open(insights_ifq_path, 'r', encoding='utf-8') as f:
        insights_ifq = json.load(f)
    print(f"IFQ insights loaded: {len(insights_ifq)} insights")
    
    # Load Baseline insights
    with open(insights_baseline_path, 'r', encoding='utf-8') as f:
        insights_baseline = json.load(f)
    print(f"Baseline insights loaded: {len(insights_baseline)} insights")
    
    # Compute diversity for IFQ
    print("\n" + "-"*70)
    print("Computing IFQ Diversity...")
    print("-"*70)
    ifq_cards = [{'question': ins.get('question', ''), 'reason': ins.get('reason', ''), 
                   'breakdown': ins.get('insight', {}).get('breakdown', ''), 
                   'measure': ins.get('insight', {}).get('measure', '')} for ins in insights_ifq]
    result_ifq = compute_diversity(ifq_cards)
    
    print(f"IFQ Results:")
    print(f"  - Diversity: {result_ifq['diversity']:.3f}")
    print(f"  - Avg similarity: {result_ifq['avg_similarity']:.3f}")
    print(f"  - Num questions: {result_ifq['num_questions']}")
    
    # Compute diversity for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Diversity...")
    print("-"*70)
    baseline_cards = [{'question': ins.get('question', ''), 'reason': ins.get('reason', ''), 
                        'breakdown': ins.get('insight', {}).get('breakdown', ''), 
                        'measure': ins.get('insight', {}).get('measure', '')} for ins in insights_baseline]
    result_baseline = compute_diversity(baseline_cards)
    
    print(f"Baseline Results:")
    print(f"  - Diversity: {result_baseline['diversity']:.3f}")
    print(f"  - Avg similarity: {result_baseline['avg_similarity']:.3f}")
    print(f"  - Num questions: {result_baseline['num_questions']}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"IFQ Diversity: {result_ifq['diversity']:.3f}")
    print(f"Baseline Diversity: {result_baseline['diversity']:.3f}")
    
    if result_ifq['diversity'] > result_baseline['diversity']:
        winner = "IFQ"
        diff = result_ifq['diversity'] - result_baseline['diversity']
    else:
        winner = "Baseline"
        diff = result_baseline['diversity'] - result_ifq['diversity']
    
    print(f"Winner: {winner} (by {diff:.3f})")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
