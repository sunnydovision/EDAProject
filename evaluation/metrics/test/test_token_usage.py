"""
Test script for token_usage.py - compares QUIS vs Baseline

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_token_usage.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.token_usage import compute_token_usage
from evaluation.configs.test_config import TOKEN_FILE
import json

# Test token usage
print("Testing token_usage.py - QUIS vs Baseline")
print("="*70)

token_file = TOKEN_FILE

print(f"Loading token data from: {token_file}")

try:
    # Compute token usage metrics
    print("\n" + "-"*70)
    print("Computing Token Usage Metrics...")
    print("-"*70)
    
    result_baseline = compute_token_usage(token_file, "baseline")
    result_ifq = compute_token_usage(token_file, "quis")
    
    print(f"\nBaseline Results:")
    print(f"  - Total tokens: {result_baseline['total_tokens']}")
    print(f"  - Input tokens: {result_baseline['input_tokens']}")
    print(f"  - Output tokens: {result_baseline['output_tokens']}")
    print(f"  - Requests: {result_baseline['requests']}")
    print(f"  - Insights generated: {result_baseline['insights_generated']}")
    print(f"  - Tokens per insight: {result_baseline['tokens_per_insight']:.2f}")
    print(f"  - Model: {result_baseline['model']}")
    
    print(f"\nQUIS Results:")
    print(f"  - Total tokens: {result_ifq['total_tokens']}")
    print(f"  - Input tokens: {result_ifq['input_tokens']}")
    print(f"  - Output tokens: {result_ifq['output_tokens']}")
    print(f"  - Requests: {result_ifq['requests']}")
    print(f"  - Insights generated: {result_ifq['insights_generated']}")
    print(f"  - Tokens per insight: {result_ifq['tokens_per_insight']:.2f}")
    print(f"  - Model: {result_ifq['model']}")
    
    print(f"\nComparison:")
    efficiency_ratio = result_ifq['total_tokens'] / result_baseline['total_tokens'] if result_baseline['total_tokens'] > 0 else 0
    print(f"  - QUIS is {efficiency_ratio:.2f}x more efficient than Baseline")
    print(f"  - Baseline uses {result_baseline['total_tokens'] / result_ifq['total_tokens'] * 100:.1f}% of QUIS tokens")
    print(f"  - Baseline tokens per insight ratio: {result_baseline['tokens_per_insight'] / result_ifq['tokens_per_insight']:.2f}x QUIS")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
