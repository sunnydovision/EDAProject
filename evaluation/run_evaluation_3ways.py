#!/usr/bin/env python3
"""
3-way evaluation pipeline: QUIS vs Baseline vs ONLYSTATS.

This script runs pairwise evaluations and then a 3-way comparison:
1. QUIS vs Baseline
2. Baseline vs QUIS
3. Onlystats vs QUIS
4. 3-way comparison using compare3.py

Usage:
  python evaluation/run_evaluation_3ways.py --dataset transactions
"""

import argparse
import subprocess
import sys
from configs.eval_config import EvalConfig


def run_evaluation(dataset: str, system_a: str, system_b: str):
    """Run pairwise evaluation."""
    cmd = [
        sys.executable, "evaluation/run_evaluation.py",
        "--dataset", dataset,
        "--system_a", system_a,
        "--system_b", system_b,
    ]
    print(f"\n{'='*70}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*70}\n")
    result = subprocess.run(cmd, cwd=".")
    return result.returncode == 0


def run_compare3(dataset: str):
    """Run 3-way comparison."""
    cmd = [
        sys.executable, "evaluation/compare3.py",
        "--dataset", dataset,
    ]
    print(f"\n{'='*70}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*70}\n")
    result = subprocess.run(cmd, cwd=".")
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description='3-way evaluation pipeline: QUIS vs Baseline vs ONLYSTATS')
    parser.add_argument('--dataset', type=str, required=True, 
                        help=f'Dataset name: {", ".join(EvalConfig.list_datasets())}')
    args = parser.parse_args()
    
    # Validate dataset
    try:
        config = EvalConfig.get_dataset_config(args.dataset)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"3-Way Evaluation Pipeline - Dataset: {args.dataset}")
    print(f"{'='*70}\n")
    
    # Check that all required insights paths exist
    if not config.quis_insights_path:
        print(f"Error: QUIS insights path not set for dataset '{args.dataset}'")
        sys.exit(1)
    if not config.baseline_insights_path:
        print(f"Error: Baseline insights path not set for dataset '{args.dataset}'")
        sys.exit(1)
    if not config.onlystats_insights_path:
        print(f"Error: Onlystats insights path not set for dataset '{args.dataset}'")
        sys.exit(1)
    
    # Run pairwise evaluations
    evaluations = [
        ("QUIS vs Baseline", "QUIS", "Baseline"),
        ("Baseline vs QUIS", "Baseline", "QUIS"),
        ("Onlystats vs QUIS", "ONLYSTATS", "QUIS"),
    ]
    
    results = {}
    for name, sys_a, sys_b in evaluations:
        success = run_evaluation(args.dataset, sys_a, sys_b)
        results[name] = success
        if not success:
            print(f"Error: {name} evaluation failed")
    
    # Run 3-way comparison
    success = run_compare3(args.dataset)
    results["3-way comparison"] = success
    
    # Summary
    print(f"\n{'='*70}")
    print("Pipeline Summary")
    print(f"{'='*70}\n")
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {name}")
    
    all_success = all(results.values())
    if all_success:
        print(f"\nPipeline completed successfully!")
        print(f"Results saved to: {config.results_dir}/")
    else:
        print(f"\nPipeline completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
