"""
Evaluation metrics for IFQ vs Baseline comparison.

This package contains individual metric computation modules:
- faithfulness: Correctness of insights
- significance: Statistical validity of insights
- novelty: Usefulness of insights compared to baseline
- diversity: Non-redundancy of insights
- time_to_insight: Efficiency metric
- token_usage: Efficiency metric
- subspace: Subspace analysis
- data_loader: Data loading and cleaning utilities
"""

from .data_loader import load_and_clean_data
from .faithfulness import compute_faithfulness
from .significance import compute_significance
from .novelty import compute_novelty
from .diversity import compute_diversity
from .time_to_insight import compute_time_to_insight
from .token_usage import compute_token_usage
from .subspace import compute_subspace_count, filter_insights_with_subspace, compute_subspace_metrics
from .score_uplift import compute_score_uplift_from_subspace

__all__ = [
    'load_and_clean_data',
    'compute_faithfulness',
    'compute_significance',
    'compute_novelty',
    'compute_diversity',
    'compute_time_to_insight',
    'compute_token_usage',
    'compute_subspace_count',
    'filter_insights_with_subspace',
    'compute_subspace_metrics',
    'compute_score_uplift_from_subspace',
]
