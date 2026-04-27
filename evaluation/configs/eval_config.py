"""
Configuration for evaluation scripts.

All paths are relative to project root.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DatasetConfig:
    """Configuration for a specific dataset."""
    data_path: str
    profile_path: Optional[str]
    quis_insights_path: Optional[str]
    baseline_insights_path: Optional[str]
    onlystats_insights_path: Optional[str]
    quis_timing_path: Optional[str] = None
    quis_usage_path: Optional[str] = None
    baseline_timing_path: Optional[str] = None
    baseline_usage_path: Optional[str] = None
    
    @property
    def results_dir(self) -> str:
        """Results directory for this dataset."""
        dataset_name = self.data_path.split("/")[-1].replace("_cleaned.csv", "")
        return f"evaluation/evaluation_results/{dataset_name}"
    
    @property
    def quis_results_path(self) -> str:
        """Path to QUIS evaluation results."""
        return f"{self.results_dir}/quis_results.json"
    
    @property
    def baseline_results_path(self) -> str:
        """Path to baseline evaluation results."""
        return f"{self.results_dir}/baseline_results.json"
    
    @property
    def onlystats_results_path(self) -> str:
        """Path to onlystats evaluation results."""
        return f"{self.results_dir}/onlystats_results.json"
    
    @property
    def comparison_output_dir(self) -> str:
        """Directory for comparison outputs."""
        return self.results_dir
    
    def validate_paths(self) -> list[str]:
        """Validate that required paths exist.
        
        Returns:
            List of error messages for missing paths. Empty if all paths are valid.
        """
        import os
        errors = []
        
        # Check data path (required)
        if not os.path.exists(self.data_path):
            errors.append(f"Data file not found: {self.data_path}")
        
        # Check profile path if specified
        if self.profile_path and not os.path.exists(self.profile_path):
            errors.append(f"Profile file not found: {self.profile_path} (Run baseline to generate)")
        
        # Check insights paths if specified
        if self.quis_insights_path and not os.path.exists(self.quis_insights_path):
            errors.append(f"QUIS insights file not found: {self.quis_insights_path} (Run QUIS pipeline to generate)")
        
        if self.baseline_insights_path and not os.path.exists(self.baseline_insights_path):
            errors.append(f"Baseline insights file not found: {self.baseline_insights_path} (Run baseline to generate)")
        
        if self.onlystats_insights_path and not os.path.exists(self.onlystats_insights_path):
            errors.append(f"Onlystats insights file not found: {self.onlystats_insights_path} (Run onlystats pipeline to generate)")
        
        # Note: timing/usage paths are optional (for efficiency metrics only)
        # They are not validated as errors to allow evaluation without them
        
        return errors


class EvalConfig:
    """Evaluation configuration manager for multiple datasets."""
    
    # Dataset configurations
    DATASETS = {
        "adidas": {
            "data_path": "data/adidas_cleaned.csv",
            "profile_path": "baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json",
            "quis_insights_path": "insights_summary_adidas_v4.json",
            "baseline_insights_path": "baseline/auto_eda_agent/output_adidas/quis_format/insights_summary.json",
            "onlystats_insights_path": "onlystats_results/onlystats_20241201_000000_Adidas_cleaned/insights_summary.json",
            "quis_timing_path": "quis_results/quis_20241201_000000_Adidas_cleaned_v4/timing.json",
            "quis_usage_path": "quis_results/quis_20241201_000000_Adidas_cleaned_v4/usage.json",
            "baseline_timing_path": "baseline/auto_eda_agent/output_adidas/timing.json",
            "baseline_usage_path": "baseline/auto_eda_agent/output_adidas/usage.json",
        },
        "transactions": {
            "data_path": "data/transactions_cleaned.csv",
            "profile_path": "baseline/auto_eda_agent/output_transactions/step1_profiling/profile.json",  # Run baseline to generate
            "quis_insights_path": "quis_results/quis_20260427_144322_transactions_cleaned/insights_summary.json",
            "baseline_insights_path": "baseline/auto_eda_agent/output_transactions/quis_format/insights_summary.json",
            "onlystats_insights_path": "onlystats_results/onlystats_20260427_160049_transactions_cleaned_v4/insights_summary.json",
            "quis_timing_path": "quis_results/quis_20260427_144322_transactions_cleaned/timing.json",
            "quis_usage_path": "quis_results/quis_20260427_144322_transactions_cleaned/usage.json",
            "baseline_timing_path": "baseline/auto_eda_agent/output_transactions/timing.json",
            "baseline_usage_path": "baseline/auto_eda_agent/output_transactions/usage.json",
        },
        "employee_attrition": {
            "data_path": "data/employee_attrition_cleaned.csv",
            "profile_path": None,  # Run baseline to generate
            "quis_insights_path": None,  # Will be determined when running QUIS
            "baseline_insights_path": None,  # Run baseline to generate
            "onlystats_insights_path": None,  # Doesn't exist yet
            "quis_timing_path": None,
            "quis_usage_path": None,
            "baseline_timing_path": None,
            "baseline_usage_path": None,
        },
        "online_sales": {
            "data_path": "data/online_sales_cleaned.csv",
            "profile_path": None,  # Run baseline to generate
            "quis_insights_path": None,  # Will be determined when running QUIS
            "baseline_insights_path": None,  # Run baseline to generate
            "onlystats_insights_path": None,  # Doesn't exist yet
            "quis_timing_path": None,
            "quis_usage_path": None,
            "baseline_timing_path": None,
            "baseline_usage_path": None,
        },
    }
    
    # Aggregated results directory (for cross-dataset comparison)
    AGGREGATED_RESULTS_DIR = "evaluation/evaluation_results/aggregated"
    
    @classmethod
    def get_dataset_config(cls, dataset_name: str) -> DatasetConfig:
        """Get configuration for a specific dataset.
        
        Args:
            dataset_name: Name of the dataset (adidas, transactions, employee_attrition, online_sales)
            
        Returns:
            DatasetConfig object with dataset-specific paths
            
        Raises:
            ValueError: If dataset is unknown or required paths are missing
        """
        if dataset_name not in cls.DATASETS:
            raise ValueError(f"Unknown dataset: {dataset_name}. Available datasets: {list(cls.DATASETS.keys())}")
        
        config = DatasetConfig(**cls.DATASETS[dataset_name])
        
        # Validate paths and report errors
        errors = config.validate_paths()
        if errors:
            error_msg = f"Missing paths for dataset '{dataset_name}':\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)
        
        return config
    
    @classmethod
    def list_datasets(cls) -> list[str]:
        """List all available datasets."""
        return list(cls.DATASETS.keys())
