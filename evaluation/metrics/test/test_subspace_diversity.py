"""
Test script for subspace diversity - compares QUIS vs Baseline
Only includes insights that have subspace for fair comparison

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_subspace_diversity.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.diversity import compute_subspace_diversity, compute_value_diversity, compute_dedup_rate, compute_semantic_diversity
from evaluation.configs.test_config import (
    QUIS_INSIGHTS_PATH,
    BASELINE_INSIGHTS_PATH
)
import json

# Test subspace diversity
print("Testing Subspace Diversity - QUIS vs Baseline (insights with subspace only)")
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
    
    # Filter to only insights with subspace
    ifq_with_subspace = [ins for ins in insights_ifq if ins.get('insight', {}).get('subspace')]
    baseline_with_subspace = [ins for ins in insights_baseline if ins.get('insight', {}).get('subspace')]
    
    print(f"\nQUIS insights with subspace: {len(ifq_with_subspace)}/{len(insights_ifq)}")
    print(f"Baseline insights with subspace: {len(baseline_with_subspace)}/{len(insights_baseline)}")
    
    if len(ifq_with_subspace) == 0 or len(baseline_with_subspace) == 0:
        print("\nNo insights with subspace to compare. Test SKIPPED.")
        sys.exit(0)
    
    # Compute semantic diversity for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Semantic Diversity...")
    print("-"*70)
    ifq_semantic_result = compute_semantic_diversity(ifq_with_subspace)
    
    print(f"QUIS Semantic Results:")
    print(f"  - Semantic Diversity: {ifq_semantic_result['semantic_diversity']:.3f}")
    print(f"  - Avg Similarity: {ifq_semantic_result['avg_similarity']:.3f}")
    print(f"  - Num Insights: {ifq_semantic_result['num_insights']}")
    
    # Compute semantic diversity for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Semantic Diversity...")
    print("-"*70)
    baseline_semantic_result = compute_semantic_diversity(baseline_with_subspace)
    
    print(f"Baseline Semantic Results:")
    print(f"  - Semantic Diversity: {baseline_semantic_result['semantic_diversity']:.3f}")
    print(f"  - Avg Similarity: {baseline_semantic_result['avg_similarity']:.3f}")
    print(f"  - Num Insights: {baseline_semantic_result['num_insights']}")
    
    # Compute subspace diversity for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Subspace Diversity...")
    print("-"*70)
    ifq_subspace_result = compute_subspace_diversity(ifq_with_subspace)
    
    if ifq_subspace_result:
        print(f"QUIS Subspace Results:")
        print(f"  - Entropy: {ifq_subspace_result['subspace_diversity_entropy']:.3f}")
        print(f"  - Count Ratio: {ifq_subspace_result['subspace_diversity_count_ratio']:.3f}")
        print(f"  - Unique Columns: {ifq_subspace_result['unique_columns']}")
        print(f"  - Total Columns: {ifq_subspace_result['total_columns']}")
        print(f"  - Column Distribution: {ifq_subspace_result['column_distribution']}")
    else:
        print(f"QUIS Subspace Diversity: None")
    
    # Compute subspace diversity for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Subspace Diversity...")
    print("-"*70)
    baseline_subspace_result = compute_subspace_diversity(baseline_with_subspace)
    
    if baseline_subspace_result:
        print(f"Baseline Subspace Results:")
        print(f"  - Entropy: {baseline_subspace_result['subspace_diversity_entropy']:.3f}")
        print(f"  - Count Ratio: {baseline_subspace_result['subspace_diversity_count_ratio']:.3f}")
        print(f"  - Unique Columns: {baseline_subspace_result['unique_columns']}")
        print(f"  - Total Columns: {baseline_subspace_result['total_columns']}")
        print(f"  - Column Distribution: {baseline_subspace_result['column_distribution']}")
    else:
        print(f"Baseline Subspace Diversity: None")
    
    # Compute value diversity for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Value Diversity...")
    print("-"*70)
    ifq_value_result = compute_value_diversity(ifq_with_subspace)
    
    if ifq_value_result:
        print(f"QUIS Value Results:")
        print(f"  - Diversity: {ifq_value_result['value_diversity']:.3f}")
        print(f"  - Unique Pairs: {ifq_value_result['unique_pairs']}")
        print(f"  - Total Pairs: {ifq_value_result['total_pairs']}")
    else:
        print(f"QUIS Value Diversity: None")
    
    # Compute value diversity for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Value Diversity...")
    print("-"*70)
    baseline_value_result = compute_value_diversity(baseline_with_subspace)
    
    if baseline_value_result:
        print(f"Baseline Value Results:")
        print(f"  - Diversity: {baseline_value_result['value_diversity']:.3f}")
        print(f"  - Unique Pairs: {baseline_value_result['unique_pairs']}")
        print(f"  - Total Pairs: {baseline_value_result['total_pairs']}")
    else:
        print(f"Baseline Value Diversity: None")
    
    # Compute dedup rate for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Dedup Rate...")
    print("-"*70)
    ifq_dedup_result = compute_dedup_rate(ifq_with_subspace)
    
    print(f"QUIS Dedup Results:")
    print(f"  - Dedup Rate: {ifq_dedup_result['dedup_rate']:.3f}")
    print(f"  - Unique Insights: {ifq_dedup_result['unique_count']}/{ifq_dedup_result['total_count']}")
    print(f"  - Duplicate Count: {ifq_dedup_result['duplicate_count']}")
    
    # Compute dedup rate for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Dedup Rate...")
    print("-"*70)
    baseline_dedup_result = compute_dedup_rate(baseline_with_subspace)
    
    print(f"Baseline Dedup Results:")
    print(f"  - Dedup Rate: {baseline_dedup_result['dedup_rate']:.3f}")
    print(f"  - Unique Insights: {baseline_dedup_result['unique_count']}/{baseline_dedup_result['total_count']}")
    print(f"  - Duplicate Count: {baseline_dedup_result['duplicate_count']}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON (insights with subspace only)")
    print("="*70)
    
    # Semantic diversity comparison
    print(f"\nQUIS Semantic Diversity: {ifq_semantic_result['semantic_diversity']:.3f}")
    print(f"Baseline Semantic Diversity: {baseline_semantic_result['semantic_diversity']:.3f}")
    
    if ifq_semantic_result['semantic_diversity'] > baseline_semantic_result['semantic_diversity']:
        semantic_winner = "QUIS"
        semantic_diff = ifq_semantic_result['semantic_diversity'] - baseline_semantic_result['semantic_diversity']
    else:
        semantic_winner = "Baseline"
        semantic_diff = baseline_semantic_result['semantic_diversity'] - ifq_semantic_result['semantic_diversity']
    
    print(f"Semantic Diversity Winner: {semantic_winner} (by {semantic_diff:.3f})")
    
    if ifq_subspace_result and baseline_subspace_result:
        print(f"\nQUIS Subspace Entropy: {ifq_subspace_result['subspace_diversity_entropy']:.3f}")
        print(f"Baseline Subspace Entropy: {baseline_subspace_result['subspace_diversity_entropy']:.3f}")
        
        if ifq_subspace_result['subspace_diversity_entropy'] > baseline_subspace_result['subspace_diversity_entropy']:
            sub_winner = "QUIS"
            sub_diff = ifq_subspace_result['subspace_diversity_entropy'] - baseline_subspace_result['subspace_diversity_entropy']
        else:
            sub_winner = "Baseline"
            sub_diff = baseline_subspace_result['subspace_diversity_entropy'] - ifq_subspace_result['subspace_diversity_entropy']
        
        print(f"Subspace Entropy Winner: {sub_winner} (by {sub_diff:.3f})")
        
        print(f"\nQUIS Unique Columns: {ifq_subspace_result['unique_columns']}")
        print(f"Baseline Unique Columns: {baseline_subspace_result['unique_columns']}")
        
        print(f"\nQUIS Column Distribution:")
        for col, count in sorted(ifq_subspace_result['column_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {col}: {count}")
        
        print(f"\nBaseline Column Distribution:")
        for col, count in sorted(baseline_subspace_result['column_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {col}: {count}")
    
    if ifq_value_result and baseline_value_result:
        print(f"\nQUIS Value Diversity: {ifq_value_result['value_diversity']:.3f}")
        print(f"Baseline Value Diversity: {baseline_value_result['value_diversity']:.3f}")
        
        if ifq_value_result['value_diversity'] > baseline_value_result['value_diversity']:
            val_winner = "QUIS"
            val_diff = ifq_value_result['value_diversity'] - baseline_value_result['value_diversity']
        else:
            val_winner = "Baseline"
            val_diff = baseline_value_result['value_diversity'] - ifq_value_result['value_diversity']
        
        print(f"Value Diversity Winner: {val_winner} (by {val_diff:.3f})")
    
    # Dedup rate comparison
    print(f"\nQUIS Dedup Rate: {ifq_dedup_result['dedup_rate']:.3f}")
    print(f"Baseline Dedup Rate: {baseline_dedup_result['dedup_rate']:.3f}")
    
    if ifq_dedup_result['dedup_rate'] < baseline_dedup_result['dedup_rate']:
        dedup_winner = "QUIS"
        dedup_diff = baseline_dedup_result['dedup_rate'] - ifq_dedup_result['dedup_rate']
    else:
        dedup_winner = "Baseline"
        dedup_diff = ifq_dedup_result['dedup_rate'] - baseline_dedup_result['dedup_rate']
    
    print(f"Dedup Rate Winner: {dedup_winner} (lower by {dedup_diff:.3f})")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
