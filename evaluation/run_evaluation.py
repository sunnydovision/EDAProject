"""
Main entry point for QUIS vs Baseline evaluation.

Usage:
    python run_evaluation.py --data data/Adidas.csv \
                            --quis insights_summary_v2.json \
                            --baseline baseline/auto_eda_agent/output/quis_format/insights_summary.json \
                            --output evaluation/results
"""

import argparse
import json
import pandas as pd
import os
import sys
import time

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from compute_metrics import evaluate_system
from compare_systems import create_comparison_table, plot_comparison, generate_report


def main():
    parser = argparse.ArgumentParser(description='Evaluate QUIS vs Baseline')
    parser.add_argument('--data', type=str, required=True, help='Path to CSV data file')
    parser.add_argument('--quis', type=str, required=True, help='Path to QUIS insights_summary.json')
    parser.add_argument('--baseline', type=str, required=True, help='Path to Baseline insights_summary.json')
    parser.add_argument('--output', type=str, default='evaluation/results', help='Output directory')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("QUIS vs Baseline Evaluation")
    print("="*70 + "\n")
    
    # Load data
    print(f"📂 Loading data: {args.data}")
    df = pd.read_csv(args.data, sep=None, engine='python')
    print(f"  ✓ Loaded {len(df)} rows, {len(df.columns)} columns\n")
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Evaluate QUIS (with TTI tracking)
    start_time = time.time()
    quis_results = evaluate_system(
        system_name="QUIS",
        summary_path=args.quis,
        df=df,
        csv_path=args.data
    )
    quis_results['time_to_insight'] = time.time() - start_time
    
    # Evaluate Baseline (with TTI tracking)
    start_time = time.time()
    baseline_results = evaluate_system(
        system_name="Baseline",
        summary_path=args.baseline,
        df=df,
        csv_path=args.data
    )
    baseline_results['time_to_insight'] = time.time() - start_time
    
    # Save individual results
    with open(f"{args.output}/quis_results.json", 'w') as f:
        json.dump(quis_results, f, indent=2, default=str)
    print(f"💾 Saved: {args.output}/quis_results.json")
    
    with open(f"{args.output}/baseline_results.json", 'w') as f:
        json.dump(baseline_results, f, indent=2, default=str)
    print(f"💾 Saved: {args.output}/baseline_results.json")
    
    # Create comparison
    print(f"\n{'='*70}")
    print("Generating Comparison")
    print(f"{'='*70}\n")
    
    # Comparison table
    comparison_df = create_comparison_table(quis_results, baseline_results)
    comparison_df.to_csv(f"{args.output}/comparison_table.csv", index=False)
    print(f"📊 Saved: {args.output}/comparison_table.csv")
    
    # Print comparison table
    print(f"\n{comparison_df.to_string(index=False)}\n")
    
    # Generate plots
    print(f"\n📊 Generating visualizations...")
    plot_comparison(quis_results, baseline_results, output_dir=f"{args.output}/plots")
    
    # Generate report
    print(f"\n📄 Generating report...")
    generate_report(quis_results, baseline_results, output_path=f"{args.output}/comparison_report.md")
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}\n")
    
    quis_wins = len(comparison_df[comparison_df['Winner'] == 'QUIS'])
    baseline_wins = len(comparison_df[comparison_df['Winner'] == 'Baseline'])
    
    print(f"🏆 QUIS Wins: {quis_wins}/{len(comparison_df)} metrics")
    print(f"🏆 Baseline Wins: {baseline_wins}/{len(comparison_df)} metrics\n")
    
    print("Key Findings:")
    print(f"  • QUIS Subspace Rate: {quis_results['subspace_metrics']['subspace_rate']*100:.1f}%")
    print(f"  • Baseline Subspace Rate: {baseline_results['subspace_metrics']['subspace_rate']*100:.1f}%")
    print(f"  • QUIS Schema Coverage: {quis_results['schema_coverage']['coverage']*100:.1f}%")
    print(f"  • Baseline Schema Coverage: {baseline_results['schema_coverage']['coverage']*100:.1f}%")
    print(f"  • QUIS Time-to-Insight: {quis_tti:.2f}s")
    print(f"  • Baseline Time-to-Insight: {baseline_tti:.2f}s")
    
    print(f"\n✅ Evaluation complete! Results saved to: {args.output}/")
    print(f"\nView full report: {args.output}/comparison_report.md")
    print(f"View plots: {args.output}/plots/\n")


if __name__ == "__main__":
    main()
