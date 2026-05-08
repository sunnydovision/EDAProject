#!/usr/bin/env python3
"""
ONLYSTATS ablation: replace QuGen with Kruskal-Wallis based (B, M) pair selection.

As described in the paper: "First, a random B is sampled from the list of all eligible 
columns of the table. This is followed by computing the Kruskal-Wallis test of association 
between breakdown B and all possible measures M in the table. The top 20 pairs of (B, M), 
ranked according to the strength of association measured by the Kruskal-Wallis test are 
selected as input to ISGEN."

Usage:
  python run_onlystats.py \\
    --csv data/adidas_cleaned.csv \\
    --profile baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json \\
    --suffix v7
Outputs: onlystats_results/onlystats_{yyyymmdd_hhiiss}_{dataset}_{suffix}/insights_summary.json,
         timing.json, usage.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import kruskal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from quis.shared.data_loader import load_data
from quis.isgen.pipeline import ISGENPipeline, ISGENConfig
from quis.configs.isgen_config import DEFAULT_ISGEN_CONFIG

_CATEGORICAL_CLASSES = {"Categorical"}
_TEMPORAL_CLASSES = {"Temporal"}
_NUMERICAL_CLASSES = {"Numerical"}
_AGGREGATIONS = ["SUM", "MEAN", "COUNT", "MAX", "MIN"]


def create_output_dir(csv_path: str, suffix: str, base_dir: str = "onlystats_results") -> Path:
    """Create timestamped output directory: {base_dir}/onlystats_{yyyymmdd_hhiiss}_{dataset}_{suffix}"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_name = Path(csv_path).stem
    dir_name = f"onlystats_{timestamp}_{dataset_name}_{suffix}"
    output_dir = Path(base_dir) / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_timing_json(output_dir: Path, total_time: float, insights_generated: int, 
                     system: str = "onlystats") -> Path:
    """Save timing.json in format compatible with evaluation/metrics/time_to_insight.py"""
    throughput = insights_generated / total_time if total_time > 0 else 0
    
    timing_data = {
        system: {
            "total_time_seconds": total_time,
            "insights_generated": insights_generated,
            "throughput_insights_per_second": throughput,
            "step_times": {
                "card_generation": 0,  # ONLYSTATS doesn't have separate card generation step
                "isgen": total_time
            }
        }
    }
    
    timing_path = output_dir / "timing.json"
    with open(timing_path, 'w', encoding='utf-8') as f:
        json.dump(timing_data, f, indent=2)
    return timing_path


def save_usage_json(output_dir: Path, system: str = "onlystats") -> Path:
    """Save usage.json in format compatible with evaluation/metrics/token_usage.py"""
    # ONLYSTATS doesn't use LLM, so token usage is 0
    usage_data = {
        system: {
            "total": {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "requests": 0,
                "model": "none"
            }
        }
    }
    
    usage_path = output_dir / "usage.json"
    with open(usage_path, 'w', encoding='utf-8') as f:
        json.dump(usage_data, f, indent=2)
    return usage_path


def _effective_data_type_class(col_name: str, info: dict) -> str:
    """Resolve data_type_class, with heuristics when baseline profile has no LLM semantic labels."""
    cls = (info.get("data_type_class") or "").strip()
    if cls:
        return cls
    dtype = str(info.get("dtype", "")).lower()
    if dtype in ("bool", "object", "category"):
        return "Categorical"
    if info.get("top_values"):
        return "Categorical"
    lc = col_name.lower()
    if ("date" in lc or "month" in lc or "year" in lc) and (
        dtype == "object" or "datetime" in dtype
    ):
        return "Temporal"
    if info.get("statistics") is not None and dtype not in ("bool", "object"):
        return "Numerical"
    return ""


def generate_cards_from_profile(df, profile_path: str, top_k_per_breakdown: int = 20) -> list[dict]:
    """
    Generate (B, M) pairs using Kruskal-Wallis test.
    
    Steps:
    1. Compute Kruskal-Wallis test between all breakdowns B and all measures M
    2. Select top K pairs per breakdown ranked by Kruskal-Wallis strength
    
    Breakdowns: Categorical + Temporal columns (ID excluded — not meaningful as grouping dim).
    Measures: SUM, MEAN, COUNT, MAX, MIN over all Numerical columns.
    """
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    col_info = profile.get("columns", {})
    breakdowns: list[str] = []
    numerical_cols: list[str] = []

    for col_name, info in col_info.items():
        cls = _effective_data_type_class(col_name, info)
        if col_name not in df.columns:
            continue
        if cls in _CATEGORICAL_CLASSES or cls in _TEMPORAL_CLASSES:
            breakdowns.append(col_name)
        elif cls in _NUMERICAL_CLASSES:
            numerical_cols.append(col_name)

    print(f"Eligible columns: {len(breakdowns)} breakdowns, {len(numerical_cols)} numerical measures")
    print(f"  Breakdowns : {breakdowns}")
    print(f"  Measures   : {numerical_cols}")

    # Compute Kruskal-Wallis test for all (B, M) pairs
    pair_scores: list[tuple[str, str, float]] = []  # (breakdown, measure, score)
    
    for b_col in breakdowns:
        for m_col in numerical_cols:
            for agg in _AGGREGATIONS:
                measure_expr = f"{agg}({m_col})"
                
                try:
                    # Prepare data for Kruskal-Wallis test
                    # For Kruskal-Wallis, we need the actual measure values grouped by breakdown
                    groups = []
                    for group_name, group_df in df.groupby(b_col, dropna=False):
                        # Get the actual measure values for this group
                        values = group_df[m_col].dropna().values
                        if len(values) > 0:
                            groups.append(values)
                    
                    if len(groups) >= 2:  # Need at least 2 groups for Kruskal-Wallis
                        # Compute Kruskal-Wallis test statistic
                        statistic, p_value = kruskal(*groups)
                        pair_scores.append((b_col, measure_expr, statistic))
                except Exception as e:
                    print(f"Warning: Failed to compute Kruskal-Wallis for ({b_col}, {measure_expr}): {e}")
                    continue

    if not pair_scores:
        raise ValueError("No valid (B, M) pairs computed")

    # Group by breakdown and select top K per breakdown
    pairs_by_breakdown: dict[str, list[tuple]] = {}
    for b, m, score in pair_scores:
        if b not in pairs_by_breakdown:
            pairs_by_breakdown[b] = []
        pairs_by_breakdown[b].append((b, m, score))

    # Sort pairs within each breakdown by score and select top K
    top_pairs: list[tuple] = []
    for b in pairs_by_breakdown:
        pairs_by_breakdown[b].sort(key=lambda x: x[2], reverse=True)
        top_pairs.extend(pairs_by_breakdown[b][:top_k_per_breakdown])

    # Generate cards from top pairs
    cards: list[dict] = []
    for b, m, score in top_pairs:
        cards.append({
            "question": f"How does {m} vary by {b}?",
            "reason": f"Statistics-based analysis (Kruskal-Wallis score={score:.3f}): {m} grouped by {b}.",
            "breakdown": b,
            "measure": m,
        })

    print(f"Generated {len(cards)} insight cards (top {top_k_per_breakdown} per breakdown from {len(pairs_by_breakdown)} breakdowns)")
    print(f"  Total breakdowns: {len(pairs_by_breakdown)}")
    print(f"  Total pairs computed: {len(pair_scores)}")
    for b in pairs_by_breakdown:
        print(f"  {b}: {len(pairs_by_breakdown[b])} pairs (selected top {min(top_k_per_breakdown, len(pairs_by_breakdown[b]))})")
    
    return cards


def main():
    parser = argparse.ArgumentParser(
        description="ONLYSTATS ablation: Kruskal-Wallis based (B,M) selection → IsGen"
    )
    parser.add_argument("--csv", required=True, help="Path to CSV dataset")
    parser.add_argument("--profile", required=True, help="Path to profile.json (column classifications)")
    parser.add_argument("--suffix", default="v7", help="Output directory suffix, e.g. v7")
    parser.add_argument("--top-k-per-breakdown", type=int, default=20, help="Number of top (B, M) pairs to select per breakdown")
    parser.add_argument("--plot-dir", default=None, help="Directory to save plots")
    parser.add_argument("--beam-width", type=int, default=100)
    parser.add_argument("--exp-factor", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--no-subspace", action="store_true", help="Skip subspace search")
    parser.add_argument("--max-overall-per-key", type=int, default=DEFAULT_ISGEN_CONFIG.max_overall_per_key)
    parser.add_argument("--max-subspace-per-key", type=int, default=DEFAULT_ISGEN_CONFIG.max_subspace_per_key)
    parser.add_argument("--max-insights-per-question", type=int, default=DEFAULT_ISGEN_CONFIG.max_insights_per_question)
    args = parser.parse_args()

    if not os.path.isfile(args.csv):
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.profile):
        print(f"Profile not found: {args.profile}", file=sys.stderr)
        sys.exit(1)

    # Create timestamped output directory
    output_dir = create_output_dir(args.csv, args.suffix)
    print(f"Output directory: {output_dir}")

    df = load_data(args.csv)
    cards = generate_cards_from_profile(df, args.profile, top_k_per_breakdown=args.top_k_per_breakdown)

    # Save insight cards
    cards_path = output_dir / "insight_cards.json"
    with open(cards_path, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(cards)} cards → {cards_path.name}")

    config = ISGENConfig(
        beam_width=args.beam_width,
        exp_factor=args.exp_factor,
        max_depth=args.max_depth,
        run_subspace_search=not args.no_subspace,
        max_overall_per_key=args.max_overall_per_key,
        max_subspace_per_key=args.max_subspace_per_key,
        max_insights_per_question=args.max_insights_per_question,
    )

    if config.run_subspace_search and not os.getenv("OPENAI_API_KEY") and not os.getenv("OPENAI_API_BASE"):
        parser.error("OPENAI_API_KEY (or OPENAI_API_BASE) required for subspace search.")

    llm = None
    if config.run_subspace_search:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "llm_client",
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "quis", "qugen", "llm_client.py")
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            llm = mod.get_default_llm_client(use_mock=False)
        except Exception as e:
            print(f"Warning: LLM client unavailable ({e}), running subspace search without LLM guidance.")

    t0 = time.perf_counter()
    pipeline = ISGENPipeline(config=config, llm_client=llm)
    summary = pipeline.run(df, cards, output_dir=args.plot_dir)
    t1 = time.perf_counter()
    total_time = t1 - t0

    # Save insights summary
    summary_path = output_dir / "insights_summary.json"
    out_data = [
        {
            "question": s.get("question", ""),
            "explanation": s.get("explanation", ""),
            "plot_path": s.get("plot_path"),
            "insight": s.get("insight", {}),
        }
        for s in summary
    ]
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(out_data)} insights → {summary_path.name}")

    # Save timing.json in evaluation-compatible format
    timing_path = save_timing_json(output_dir, total_time, len(out_data), system="onlystats")
    print(f"Saved timing: {timing_path.name}")

    # Save usage.json in evaluation-compatible format
    usage_path = save_usage_json(output_dir, system="onlystats")
    print(f"Saved usage: {usage_path.name}")

    print(f"\n{'='*70}")
    print("ONLYSTATS Pipeline Summary")
    print(f"{'='*70}")
    print(f"CSV: {args.csv}")
    print(f"Profile: {args.profile}")
    print(f"\nWall-clock seconds: {total_time:.3f}")
    print(f"\nInsights generated: {len(out_data)}")
    print(f"\nOutputs:")
    print(f"  {cards_path.name}")
    print(f"  {summary_path.name}")
    print(f"  {timing_path.name}")
    print(f"  {usage_path.name}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
