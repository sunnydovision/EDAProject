"""
ISGEN models (paper Section 2): Insight(B, M, S, P), Subspace S = set of (column, value) filters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Pattern types (paper)
TREND = "Trend"
OUTSTANDING_VALUE = "Outstanding Value"
ATTRIBUTION = "Attribution"
DISTRIBUTION_DIFFERENCE = "Distribution Difference"

PATTERNS = (TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE)


@dataclass(frozen=True)
class Subspace:
    """Subspace S = set of filters (column, value). Empty = no filter (whole dataset)."""
    filters: tuple[tuple[str, Any], ...]  # ((col1, val1), (col2, val2), ...)

    def used_cols(self) -> set[str]:
        return {f[0] for f in self.filters}

    def add(self, column: str, value: Any) -> Subspace:
        return Subspace(self.filters + ((column, value),))

    @classmethod
    def empty(cls) -> Subspace:
        return Subspace(())


@dataclass
class Insight:
    """Insight(B, M, S, P) per paper Section 2."""
    breakdown: str   # B
    measure: str     # M (e.g. "MEAN(Col)")
    subspace: Subspace  # S
    pattern: str     # P: Trend | Outstanding Value | Attribution | Distribution Difference
    score: float = 0.0
    view_values: list[float] | None = None  # values of view for plotting
    view_labels: list[str] | None = None   # breakdown values (labels)
    # For Distribution Difference: baseline (overall) distribution to compare against
    view_values_baseline: list[float] | None = None
    view_labels_baseline: list[str] | None = None
    # Optional: link back to card
    question: str = ""
    reason: str = ""

    def to_dict(self) -> dict:
        d = {
            "breakdown": self.breakdown,
            "measure": self.measure,
            "subspace": list(self.subspace.filters),
            "pattern": self.pattern,
            "score": self.score,
            "question": self.question,
            "reason": self.reason,
            "view_labels": self.view_labels or [],
            "view_values": self.view_values or [],
        }
        if self.view_values_baseline is not None:
            d["view_labels_baseline"] = self.view_labels_baseline or []
            d["view_values_baseline"] = self.view_values_baseline or []
        return d
