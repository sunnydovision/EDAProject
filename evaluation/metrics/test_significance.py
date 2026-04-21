"""
Test script for significance.py - compares IFQ vs Baseline
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from metrics.data_loader import load_and_clean_data
from metrics.significance import compute_significance
import json

# Test significance
print("Testing significance.py - IFQ vs Baseline")
print("="*70)

csv_path = "../../data/Adidas_cleaned.csv"
insights_ifq_path = "../../insights_summary_adidas_adidas_v3.json"
insights_baseline_path = "../../baseline/auto_eda_agent/output_adidas/ifq_format/insights_summary.json"

print(f"Loading data from: {csv_path}")

try:
    df_raw, df_cleaned = load_and_clean_data(csv_path)
    print(f"Data loaded: {len(df_raw)} rows, {len(df_cleaned)} columns")
    
    # Load IFQ insights
    print(f"\nLoading IFQ insights from: {insights_ifq_path}")
    with open(insights_ifq_path, 'r', encoding='utf-8') as f:
        insights_ifq = json.load(f)
    print(f"IFQ insights loaded: {len(insights_ifq)} insights")
    
    # Load Baseline insights
    print(f"Loading Baseline insights from: {insights_baseline_path}")
    with open(insights_baseline_path, 'r', encoding='utf-8') as f:
        insights_baseline = json.load(f)
    print(f"Baseline insights loaded: {len(insights_baseline)} insights")
    
    # Compute significance for IFQ
    print("\n" + "-"*70)
    print("Computing IFQ Significance...")
    print("-"*70)
    result_ifq = compute_significance(insights_ifq, df_cleaned, csv_path)
    
    print(f"IFQ Results:")
    print(f"  - Significant rate: {result_ifq['significant_rate']*100:.1f}%")
    print(f"  - Significant count: {result_ifq['significant_count']}")
    print(f"  - Total evaluated: {result_ifq['total_evaluated']}")
    print(f"  - Avg effect size: {result_ifq['avg_effect_size']:.4f}")
    if 'by_pattern' in result_ifq:
        print(f"  - By pattern:")
        for pattern, stats in result_ifq['by_pattern'].items():
            print(f"    {pattern}: {stats['significant_rate']*100:.1f}% ({stats['significant_count']}/{stats['total_count']})")
    
    # Compute significance for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Significance...")
    print("-"*70)
    result_baseline = compute_significance(insights_baseline, df_cleaned, csv_path)
    
    print(f"Baseline Results:")
    print(f"  - Significant rate: {result_baseline['significant_rate']*100:.1f}%")
    print(f"  - Significant count: {result_baseline['significant_count']}")
    print(f"  - Total evaluated: {result_baseline['total_evaluated']}")
    print(f"  - Avg effect size: {result_baseline['avg_effect_size']:.4f}")
    if 'by_pattern' in result_baseline:
        print(f"  - By pattern:")
        for pattern, stats in result_baseline['by_pattern'].items():
            print(f"    {pattern}: {stats['significant_rate']*100:.1f}% ({stats['significant_count']}/{stats['total_count']})")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"IFQ Significance Rate: {result_ifq['significant_rate']*100:.1f}%")
    print(f"Baseline Significance Rate: {result_baseline['significant_rate']*100:.1f}%")
    
    if result_ifq['significant_rate'] > result_baseline['significant_rate']:
        winner = "IFQ"
        diff = result_ifq['significant_rate'] - result_baseline['significant_rate']
    else:
        winner = "Baseline"
        diff = result_baseline['significant_rate'] - result_ifq['significant_rate']
    
    print(f"Winner: {winner} (by {diff*100:.1f}%)")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
