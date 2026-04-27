"""
Main evaluation script for evaluation_v2.

Modular evaluation system with separate components for:
- Data loading and cleaning
- Individual metric computation
- Model comparison
"""

import argparse
import json
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from metrics.data_loader import load_and_clean_data
from metrics.faithfulness import compute_faithfulness
from metrics.significance import compute_significance
from metrics.novelty import compute_novelty
from metrics.diversity import compute_diversity
from metrics.time_to_insight import compute_time_to_insight
from metrics.token_usage import compute_token_usage
from metrics.subspace import compute_subspace_metrics, filter_insights_with_subspace
from metrics.score_uplift import compute_score_uplift_from_subspace
from metrics.breakdown_measure import compute_bm_quality
from metrics.question_quality import (
    compute_question_quality,
    compute_question_novelty,
)
from compare import create_comparison_table, generate_report
from plot_evaluation import plot_evaluation_results
from configs.eval_config import (
    DATA_PATH,
    PROFILE_PATH,
    QUIS_INSIGHTS_PATH,
    BASELINE_INSIGHTS_PATH,
    ONLYSTATS_INSIGHTS_PATH,
    RESULTS_DIR,
)


def load_insights(summary_path: str):
    """Load insights from insights_summary.json."""
    with open(summary_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def evaluate_system(
    system_name: str,
    summary_path: str,
    df_raw: pd.DataFrame,
    df_cleaned: pd.DataFrame,
    csv_path: str = None,
    timing_file: str = None,
    token_file: str = None,
    profile_path: str = None,
) -> dict:
    """
    Evaluate a single system across all metrics.
    
    Args:
        system_name: Name of the system
        summary_path: Path to insights_summary.json
        df_raw: Raw dataframe
        df_cleaned: Cleaned dataframe
        csv_path: Path to CSV file
        timing_file: Path to timing file (optional)
        token_file: Path to token usage file (optional)
        profile_path: Path to profile.json from LLM column profiling step.
            Adidas dataset : baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json
            Transactions   : baseline/auto_eda_agent/output_transactions/step1_profiling/profile.json
        
    Returns:
        Dictionary with all evaluation results
    """
    print(f"\n{'='*70}")
    print(f"Evaluating {system_name}")
    print(f"{'='*70}")
    
    # Load insights
    insights_data = load_insights(summary_path)
    print(f"Loaded:")
    print(f"  - {len(insights_data)} insight cards")
    
    # Extract cards for diversity computation
    cards = []
    for ins in insights_data:
        card = {
            'question': ins.get('question', ''),
            'reason': ins.get('reason', ''),
            'breakdown': ins.get('insight', {}).get('breakdown', ''),
            'measure': ins.get('insight', {}).get('measure', '')
        }
        cards.append(card)
    
    # Compute metrics
    print(f"\nComputing metrics...")
    
    # Load timing and token data
    timing_data = None
    token_data = None
    
    if timing_file:
        try:
            timing_data = compute_time_to_insight(timing_file, system_name)
        except Exception as e:
            print(f"Warning: Could not load timing data from {timing_file}: {e}")
    
    if token_file:
        try:
            token_data = compute_token_usage(token_file, system_name, timing_file)
        except Exception as e:
            print(f"Warning: Could not load token data from {token_file}: {e}")
    
    results = {
        'system': system_name,
        'num_cards': len(cards),
        'num_insights': len(insights_data),
        'score_uplift_from_subspace': compute_score_uplift_from_subspace(insights_data, df_cleaned, profile_path),
        
        # 4 CORE METRICS for Defense
        'faithfulness': compute_faithfulness(insights_data, df_raw, df_cleaned, csv_path),
        'insight_significance': compute_significance(insights_data, df_cleaned, csv_path, profile_path),
        'question_diversity': compute_diversity(insights_data),
        'bm_quality': compute_bm_quality(insights_data, df_cleaned, profile_path) if profile_path else None,

        # GROUP 3 (sub-section 3.2) — QuGen text / reason metrics.
        # Stored under the same key for backward compatibility with downstream
        # consumers that parse `results['question_quality']`.
        'question_quality': compute_question_quality(insights_data, system_name),

        # EFFICIENCY METRICS
        'time_to_insight': timing_data,
        'token_usage': token_data,
    }
    
    print(f"Metrics computed successfully\n")
    
    return results


def evaluate_comparison(
    results_a: dict,
    results_b: dict,
    insights_a: list,
    insights_b: list
) -> dict:
    """
    Compute comparative metrics between two systems.
    
    Args:
        results_a: Results for system A
        results_b: Results for system B
        insights_a: Insights from system A
        insights_b: Insights from system B
        
    Returns:
        Dictionary with novelty metrics for both systems
    """
    print(f"\n{'='*70}")
    print("Computing Comparative Metrics")
    print(f"{'='*70}\n")
    
    # Compute novelty
    print(f" Computing {results_a['system']} novelty vs {results_b['system']}...")
    novelty_a = compute_novelty(insights_a, insights_b)
    novelty_a['compared_against'] = results_b['system']
    results_a['insight_novelty'] = novelty_a

    print(f" Computing {results_b['system']} novelty vs {results_a['system']}...")
    novelty_b = compute_novelty(insights_b, insights_a)
    novelty_b['compared_against'] = results_a['system']
    results_b['insight_novelty'] = novelty_b

    # Cross-system Question Novelty (Group 3 / 3.2 — QuGen text & reason)
    print(f" Computing {results_a['system']} question novelty vs {results_b['system']}...")
    q_novelty_a = compute_question_novelty(insights_a, insights_b, system_name=results_a['system'])
    q_novelty_a['compared_against'] = results_b['system']
    results_a.setdefault('question_quality', {})['question_novelty'] = q_novelty_a

    print(f" Computing {results_b['system']} question novelty vs {results_a['system']}...")
    q_novelty_b = compute_question_novelty(insights_b, insights_a, system_name=results_b['system'])
    q_novelty_b['compared_against'] = results_a['system']
    results_b.setdefault('question_quality', {})['question_novelty'] = q_novelty_b

    return {
        'system_a': results_a,
        'system_b': results_b
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate QUIS vs Baseline (v2)')
    parser.add_argument('--system_a', type=str, required=True, help='Name of system A (e.g., QUIS)')
    parser.add_argument('--system_b', type=str, required=True, help='Name of system B (e.g., Baseline)')
    parser.add_argument('--output', type=str, default=RESULTS_DIR, help='Output directory')
    
    args = parser.parse_args()
    
    # Map system names to paths
    system_paths = {
        'QUIS': QUIS_INSIGHTS_PATH,
        'quis': QUIS_INSIGHTS_PATH,
        'Baseline': BASELINE_INSIGHTS_PATH,
        'baseline': BASELINE_INSIGHTS_PATH,
        'ONLYSTATS': ONLYSTATS_INSIGHTS_PATH,
        'onlystats': ONLYSTATS_INSIGHTS_PATH,
    }
    
    path_a = system_paths.get(args.system_a)
    path_b = system_paths.get(args.system_b)
    
    if path_a is None:
        raise ValueError(f"Unknown system A: {args.system_a}. Valid options: {list(system_paths.keys())}")
    if path_b is None:
        raise ValueError(f"Unknown system B: {args.system_b}. Valid options: {list(system_paths.keys())}")
    
    print(f"{'='*70}")
    print(f"{args.system_a} vs {args.system_b} Evaluation (v2)")
    print(f"{'='*70}\n")
    
    # Load and clean data
    print(f"Loading data: {DATA_PATH}")
    df_raw, df_cleaned = load_and_clean_data(DATA_PATH)
    print(f"  Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns")
    print(f"  Cleaned {len(df_cleaned)} rows, {len(df_cleaned.columns)} columns")
    print()
    
    # Evaluate both systems
    results_a = evaluate_system(
        system_name=args.system_a,
        summary_path=path_a,
        df_raw=df_raw,
        df_cleaned=df_cleaned,
        csv_path=DATA_PATH,
        timing_file=None,
        token_file=None,
        profile_path=PROFILE_PATH,
    )
    
    results_b = evaluate_system(
        system_name=args.system_b,
        summary_path=path_b,
        df_raw=df_raw,
        df_cleaned=df_cleaned,
        csv_path=DATA_PATH,
        timing_file=None,
        token_file=None,
        profile_path=PROFILE_PATH,
    )
    
    # Load insights for novelty computation
    insights_a = load_insights(path_a)
    insights_b = load_insights(path_b)
    
    # Compute comparative metrics (novelty)
    comparison_results = evaluate_comparison(results_a, results_b, insights_a, insights_b)
    
    # Compute subspace-specific metrics
    print(f"\n{'='*70}")
    print("Computing Subspace Metrics")
    print(f"{'='*70}\n")
    print(f" Subspace insights: {args.system_a}={len(filter_insights_with_subspace(insights_a))}, {args.system_b}={len(filter_insights_with_subspace(insights_b))}")
    subspace_results = compute_subspace_metrics(insights_a, insights_b, df_raw, df_cleaned, DATA_PATH)
    results_a['subspace_metrics'] = subspace_results['system_a']
    results_b['subspace_metrics'] = subspace_results['system_b']
    
    # Save individual results
    os.makedirs(args.output, exist_ok=True)
    
    with open(f"{args.output}/{args.system_a.lower()}_results.json", 'w') as f:
        json.dump(results_a, f, indent=2)
    print(f"Saved: {args.output}/{args.system_a.lower()}_results.json")
    
    with open(f"{args.output}/{args.system_b.lower()}_results.json", 'w') as f:
        json.dump(results_b, f, indent=2)
    print(f"Saved: {args.output}/{args.system_b.lower()}_results.json")
    
    # Generate plots
    plot_evaluation_results(results_a, results_b, args.output, args.system_a, args.system_b)
    
    # Generate comparison table
    print(f"\n{'='*70}")
    print("Generating Comparison")
    print(f"{'='*70}\n")
    
    comparison_df = create_comparison_table(results_a, results_b, args.system_a, args.system_b)
    comparison_df.to_csv(f"{args.output}/comparison_table.csv", index=False)
    print(f"Saved: {args.output}/comparison_table.csv")
    
    # Print comparison table
    print(f"\n{comparison_df.to_string(index=False)}\n")
    
    # Generate report
    generate_report(
        results_a, 
        results_b, 
        output_path=f"{args.output}/comparison_report.md",
        name_a=args.system_a,
        name_b=args.system_b
    )
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}\n")
    
    a_wins = len(comparison_df[comparison_df['Winner'] == args.system_a])
    b_wins = len(comparison_df[comparison_df['Winner'] == args.system_b])
    
    print(f"{args.system_a} Wins: {a_wins}/{len(comparison_df)} metrics")
    print(f"{args.system_b} Wins: {b_wins}/{len(comparison_df)} metrics")

    # ── GROUP 1: Core + Efficiency ─────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"GROUP 1 — Core Metrics & Efficiency")
    print(f"{'─'*70}")

    print(f"\n1. Faithfulness (Correctness):")
    print(f"  • {args.system_a}: {results_a['faithfulness']['faithfulness']*100:.1f}%")
    print(f"  • {args.system_b}: {results_b['faithfulness']['faithfulness']*100:.1f}%")

    print(f"\n2. Statistical Significance (Validity):")
    sig_a = results_a['insight_significance']
    sig_b = results_b['insight_significance']
    print(f"  Overall:                 {args.system_a}={sig_a['significant_rate']*100:.1f}%  {args.system_b}={sig_b['significant_rate']*100:.1f}%")
    bp_a = sig_a.get('by_pattern', {})
    bp_b = sig_b.get('by_pattern', {})
    for pattern in ['TREND', 'OUTSTANDING_VALUE', 'ATTRIBUTION', 'DISTRIBUTION_DIFFERENCE']:
        p_a = bp_a.get(pattern, {}).get('significant_rate', 0) or 0
        p_b = bp_b.get(pattern, {}).get('significant_rate', 0) or 0
        count_a = bp_a.get(pattern, {}).get('total_count', 0)
        count_b = bp_b.get(pattern, {}).get('total_count', 0)
        print(f"  {pattern:25} {args.system_a}={p_a*100:.1f}% ({count_a})  {args.system_b}={p_b*100:.1f}% ({count_b})")

    print(f"\n3. Insight Novelty (Usefulness):")
    print(f"  • {args.system_a}: {results_a['insight_novelty']['novelty']*100:.1f}%")
    print(f"  • {args.system_b}: {results_b['insight_novelty']['novelty']*100:.1f}%")

    print(f"\n4. Insight Diversity (Non-redundancy):")
    _div_a = results_a['question_diversity']
    _div_b = results_b['question_diversity']
    print(f"  4a. Semantic:          {args.system_a}={(_div_a.get('semantic_diversity') or 0):.3f}  {args.system_b}={(_div_b.get('semantic_diversity') or 0):.3f}")
    _se_a = (_div_a.get('subspace_diversity') or {}).get('subspace_diversity_entropy')
    _se_b = (_div_b.get('subspace_diversity') or {}).get('subspace_diversity_entropy')
    print(f"  4b. Subspace Entropy:  {args.system_a}={f'{_se_a:.3f}' if _se_a is not None else 'N/A'}  {args.system_b}={f'{_se_b:.3f}' if _se_b is not None else 'N/A'}")
    _vd_a = (_div_a.get('value_diversity') or {}).get('value_diversity')
    _vd_b = (_div_b.get('value_diversity') or {}).get('value_diversity')
    print(f"  4c. Value Diversity:   {args.system_a}={f'{_vd_a:.3f}' if _vd_a is not None else 'N/A'}  {args.system_b}={f'{_vd_b:.3f}' if _vd_b is not None else 'N/A'}")
    print(f"  4d. Dedup Rate:        {args.system_a}={(_div_a.get('dedup_rate') or 0):.3f}  {args.system_b}={(_div_b.get('dedup_rate') or 0):.3f}")

    print(f"\n5. Time to Insight (Efficiency):")
    if results_a.get('time_to_insight') and results_b.get('time_to_insight'):
        time_a = results_a['time_to_insight'].get('time_per_insight_seconds')
        time_b = results_b['time_to_insight'].get('time_per_insight_seconds')
        if time_a is not None and time_b is not None:
            print(f"  • {args.system_a}: {results_a['time_to_insight'].get('total_time_seconds', 0):.2f}s total, {time_a:.2f}s per insight")
            print(f"  • {args.system_b}: {results_b['time_to_insight'].get('total_time_seconds', 0):.2f}s total, {time_b:.2f}s per insight")
        else:
            print(f"  • Timing data not available")
    else:
        print(f"  • Timing data not available")

    print(f"\n6. Token Usage (Efficiency):")
    if results_a.get('token_usage') and results_b.get('token_usage'):
        tokens_a = results_a['token_usage'].get('tokens_per_insight')
        tokens_b = results_b['token_usage'].get('tokens_per_insight')
        if tokens_a is not None and tokens_b is not None:
            print(f"  • {args.system_a}: {results_a['token_usage'].get('total_tokens', 0)} tokens, {tokens_a:.2f} tokens per insight")
            print(f"  • {args.system_b}: {results_b['token_usage'].get('total_tokens', 0)} tokens, {tokens_b:.2f} tokens per insight")
        else:
            print(f"  • Token data not available")
    else:
        print(f"  • Token data not available")

    # ── GROUP 2: Subspace Deep-dive ────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"GROUP 2 — Subspace Deep-dive")
    print(f"{'─'*70}")

    print(f"\n7. Subspace Coverage & Quality (insights with subspace filter only):")
    sa = results_a.get('subspace_metrics', {})
    sb = results_b.get('subspace_metrics', {})
    total_a_n = results_a.get('num_insights', 1) or 1
    total_b_n = results_b.get('num_insights', 1) or 1
    print(f"  • {args.system_a}: {sa.get('total_with_subspace', 0)}/{total_a_n} subspace insights ({sa.get('total_with_subspace', 0)/total_a_n*100:.1f}%)")
    print(f"  • {args.system_b}: {sb.get('total_with_subspace', 0)}/{total_b_n} subspace insights ({sb.get('total_with_subspace', 0)/total_b_n*100:.1f}%)")
    if sa.get('faithfulness') and sb.get('faithfulness'):
        print(f"  Faithfulness:  {args.system_a}={sa['faithfulness']['faithfulness']*100:.1f}%  {args.system_b}={sb['faithfulness']['faithfulness']*100:.1f}%")
    if sa.get('significance') and sb.get('significance'):
        print(f"  Significance:  {args.system_a}={sa['significance']['significant_rate']*100:.1f}%  {args.system_b}={sb['significance']['significant_rate']*100:.1f}%")
    if sa.get('novelty') and sb.get('novelty'):
        print(f"  Novelty:       {args.system_a}={sa['novelty']['novelty']*100:.1f}%  {args.system_b}={sb['novelty']['novelty']*100:.1f}%")
    if sa.get('diversity') and sb.get('diversity'):
        _sdiv_a = sa['diversity'].get('semantic_diversity', 0) or 0
        _sdiv_b = sb['diversity'].get('semantic_diversity', 0) or 0
        print(f"  Diversity Semantic:      {args.system_a}={_sdiv_a:.3f}  {args.system_b}={_sdiv_b:.3f}")
        _sse_a = (sa['diversity'].get('subspace_diversity') or {}).get('subspace_diversity_entropy')
        _sse_b = (sb['diversity'].get('subspace_diversity') or {}).get('subspace_diversity_entropy')
        print(f"  Diversity Sub-Entropy:   {args.system_a}={f'{_sse_a:.3f}' if _sse_a is not None else 'N/A'}  {args.system_b}={f'{_sse_b:.3f}' if _sse_b is not None else 'N/A'}")
        _svd_a = (sa['diversity'].get('value_diversity') or {}).get('value_diversity')
        _svd_b = (sb['diversity'].get('value_diversity') or {}).get('value_diversity')
        print(f"  Diversity Value:         {args.system_a}={f'{_svd_a:.3f}' if _svd_a is not None else 'N/A'}  {args.system_b}={f'{_svd_b:.3f}' if _svd_b is not None else 'N/A'}")
        _sdr_a = sa['diversity'].get('dedup_rate', 0) or 0
        _sdr_b = sb['diversity'].get('dedup_rate', 0) or 0
        print(f"  Diversity Dedup Rate:    {args.system_a}={_sdr_a:.3f}  {args.system_b}={_sdr_b:.3f}")

    print(f"\n8. Score Uplift from Subspace:")
    up_a = results_a.get('score_uplift_from_subspace', {})
    up_b = results_b.get('score_uplift_from_subspace', {})
    print(
        f"  • {args.system_a}: with={up_a.get('mean_score_with_subspace')} "
        f"without={up_a.get('mean_score_without_subspace')} "
        f"uplift={up_a.get('score_uplift_abs')} ratio={up_a.get('score_uplift_ratio')}"
    )
    print(
        f"  • {args.system_b}: with={up_b.get('mean_score_with_subspace')} "
        f"without={up_b.get('mean_score_without_subspace')} "
        f"uplift={up_b.get('score_uplift_abs')} ratio={up_b.get('score_uplift_ratio')}"
    )

    print(f"\n9. Direction Uplift:")
    print(f"  • {args.system_a}: direction={up_a.get('score_uplift_direction')}")
    print(f"  • {args.system_b}: direction={up_b.get('score_uplift_direction')}")

    # ── GROUP 3: Intent Layer Quality ─────────────────────────────
    # Merged group: BM target structure (10a-e) + Question text/reason (11a-e).
    # Both probe the same QuGen module, separated only for readability.
    print(f"\n{'─'*70}")
    print(f"GROUP 3 — Intent Layer Quality")
    print(f"{'─'*70}")

    print(f"\n[3.1] Target structure — (breakdown, measure)")
    print(f"\n10. BM Quality (Breakdown-Measure Quality):")
    bm_a = results_a.get('bm_quality')
    bm_b = results_b.get('bm_quality')
    if bm_a and bm_b:
        print(f"  10a. NMI mean:          {args.system_a}={bm_a.get('nmi_mean', 0):.4f}  {args.system_b}={bm_b.get('nmi_mean', 0):.4f}")
        print(f"  10b. Interestingness:   {args.system_a}={bm_a.get('int_mean', 0):.4f}  {args.system_b}={bm_b.get('int_mean', 0):.4f}")
        print(f"  10c. Actionability:     {args.system_a}={bm_a.get('actionability', 0):.4f}  {args.system_b}={bm_b.get('actionability', 0):.4f}")
        print(f"  10d. BM Diversity:      {args.system_a}={bm_a.get('bm_diversity', 0):.4f}  {args.system_b}={bm_b.get('bm_diversity', 0):.4f}")
        print(f"  10e. Cat pairs:         {args.system_a}={bm_a.get('total_categorical', 0)}/{bm_a.get('total_evaluated', 0)}  {args.system_b}={bm_b.get('total_categorical', 0)}/{bm_b.get('total_evaluated', 0)}")
    else:
        print(f"  BM Quality not available (--profile not provided)")

    print(f"\n[3.2] Question text & reason")

    qa = results_a.get('question_quality') or {}
    qb = results_b.get('question_quality') or {}

    qd_a = (qa.get('question_diversity') or {}).get('question_diversity', 0) or 0
    qd_b = (qb.get('question_diversity') or {}).get('question_diversity', 0) or 0
    print(f"\n11a. Question Semantic Diversity (within-system):")
    print(f"  • {args.system_a}: {qd_a:.4f}")
    print(f"  • {args.system_b}: {qd_b:.4f}")

    sp_a = qa.get('question_specificity') or {}
    sp_b = qb.get('question_specificity') or {}
    print(f"\n11b. Question Specificity (avg ± std word count):")
    print(f"  • {args.system_a}: {sp_a.get('question_specificity_mean', 0):.2f} ± {sp_a.get('question_specificity_std', 0):.2f}")
    print(f"  • {args.system_b}: {sp_b.get('question_specificity_mean', 0):.2f} ± {sp_b.get('question_specificity_std', 0):.2f}")

    al_a = (qa.get('question_insight_alignment') or {}).get('question_insight_alignment', 0) or 0
    al_b = (qb.get('question_insight_alignment') or {}).get('question_insight_alignment', 0) or 0
    print(f"\n11c. Question–Insight Alignment (cosine sim):")
    print(f"  • {args.system_a}: {al_a:.4f}")
    print(f"  • {args.system_b}: {al_b:.4f}")

    qn_a = (qa.get('question_novelty') or {}).get('question_novelty', 0) or 0
    qn_b = (qb.get('question_novelty') or {}).get('question_novelty', 0) or 0
    print(f"\n11d. Question Novelty (cross-system, tau=0.85):")
    print(f"  • {args.system_a}: {qn_a*100:.1f}%")
    print(f"  • {args.system_b}: {qn_b*100:.1f}%")

    rc_a = (qa.get('reason_insight_coherence') or {}).get('reason_insight_coherence', 0) or 0
    rc_b = (qb.get('reason_insight_coherence') or {}).get('reason_insight_coherence', 0) or 0
    print(f"\n11e. Reason–Insight Coherence (cosine sim):")
    print(f"  • {args.system_a}: {rc_a:.4f}")
    print(f"  • {args.system_b}: {rc_b:.4f}")

    print(f"\nEvaluation complete! Results saved to: {args.output}/")


if __name__ == "__main__":
    main()
