"""
Configuration for evaluation scripts.

All paths are relative to project root.
"""

# Data paths
DATA_PATH = "data/Adidas_cleaned.csv"

# Profile path for significance testing
PROFILE_PATH = "baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json"

# Insights paths
QUIS_INSIGHTS_PATH = "insights_summary_adidas_v4.json"
BASELINE_INSIGHTS_PATH = "baseline/auto_eda_agent/output_adidas/quis_format/insights_summary.json"
ONLYSTATS_INSIGHTS_PATH = "onlystats_output_adidas/insights_summary.json"

# Results paths
RESULTS_DIR = "evaluation/evaluation_results"
QUIS_RESULTS = "evaluation/evaluation_results/quis_results.json"
BASELINE_RESULTS = "evaluation/evaluation_results/baseline_results.json"
ONLYSTATS_RESULTS = "evaluation/evaluation_results/onlystats_results.json"

# Comparison output
COMPARISON_OUTPUT_DIR = "evaluation/evaluation_results"
