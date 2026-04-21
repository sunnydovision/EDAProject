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
from compare import create_comparison_table, generate_report
from plot_evaluation import plot_evaluation_results


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
    token_file: str = None
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
        
        # 4 CORE METRICS for Defense
        'faithfulness': compute_faithfulness(insights_data, df_raw, df_cleaned, csv_path),
        'insight_significance': compute_significance(insights_data, df_cleaned, csv_path),
        'question_diversity': compute_diversity(insights_data),
        
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
    results_a['insight_novelty'] = novelty_a
    
    print(f" Computing {results_b['system']} novelty vs {results_a['system']}...")
    novelty_b = compute_novelty(insights_b, insights_a)
    results_b['insight_novelty'] = novelty_b
    
    return {
        'system_a': results_a,
        'system_b': results_b
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate IFQ vs Baseline (v2)')
    parser.add_argument('--data', type=str, required=True, help='Path to CSV data file')
    parser.add_argument('--system_a', type=str, required=True, help='Name of system A (e.g., IFQ)')
    parser.add_argument('--path_a', type=str, required=True, help='Path to system A insights_summary.json')
    parser.add_argument('--timing_a', type=str, default=None, help='Path to system A timing file')
    parser.add_argument('--token_a', type=str, default=None, help='Path to system A token usage file')
    parser.add_argument('--system_b', type=str, required=True, help='Name of system B (e.g., Baseline)')
    parser.add_argument('--path_b', type=str, required=True, help='Path to system B insights_summary.json')
    parser.add_argument('--timing_b', type=str, default=None, help='Path to system B timing file')
    parser.add_argument('--token_b', type=str, default=None, help='Path to system B token usage file')
    parser.add_argument('--output', type=str, default='evaluation/results', help='Output directory')
    
    args = parser.parse_args()
    
    print(f"{'='*70}")
    print(f"{args.system_a} vs {args.system_b} Evaluation (v2)")
    print(f"{'='*70}\n")
    
    # Load and clean data
    print(f"Loading data: {args.data}")
    df_raw, df_cleaned = load_and_clean_data(args.data)
    print(f"  Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns")
    print(f"  Cleaned {len(df_cleaned)} rows, {len(df_cleaned.columns)} columns")
    print()
    
    # Evaluate both systems
    results_a = evaluate_system(
        system_name=args.system_a,
        summary_path=args.path_a,
        df_raw=df_raw,
        df_cleaned=df_cleaned,
        csv_path=args.data,
        timing_file=args.timing_a,
        token_file=args.token_a
    )
    
    results_b = evaluate_system(
        system_name=args.system_b,
        summary_path=args.path_b,
        df_raw=df_raw,
        df_cleaned=df_cleaned,
        csv_path=args.data,
        timing_file=args.timing_b,
        token_file=args.token_b
    )
    
    # Load insights for novelty computation
    insights_a = load_insights(args.path_a)
    insights_b = load_insights(args.path_b)
    
    # Compute comparative metrics (novelty)
    comparison_results = evaluate_comparison(results_a, results_b, insights_a, insights_b)
    
    # Compute subspace-specific metrics
    print(f"\n{'='*70}")
    print("Computing Subspace Metrics")
    print(f"{'='*70}\n")
    print(f" Subspace insights: {args.system_a}={len(filter_insights_with_subspace(insights_a))}, {args.system_b}={len(filter_insights_with_subspace(insights_b))}")
    subspace_results = compute_subspace_metrics(insights_a, insights_b, df_raw, df_cleaned, args.data)
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
    
    print(f"\n4 CORE METRICS + 2 EFFICIENCY METRICS:\n")
    
    print(f"1. Faithfulness (Correctness):")
    print(f"  • {args.system_a}: {results_a['faithfulness']['faithfulness']*100:.1f}%")
    print(f"  • {args.system_b}: {results_b['faithfulness']['faithfulness']*100:.1f}%")
    
    print(f"\n2. Statistical Significance (Validity):")
    print(f"  • {args.system_a}: {results_a['insight_significance']['significant_rate']*100:.1f}%")
    print(f"  • {args.system_b}: {results_b['insight_significance']['significant_rate']*100:.1f}%")
    
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
    
    # Subspace metrics summary
    print(f"\n7. Subspace Metrics (insights with subspace filter only):")
    sa = results_a.get('subspace_metrics', {})
    sb = results_b.get('subspace_metrics', {})
    print(f"  • {args.system_a}: {sa.get('total_with_subspace', 0)} subspace insights")
    print(f"  • {args.system_b}: {sb.get('total_with_subspace', 0)} subspace insights")
    if sa.get('faithfulness') and sb.get('faithfulness'):
        print(f"  Faithfulness:  {args.system_a}={sa['faithfulness']['faithfulness']*100:.1f}%  {args.system_b}={sb['faithfulness']['faithfulness']*100:.1f}%")
    if sa.get('significance') and sb.get('significance'):
        print(f"  Significance:  {args.system_a}={sa['significance']['significant_rate']*100:.1f}%  {args.system_b}={sb['significance']['significant_rate']*100:.1f}%")
    if sa.get('novelty') and sb.get('novelty'):
        print(f"  Novelty:       {args.system_a}={sa['novelty']['novelty']*100:.1f}%  {args.system_b}={sb['novelty']['novelty']*100:.1f}%")
    if sa.get('diversity') and sb.get('diversity'):
        _sdiv_a = sa['diversity'].get('diversity') or sa['diversity'].get('semantic_diversity', 0)
        _sdiv_b = sb['diversity'].get('diversity') or sb['diversity'].get('semantic_diversity', 0)
        print(f"  Diversity:     {args.system_a}={_sdiv_a:.3f}  {args.system_b}={_sdiv_b:.3f}")
    
    print(f"\nEvaluation complete! Results saved to: {args.output}/")


if __name__ == "__main__":
    main()
