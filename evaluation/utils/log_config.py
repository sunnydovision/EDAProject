"""
Utility to save evaluation configuration to logs for debugging.

Logs are saved to evaluation/logs/ with timestamp.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


def save_run_log(
    script_name: str,
    args: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str = "evaluation/logs"
) -> str:
    """
    Save run configuration to a timestamped log file.
    
    Args:
        script_name: Name of the script being run (e.g., "run_evaluation", "compare_results")
        args: Dictionary of command line arguments
        config: Dictionary of configuration values
        output_dir: Directory to save logs (default: evaluation/logs)
        
    Returns:
        Path to the saved log file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{script_name}_{timestamp}.json"
    log_path = os.path.join(output_dir, log_filename)
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "script": script_name,
        "arguments": args,
        "config": config,
    }
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"Run log saved: {log_path}")
    return log_path


def load_eval_config(dataset_name: str = None) -> Dict[str, Any]:
    """Load and return the evaluation configuration.
    
    Args:
        dataset_name: Optional dataset name to get specific config. If None, returns available datasets.
    """
    from configs.eval_config import EvalConfig
    
    if dataset_name:
        config = EvalConfig.get_dataset_config(dataset_name)
        return {
            "dataset": dataset_name,
            "data_path": config.data_path,
            "profile_path": config.profile_path,
            "quis_insights_path": config.quis_insights_path,
            "baseline_insights_path": config.baseline_insights_path,
            "onlystats_insights_path": config.onlystats_insights_path,
            "results_dir": config.results_dir,
        }
    else:
        return {
            "available_datasets": EvalConfig.list_datasets(),
            "aggregated_results_dir": EvalConfig.AGGREGATED_RESULTS_DIR,
        }
