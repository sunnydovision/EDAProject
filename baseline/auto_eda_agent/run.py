"""
Agentic AutoEDA Baseline - Main Entry Point

Run complete agentic AutoEDA workflow where each step:
- Acts as autonomous specialist agent
- Iteratively refines until satisfied
- Uses multi-prompt strategy
- Verbose logging of all actions

Usage:
    cd baseline
    python run.py ../data/transactions.csv output
"""

import sys
import os
from agent import AgenticAutoEDA


def run_baseline(data_file: str, output_dir: str = 'output', max_iterations: int = 3, skip_step5: bool = False):
    """
    Run complete Agentic AutoEDA baseline workflow.
    
    Each step acts as autonomous agent:
    - Iteratively refines until satisfied
    - Uses multi-prompt strategy
    - Verbose logging of all actions
    
    Args:
        data_file: Path to dataset
        output_dir: Directory for output files
        max_iterations: Max iterations per step (default: 3)
        skip_step5: Skip step 5 (insight extraction) if True (default: False)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 70)
    print("🤖 AGENTIC AUTOEDA BASELINE")
    print("=" * 70)
    print("\nEach step acts as autonomous specialist agent:")
    print("  • Iteratively refines analysis")
    print("  • Self-evaluates and improves")
    print("  • Uses multi-prompt strategy")
    print("  • Verbose action logging\n")
    
    if skip_step5:
        print("⚠️  Running steps 1-4 only (skipping step 5)\n")
    
    # Initialize Agentic AutoEDA
    agent = AgenticAutoEDA(data_file)
    
    # Run complete agentic workflow
    step_outputs = agent.run_autoeda(output_dir, max_iterations, skip_step5)
    
    print("\n" + "=" * 70)
    print("✅ AGENTIC AUTOEDA COMPLETE")
    print("=" * 70)
    print(f"\nOutput structure in '{output_dir}/':")
    print(f"  📁 step1_profiling/")
    print(f"     • profiling_code_v*.py - Code iterations")
    print(f"     • profile.json - Final profile")
    print(f"     • summary.md - Step summary")
    print(f"  📁 step2_quality/")
    print(f"     • quality_code_v*.py - Code iterations")
    print(f"     • quality_report.json - Quality analysis")
    print(f"     • summary.md - Step summary")
    print(f"  📁 step3_statistics/")
    print(f"     • statistics_code_v*.py - Code iterations")
    print(f"     • statistics.json - Statistical analysis")
    print(f"     • summary.md - Step summary")
    print(f"  📁 step4_patterns/")
    print(f"     • pattern_code_*.py - Multi-prompt code")
    print(f"     • patterns.json - All discovered patterns")
    print(f"     • patterns_*.json - Patterns by category")
    print(f"  📁 step5_insights/")
    print(f"     • insights.json - All insights with ISGEN scores")
    print(f"     • insight_*.png - Charts ({len(step_outputs.get('step5', []))} files)")
    print(f"  📁 summary/")
    print(f"     • summary.txt - Overall summary")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <data_file> [output_dir] [--skip-step5]")
        print("Example: python run.py ../data/transactions.csv output")
        print("         python run.py ../data/transactions.csv output --skip-step5")
        sys.exit(1)
    
    data_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    skip_step5 = '--skip-step5' in sys.argv
    
    run_baseline(data_file, output_dir, skip_step5=skip_step5)
