"""
Test script for breakdown_measure.py — compares QUIS vs Baseline
on NMI and Interestingness metrics.

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_breakdown_measure.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
from evaluation.metrics.data_loader import load_and_clean_data
from evaluation.metrics.breakdown_measure import compute_bm_quality
from evaluation.configs.test_config import (
    DATA_PATH,
    QUIS_INSIGHTS_PATH,
    BASELINE_INSIGHTS_PATH
)

print("BM Quality (NMI + Interestingness) — QUIS vs Baseline")
print("=" * 70)

CSV_PATH      = DATA_PATH
IFQ_PATH      = QUIS_INSIGHTS_PATH
BASELINE_PATH = BASELINE_INSIGHTS_PATH

_, df = load_and_clean_data(CSV_PATH)
print(f"Data: {len(df)} rows, {len(df.columns)} columns\n")

with open(IFQ_PATH, encoding='utf-8') as f:
    insights_ifq = json.load(f)
with open(BASELINE_PATH, encoding='utf-8') as f:
    insights_baseline = json.load(f)

print(f"QUIS insights     : {len(insights_ifq)}")
print(f"Baseline insights: {len(insights_baseline)}")


def print_result(name: str, r: dict):
    print(f"\n{name} Results:")
    print(f"  nmi_mean        : {r['nmi_mean']:.4f}")
    print(f"  int_mean        : {r['int_mean']:.4f}")
    print(f"  actionability   : {r['actionability']:.4f}  ({r['total_categorical']}/{r['total_evaluated']} pairs have categorical B)")
    print(f"  bm_diversity    : {r['bm_diversity']:.4f}  ({r['total_evaluated']} unique pairs / {r['total_insights']} insights)")

    cat_pairs = [p for p in r['pairs'] if p['categorical_b']]
    num_pairs = [p for p in r['pairs'] if not p['categorical_b']]

    by_nmi = sorted([p for p in cat_pairs if p['nmi'] is not None], key=lambda x: -x['nmi'])
    by_int = sorted([p for p in cat_pairs if p['interestingness'] is not None], key=lambda x: -x['interestingness'])

    print(f"\n  Top 5 by NMI (categorical B only):")
    for p in by_nmi[:5]:
        print(f"    {p['breakdown']} / {p['agg']}({p['col']})"
              f"  NMI={p['nmi']:.4f}  Int={p['interestingness']:.4f}")

    print(f"\n  Top 5 by Interestingness (categorical B only):")
    for p in by_int[:5]:
        print(f"    {p['breakdown']} / {p['agg']}({p['col']})"
              f"  NMI={p['nmi']:.4f}  Int={p['interestingness']:.4f}")

    if num_pairs:
        print(f"\n  Non-categorical B pairs (excluded from NMI/Int):")
        for p in num_pairs[:5]:
            print(f"    [numeric] {p['breakdown']} / {p['agg']}({p['col']})")


print("\n" + "-" * 70)
print("Computing QUIS BM Quality...")
print("-" * 70)
r_ifq = compute_bm_quality(insights_ifq, df)
print_result("QUIS", r_ifq)

print("\n" + "-" * 70)
print("Computing Baseline BM Quality...")
print("-" * 70)
r_bas = compute_bm_quality(insights_baseline, df)
print_result("Baseline", r_bas)


# ── Comparison ───────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("COMPARISON")
print("=" * 70)

def winner(a, b):
    if a > b:   return "QUIS"
    elif b > a: return "Baseline"
    else:       return "Tie"

rows = [
    ("NMI mean (cat-B only)",      r_ifq['nmi_mean'],        r_bas['nmi_mean']),
    ("Interestingness (cat-B only)",r_ifq['int_mean'],        r_bas['int_mean']),
    ("Actionability",               r_ifq['actionability'],   r_bas['actionability']),
    ("BM Diversity",                r_ifq['bm_diversity'],    r_bas['bm_diversity']),
    ("# categorical pairs",         r_ifq['total_categorical'],r_bas['total_categorical']),
    ("# unique pairs",              r_ifq['total_evaluated'], r_bas['total_evaluated']),
]

print(f"{'Metric':<32} {'QUIS':>10} {'Baseline':>10} {'Winner':>10}")
print("-" * 66)
for label, a, b in rows:
    print(f"  {label:<30} {a:>10.4f} {b:>10.4f} {winner(a, b):>10}")

print("-" * 66)
print(f"\nActionability winner  : {winner(r_ifq['actionability'], r_bas['actionability'])}")
print(f"BM Diversity winner   : {winner(r_ifq['bm_diversity'], r_bas['bm_diversity'])}")
print(f"NMI winner            : {winner(r_ifq['nmi_mean'], r_bas['nmi_mean'])}")
print(f"Interestingness winner: {winner(r_ifq['int_mean'], r_bas['int_mean'])}")

print("\n" + "=" * 70)
print("Test PASSED!")
