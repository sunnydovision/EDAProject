"""
QUGEN: Question Generation module of QUIS.
Generates Insight Cards (Question, Reason, Breakdown, Measure) from data semantics
in an iterative way, without manually curated examples.
"""

from .models import InsightCard, TableSchema
from .pipeline import QUGENPipeline, QUGENConfig
from .stats import BasicStatsGenerator

__all__ = [
    "InsightCard",
    "TableSchema",
    "QUGENPipeline",
    "QUGENConfig",
    "BasicStatsGenerator",
]
