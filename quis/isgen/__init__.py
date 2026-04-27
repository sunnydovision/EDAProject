"""
ISGEN: Insight Generation module of QUIS.
Consumes Insight Cards from QUGEN, computes views and scores, runs basic insight + subspace search,
then NL explanation and rule-based plotting to produce Insight Summary.
"""

from .models import Insight, Subspace
from .pipeline import ISGENPipeline, ISGENConfig
from .views import compute_view, parse_measure

__all__ = [
    "Insight",
    "Subspace",
    "ISGENPipeline",
    "ISGENConfig",
    "compute_view",
    "parse_measure",
]
