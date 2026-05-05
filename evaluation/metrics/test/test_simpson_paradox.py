"""
Test script for simpson_paradox.py - Standalone test

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_simpson_paradox.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.data_loader import load_and_clean_data
from evaluation.metrics.simpson_paradox import compute_simpson_paradox_rate
from evaluation.configs.test_config import (
    DATA_PATH,
    QUIS_INSIGHTS_PATH,
    BASELINE_INSIGHTS_PATH,
    ONLYSTATS_INSIGHTS_PATH
)
import json

def print_separator(char='=', length=80):
    print(char * length)

def print_header(text):
    print_separator()
    print(text)
    print_separator()

def print_subheader(text):
    print_separator('-', 80)
    print(text)
    print_separator('-', 80)

def print_results(system_name, result):
    """Print Simpson's Paradox detection results."""
    print(f"\n{system_name} Results:")
    print(f"  Total insights: {result['total_insights']}")
    print(f"  Insights with subspace: {result['subspace_count']}")
    print(f"  Simpson's Paradox detected: {result['paradox_count']}")
    print(f"  Significant paradoxes: {result['significant_paradox_count']} ({result['significant_paradox_count']/result['paradox_count']*100 if result['paradox_count'] > 0 else 0:.1f}% of detected)")
    print(f"  Simpson's Paradox Rate: {result['simpson_paradox_rate']:.1%}")
    print(f"  Significant Paradox Rate: {result['significant_paradox_rate']:.1%}")
    
    if result['by_pattern']:
        print(f"\n  By Pattern:")
        for pattern, stats in result['by_pattern'].items():
            rate = stats['simpson_paradox_rate']
            sig_rate = stats['significant_paradox_rate']
            count = stats['paradox_count']
            sig_count = stats['significant_paradox_count']
            total = stats['subspace_count']
            print(f"    {pattern:25s}: {count:3d}/{total:3d} = {rate:6.1%} ({sig_count} significant = {sig_rate:6.1%})")
    
    if result['paradoxes']:
        # Show significant paradoxes first
        significant_paradoxes = [p for p in result['paradoxes'] if p['is_significant']]
        if significant_paradoxes:
            print(f"\n  Example SIGNIFICANT Paradoxes (showing first 3):")
            for i, paradox in enumerate(significant_paradoxes[:3]):
                print(f"\n    [{i+1}] {paradox['pattern']} ✓")
                print(f"        Breakdown: {paradox['breakdown']}")
                print(f"        Measure: {paradox['measure']}")
                print(f"        Subspace: {paradox['subspace']}")
                print(f"        {paradox['reversal_type']}")
                print(f"        Subspace size: {paradox['subspace_size']} rows")
        else:
            print(f"\n  Example Paradoxes (showing first 3 - none are statistically significant):")
            for i, paradox in enumerate(result['paradoxes'][:3]):
                print(f"\n    [{i+1}] {paradox['pattern']}")
                print(f"        Breakdown: {paradox['breakdown']}")
                print(f"        Measure: {paradox['measure']}")
                print(f"        Subspace: {paradox['subspace']}")
                print(f"        {paradox['reversal_type']}")
                print(f"        Subspace size: {paradox['subspace_size']} rows")

def main():
    print_header("Testing simpson_paradox.py - Simpson's Paradox Detection")
    
    csv_path = DATA_PATH
    print(f"\nLoading data from: {csv_path}")
    
    try:
        df_raw, df_cleaned = load_and_clean_data(csv_path)
        print(f"Data loaded: {len(df_raw)} rows, {len(df_cleaned.columns)} columns")
        print(f"Columns: {list(df_cleaned.columns)}")
        
        # Test 1: QUIS
        print_subheader("Test 1: QUIS System")
        print(f"Loading QUIS insights from: {QUIS_INSIGHTS_PATH}")
        with open(QUIS_INSIGHTS_PATH, 'r', encoding='utf-8') as f:
            insights_quis = json.load(f)
        print(f"QUIS insights loaded: {len(insights_quis)} insights")
        
        result_quis = compute_simpson_paradox_rate(insights_quis, df_cleaned)
        print_results("QUIS", result_quis)
        
        # Test 2: Baseline
        print_subheader("Test 2: LLM Baseline System")
        print(f"Loading Baseline insights from: {BASELINE_INSIGHTS_PATH}")
        with open(BASELINE_INSIGHTS_PATH, 'r', encoding='utf-8') as f:
            insights_baseline = json.load(f)
        print(f"Baseline insights loaded: {len(insights_baseline)} insights")
        
        result_baseline = compute_simpson_paradox_rate(insights_baseline, df_cleaned)
        print_results("Baseline", result_baseline)
        
        # Test 3: ONLYSTATS
        print_subheader("Test 3: ONLYSTATS System")
        print(f"Loading ONLYSTATS insights from: {ONLYSTATS_INSIGHTS_PATH}")
        with open(ONLYSTATS_INSIGHTS_PATH, 'r', encoding='utf-8') as f:
            insights_onlystats = json.load(f)
        print(f"ONLYSTATS insights loaded: {len(insights_onlystats)} insights")
        
        result_onlystats = compute_simpson_paradox_rate(insights_onlystats, df_cleaned)
        print_results("ONLYSTATS", result_onlystats)
        
        # Comparison
        print_header("COMPARISON - Simpson's Paradox Rate")
        
        systems = [
            ("QUIS", result_quis),
            ("Baseline", result_baseline),
            ("ONLYSTATS", result_onlystats)
        ]
        
        print(f"\n{'System':<15} {'Total':>8} {'Subspace':>10} {'Paradox':>10} {'Significant':>12} {'SPR':>10} {'Sig SPR':>10}")
        print_separator('-', 100)
        
        for name, result in systems:
            total = result['total_insights']
            subspace = result['subspace_count']
            paradox = result['paradox_count']
            sig_paradox = result['significant_paradox_count']
            spr = result['simpson_paradox_rate']
            sig_spr = result['significant_paradox_rate']
            print(f"{name:<15} {total:>8} {subspace:>10} {paradox:>10} {sig_paradox:>12} {spr:>9.1%} {sig_spr:>9.1%}")
        
        # Find winner
        print_separator()
        rates = [(name, result['simpson_paradox_rate']) for name, result in systems]
        rates.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nRanking by Simpson's Paradox Rate (All Detected):")
        for i, (name, rate) in enumerate(rates, 1):
            print(f"  {i}. {name}: {rate:.1%}")
        
        # Also rank by significant rate
        sig_rates = [(name, result['significant_paradox_rate']) for name, result in systems]
        sig_rates.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\nRanking by Significant Paradox Rate:")
        for i, (name, rate) in enumerate(sig_rates, 1):
            print(f"  {i}. {name}: {rate:.1%}")
        
        winner_name, winner_rate = rates[0]
        sig_winner_name, sig_winner_rate = sig_rates[0]
        print(f"\n🏆 Winner (All Paradoxes): {winner_name} with {winner_rate:.1%}")
        print(f"🏆 Winner (Significant Only): {sig_winner_name} with {sig_winner_rate:.1%}")
        
        # Key findings
        print_header("KEY FINDINGS")
        
        print(f"\n1. Simpson's Paradox Detection:")
        print(f"   - All paradoxes: {winner_name} discovers the most ({winner_rate:.1%})")
        print(f"   - Significant paradoxes: {sig_winner_name} discovers the most ({sig_winner_rate:.1%})")
        
        if result_quis['paradox_count'] > 0 or result_baseline['paradox_count'] > 0 or result_onlystats['paradox_count'] > 0:
            print(f"\n2. Total Paradoxes Found:")
            print(f"   - QUIS: {result_quis['paradox_count']} total ({result_quis['significant_paradox_count']} significant = {result_quis['significant_paradox_count']/result_quis['paradox_count']*100 if result_quis['paradox_count'] > 0 else 0:.1f}%)")
            print(f"   - Baseline: {result_baseline['paradox_count']} total ({result_baseline['significant_paradox_count']} significant = {result_baseline['significant_paradox_count']/result_baseline['paradox_count']*100 if result_baseline['paradox_count'] > 0 else 0:.1f}%)")
            print(f"   - ONLYSTATS: {result_onlystats['paradox_count']} total ({result_onlystats['significant_paradox_count']} significant = {result_onlystats['significant_paradox_count']/result_onlystats['paradox_count']*100 if result_onlystats['paradox_count'] > 0 else 0:.1f}%)")
        
        print(f"\n3. Subspace Exploration:")
        print(f"   - QUIS: {result_quis['subspace_count']}/{result_quis['total_insights']} insights have subspace")
        print(f"   - Baseline: {result_baseline['subspace_count']}/{result_baseline['total_insights']} insights have subspace")
        print(f"   - ONLYSTATS: {result_onlystats['subspace_count']}/{result_onlystats['total_insights']} insights have subspace")
        
        # Trade-off analysis
        quis_subspace_rate = result_quis['subspace_count'] / result_quis['total_insights'] if result_quis['total_insights'] > 0 else 0
        onlystats_subspace_rate = result_onlystats['subspace_count'] / result_onlystats['total_insights'] if result_onlystats['total_insights'] > 0 else 0
        
        print(f"\n4. Trade-off Analysis:")
        print(f"   - QUIS: {quis_subspace_rate:.1%} subspace rate, {result_quis['simpson_paradox_rate']:.1%} paradox rate, {result_quis['significant_paradox_rate']:.1%} significant")
        print(f"   - ONLYSTATS: {onlystats_subspace_rate:.1%} subspace rate, {result_onlystats['simpson_paradox_rate']:.1%} paradox rate, {result_onlystats['significant_paradox_rate']:.1%} significant")
        
        if quis_subspace_rate > onlystats_subspace_rate and result_quis['significant_paradox_rate'] < result_onlystats['significant_paradox_rate']:
            print(f"\n   ⚖️  Trade-off detected:")
            print(f"      QUIS explores more subspaces ({quis_subspace_rate:.1%}) but finds fewer significant paradoxes ({result_quis['significant_paradox_rate']:.1%})")
            print(f"      ONLYSTATS explores fewer subspaces ({onlystats_subspace_rate:.1%}) but finds more significant paradoxes ({result_onlystats['significant_paradox_rate']:.1%})")
            print(f"\n   📊 Quality Comparison:")
            quis_quality = result_quis['significant_paradox_count'] / result_quis['paradox_count'] * 100 if result_quis['paradox_count'] > 0 else 0
            onlystats_quality = result_onlystats['significant_paradox_count'] / result_onlystats['paradox_count'] * 100 if result_onlystats['paradox_count'] > 0 else 0
            print(f"      QUIS: {quis_quality:.1f}% of detected paradoxes are significant")
            print(f"      ONLYSTATS: {onlystats_quality:.1f}% of detected paradoxes are significant")
        
        print_separator()
        print("✅ Test PASSED!")
        print_separator()
        
    except FileNotFoundError as e:
        print(f"\n❌ Test FAILED: File not found")
        print(f"   {e}")
        print(f"\nMake sure you have run the systems first to generate insights.")
        import traceback
        traceback.print_exc()
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
