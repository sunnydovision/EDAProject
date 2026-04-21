"""
Test script for diversity.py - compares IFQ vs Baseline
Tests all 4 diversity metrics: semantic, subspace, value, dedup rate
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.diversity import compute_diversity
import json

# Test diversity
print("Testing diversity.py - IFQ vs Baseline")
print("="*70)

insights_ifq_path = "insights_summary_adidas_cleaned.json"
insights_baseline_path = "baseline/auto_eda_agent/output_adidas/quis_format/insights_summary.json"

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
    print("Computing IFQ Diversity Metrics...")
    print("-"*70)
    result_ifq = compute_diversity(insights_ifq)
    
    print(f"IFQ Results:")
    print(f"  - Semantic Diversity: {result_ifq['semantic_diversity']:.3f}")
    print(f"  - Avg Similarity: {result_ifq['avg_similarity']:.3f}")
    print(f"  - Num Insights: {result_ifq['num_insights']}")
    print(f"  - Subspace Diversity: {result_ifq['subspace_diversity']}")
    print(f"  - Value Diversity: {result_ifq['value_diversity']}")
    print(f"  - Dedup Rate: {result_ifq['dedup_rate']:.3f}")
    print(f"  - Unique Insights: {result_ifq['unique_count']}/{result_ifq['total_count']}")
    
    # Compute diversity for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Diversity Metrics...")
    print("-"*70)
    result_baseline = compute_diversity(insights_baseline)
    
    print(f"Baseline Results:")
    print(f"  - Semantic Diversity: {result_baseline['semantic_diversity']:.3f}")
    print(f"  - Avg Similarity: {result_baseline['avg_similarity']:.3f}")
    print(f"  - Num Insights: {result_baseline['num_insights']}")
    print(f"  - Subspace Diversity: {result_baseline['subspace_diversity']}")
    print(f"  - Value Diversity: {result_baseline['value_diversity']}")
    print(f"  - Dedup Rate: {result_baseline['dedup_rate']:.3f}")
    print(f"  - Unique Insights: {result_baseline['unique_count']}/{result_baseline['total_count']}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"IFQ Semantic Diversity: {result_ifq['semantic_diversity']:.3f}")
    print(f"Baseline Semantic Diversity: {result_baseline['semantic_diversity']:.3f}")
    
    if result_ifq['semantic_diversity'] > result_baseline['semantic_diversity']:
        winner = "IFQ"
        diff = result_ifq['semantic_diversity'] - result_baseline['semantic_diversity']
    else:
        winner = "Baseline"
        diff = result_baseline['semantic_diversity'] - result_ifq['semantic_diversity']
    
    print(f"Semantic Diversity Winner: {winner} (by {diff:.3f})")
    
    # Compare dedup rate (lower is better)
    print(f"\nIFQ Dedup Rate: {result_ifq['dedup_rate']:.3f}")
    print(f"Baseline Dedup Rate: {result_baseline['dedup_rate']:.3f}")
    
    if result_ifq['dedup_rate'] < result_baseline['dedup_rate']:
        dedup_winner = "IFQ"
        dedup_diff = result_baseline['dedup_rate'] - result_ifq['dedup_rate']
    else:
        dedup_winner = "Baseline"
        dedup_diff = result_ifq['dedup_rate'] - result_baseline['dedup_rate']
    
    print(f"Dedup Rate Winner: {dedup_winner} (lower by {dedup_diff:.3f})")
    
    # Subspace diversity comparison (if both have subspace)
    if result_ifq['subspace_diversity'] and result_baseline['subspace_diversity']:
        print(f"\nIFQ Subspace Entropy: {result_ifq['subspace_diversity']['subspace_diversity_entropy']:.3f}")
        print(f"Baseline Subspace Entropy: {result_baseline['subspace_diversity']['subspace_diversity_entropy']:.3f}")
        
        if result_ifq['subspace_diversity']['subspace_diversity_entropy'] > result_baseline['subspace_diversity']['subspace_diversity_entropy']:
            sub_winner = "IFQ"
        else:
            sub_winner = "Baseline"
        
        print(f"Subspace Diversity Winner: {sub_winner}")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
