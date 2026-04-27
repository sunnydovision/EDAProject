"""
Test script for time_to_insight.py - compares QUIS vs Baseline

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_time_to_insight.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.time_to_insight import compute_time_to_insight
from evaluation.configs.test_config import (
    TIMING_FILE,
    QUIS_INSIGHTS_PATH
)
import json

# Test time to insight
print("Testing time_to_insight.py - QUIS vs Baseline")
print("="*70)

timing_file = TIMING_FILE

print(f"Loading timing data from: {timing_file}")

try:
    # Load QUIS insights count for comparison
    insights_ifq_path = QUIS_INSIGHTS_PATH
    with open(insights_ifq_path, 'r', encoding='utf-8') as f:
        insights_ifq = json.load(f)
    print(f"QUIS insights: {len(insights_ifq)} insights")
    
    # Compute time to insight metrics
    print("\n" + "-"*70)
    print("Computing Time to Insight Metrics...")
    print("-"*70)
    
    result_baseline = compute_time_to_insight(timing_file, "baseline")
    result_ifq = compute_time_to_insight(timing_file, "quis")
    
    print(f"\nBaseline Results:")
    print(f"  - Total time: {result_baseline['total_time_seconds']:.2f} seconds")
    print(f"  - Insights generated: {result_baseline['insights_generated']}")
    print(f"  - Time per insight: {result_baseline['time_per_insight_seconds']:.2f} seconds")
    print(f"  - Throughput: {result_baseline['throughput_insights_per_second']:.3f} insights/second")
    
    print(f"\nQUIS Results:")
    print(f"  - Total time: {result_ifq['total_time_seconds']:.2f} seconds")
    print(f"  - Insights generated: {result_ifq['insights_generated']}")
    print(f"  - Time per insight: {result_ifq['time_per_insight_seconds']:.2f} seconds")
    print(f"  - Throughput: {result_ifq['throughput_insights_per_second']:.3f} insights/second")
    
    print(f"\nComparison:")
    time_ratio = result_ifq['total_time_seconds'] / result_baseline['total_time_seconds'] if result_baseline['total_time_seconds'] > 0 else 0
    print(f"  - Baseline is {time_ratio:.2f}x faster than QUIS")
    print(f"  - Baseline takes {result_baseline['total_time_seconds'] / result_ifq['total_time_seconds'] * 100:.1f}% of QUIS time")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
