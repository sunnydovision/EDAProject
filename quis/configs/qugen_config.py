"""
QUGEN configuration parameters.

Paper Appendix D.2:
- LLM: Llama-3-70b-instruct (AI@Meta, 2024)
- Sampling temperature t = 1.1
- Number of samples at each iteration s = 3
- Number of iterations n = 10
- Number of in-context examples = 6
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from .api_config import get_default_model


@dataclass
class QUGENConfig:
    """Parameters for QUGEN (paper Appendix D.2)."""

    # LLM configuration
    model: str = get_default_model()
    
    # LLM sampling parameters
    temperature: float = 1.1
    num_samples_per_iteration: int = 3
    num_iterations: int = 10
    num_in_context_examples: int = 6
    num_questions_per_prompt: int = 10

    # Filter thresholds
    schema_relevance_threshold: float = 0.25
    dedup_similarity_threshold: float = 0.85

    # Optional: callable(question) -> row_count for simple-question filter; None = heuristic only
    run_query_fn: Callable[[str], int] | None = None


# Default config instance
DEFAULT_QUGEN_CONFIG = QUGENConfig()
