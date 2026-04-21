"""
Test script for faithfulness.py - compares IFQ vs Baseline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_loader import load_and_clean_data
from faithfulness import compute_faithfulness
import json

# Test faithfulness
print("Testing faithfulness.py - IFQ vs Baseline")
print("="*70)

csv_path = "../data/Adidas_cleaned.csv"
insights_ifq_path = "../insights_summary_adidas_2.json"
insights_baseline_path = "../baseline/auto_eda_agent/ifq_compatible_output/insights_summary.json"

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
    
    # Compute faithfulness for IFQ
    print("\n" + "-"*70)
    print("Computing IFQ Faithfulness...")
    print("-"*70)
    result_ifq = compute_faithfulness(insights_ifq, df_raw, df_cleaned, csv_path)
    
    print(f"IFQ Results:")
    print(f"  - Faithfulness: {result_ifq['faithfulness']*100:.1f}%")
    print(f"  - Verified: {result_ifq['verified_count']}/{result_ifq['total_count']}")
    print(f"  - Hallucinations: {result_ifq['hallucination_count']}")
    
    if result_ifq['_failed_insights']:
        print(f"\nIFQ Failed Insights ({len(result_ifq['_failed_insights'])}):")
        for fail in result_ifq['_failed_insights']:
            print(f"  - Insight {fail['idx']}: {fail['reason']} (pattern: {fail.get('pattern', 'N/A')})")
    
    # Compute faithfulness for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Faithfulness...")
    print("-"*70)
    result_baseline = compute_faithfulness(insights_baseline, df_raw, df_cleaned, csv_path)
    
    print(f"Baseline Results:")
    print(f"  - Faithfulness: {result_baseline['faithfulness']*100:.1f}%")
    print(f"  - Verified: {result_baseline['verified_count']}/{result_baseline['total_count']}")
    print(f"  - Hallucinations: {result_baseline['hallucination_count']}")
    
    if result_baseline['_failed_insights']:
        print(f"\nBaseline Failed Insights ({len(result_baseline['_failed_insights'])}):")
        for fail in result_baseline['_failed_insights'][:10]:  # Show first 10
            print(f"  - Insight {fail['idx']}: {fail['reason']} (pattern: {fail.get('pattern', 'N/A')})")
        if len(result_baseline['_failed_insights']) > 10:
            print(f"  ... and {len(result_baseline['_failed_insights']) - 10} more")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"IFQ Faithfulness: {result_ifq['faithfulness']*100:.1f}%")
    print(f"Baseline Faithfulness: {result_baseline['faithfulness']*100:.1f}%")
    
    if result_ifq['faithfulness'] > result_baseline['faithfulness']:
        winner = "IFQ"
        diff = result_ifq['faithfulness'] - result_baseline['faithfulness']
    else:
        winner = "Baseline"
        diff = result_baseline['faithfulness'] - result_ifq['faithfulness']
    
    print(f"Winner: {winner} (by {diff*100:.1f}%)")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
