"""
Test script for time_to_insight.py - compares IFQ vs Baseline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from time_to_insight import compute_time_to_insight
import json

# Test time to insight
print("Testing time_to_insight.py - IFQ vs Baseline")
print("="*70)

timing_file = "timing.json"

print(f"Loading timing data from: {timing_file}")

try:
    # Load IFQ insights count for comparison
    insights_ifq_path = "../insights_summary_adidas_cleaned.json"
    with open(insights_ifq_path, 'r', encoding='utf-8') as f:
        insights_ifq = json.load(f)
    print(f"IFQ insights: {len(insights_ifq)} insights")
    
    # Compute time to insight metrics
    print("\n" + "-"*70)
    print("Computing Time to Insight Metrics...")
    print("-"*70)
    
    result_baseline = compute_time_to_insight(timing_file, "baseline")
    result_ifq = compute_time_to_insight(timing_file, "ifq")
    
    print(f"\nBaseline Results:")
    print(f"  - Total time: {result_baseline['total_time_seconds']:.2f} seconds")
    print(f"  - Insights generated: {result_baseline['insights_generated']}")
    print(f"  - Time per insight: {result_baseline['time_per_insight_seconds']:.2f} seconds")
    print(f"  - Throughput: {result_baseline['throughput_insights_per_second']:.3f} insights/second")
    
    print(f"\nIFQ Results:")
    print(f"  - Total time: {result_ifq['total_time_seconds']:.2f} seconds")
    print(f"  - Insights generated: {result_ifq['insights_generated']}")
    print(f"  - Time per insight: {result_ifq['time_per_insight_seconds']:.2f} seconds")
    print(f"  - Throughput: {result_ifq['throughput_insights_per_second']:.3f} insights/second")
    
    print(f"\nComparison:")
    time_ratio = result_ifq['total_time_seconds'] / result_baseline['total_time_seconds'] if result_baseline['total_time_seconds'] > 0 else 0
    print(f"  - Baseline is {time_ratio:.2f}x faster than IFQ")
    print(f"  - Baseline takes {result_baseline['total_time_seconds'] / result_ifq['total_time_seconds'] * 100:.1f}% of IFQ time")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
