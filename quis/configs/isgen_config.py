"""
ISGEN configuration parameters.

Paper parameters:
- beam_width = 100
- exp_factor = 100
- max_depth = 1
- wLLM = 0.5
"""

from dataclasses import dataclass


@dataclass
class ISGENConfig:
    """Parameters for ISGEN subspace search."""

    # Subspace search parameters (paper values)
    beam_width: int = 100
    exp_factor: int = 100
    max_depth: int = 1
    w_llm: float = 0.5

    # Pipeline configuration
    run_subspace_search: bool = True
    max_insights_per_card: int = 3
    threshold_scale: float = 1.0

    # Deduplication thresholds
    max_overall_per_key: int = 1
    max_subspace_per_key: int = 2
    max_insights_per_question: int = 3


# Default config instance
DEFAULT_ISGEN_CONFIG = ISGENConfig()
