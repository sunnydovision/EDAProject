"""
Standalone script to compare existing evaluation results.

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/compare_results.py --system_a QUIS --system_b Baseline
"""

import argparse
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from compare import create_comparison_table, generate_report
from configs.eval_config import RESULTS_DIR
from utils.log_config import save_run_log, load_eval_config

def load_results(system_name: str) -> dict:
    """Load evaluation results for a system."""
    result_file = f"{RESULTS_DIR}/{system_name.lower()}_results.json"
    with open(result_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Compare existing evaluation results')
    parser.add_argument('--system_a', type=str, required=True, help='Name of system A (e.g., QUIS)')
    parser.add_argument('--system_b', type=str, required=True, help='Name of system B (e.g., Baseline)')
    parser.add_argument('--output', type=str, default=RESULTS_DIR, help='Output directory')
    
    args = parser.parse_args()
    
    print(f"{'='*70}")
    print(f"Comparing {args.system_a} vs {args.system_b}")
    print(f"{'='*70}\n")
    
    # Save run log
    args_dict = vars(args)
    config_dict = load_eval_config()
    save_run_log("compare_results", args_dict, config_dict)
    
    # Load results
    print(f"Loading {args.system_a} results...")
    results_a = load_results(args.system_a)
    
    print(f"Loading {args.system_b} results...")
    results_b = load_results(args.system_b)
    
    # Generate comparison table
    print(f"\nGenerating comparison table...")
    comparison_df = create_comparison_table(results_a, results_b, args.system_a, args.system_b)
    
    # Save comparison table
    os.makedirs(args.output, exist_ok=True)
    comparison_path = f"{args.output}/comparison_table.csv"
    comparison_df.to_csv(comparison_path, index=False)
    print(f"Saved: {comparison_path}")
    
    # Print comparison table
    print(f"\n{comparison_df.to_string(index=False)}\n")
    
    # Generate report
    print(f"Generating comparison report...")
    report_path = f"{args.output}/comparison_report.md"
    generate_report(
        results_a, 
        results_b, 
        output_path=report_path,
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
    
    if a_wins > b_wins:
        print(f"\nOverall Winner: {args.system_a}")
    elif b_wins > a_wins:
        print(f"\nOverall Winner: {args.system_b}")
    else:
        print(f"\nOverall Winner: Tie")
    
    print(f"\nComparison complete! Results saved to: {args.output}/")

if __name__ == "__main__":
    main()
