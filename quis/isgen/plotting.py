"""
Rule-based plotting per pattern (paper Appendix B).
"""

from __future__ import annotations

import os
import numpy as np
from .models import Insight, TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE


def plot_insight(insight: Insight, save_path: str | None = None) -> str | None:
    """
    Generate plot for insight; save to save_path if provided.
    Returns path to saved file or None.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    labels = insight.view_labels or []
    values = insight.view_values or []
    if len(values) < 2:
        return None
    P = insight.pattern
    fig, ax = plt.subplots()
    if P == TREND:
        sorted_pairs = sorted(zip(values, labels))
        sorted_values = [v for v, _ in sorted_pairs]
        sorted_labels = [l for _, l in sorted_pairs]
        x = list(range(len(sorted_values)))
        ax.plot(x, sorted_values, "o-", color="steelblue", linewidth=2, markersize=5)
        ax.set_xticks(x)
        ax.set_xticklabels(sorted_labels, rotation=45, ha="right")
        ax.set_ylabel(insight.measure)
        ax.set_xlabel(insight.breakdown)
        ax.set_title(f"Trend: {insight.measure} by {insight.breakdown}")
    elif P == ATTRIBUTION and sum(values) > 0:
        pcts = [v / sum(values) * 100 for v in values[:20]]
        ax.bar(labels[:20], pcts)
        ax.set_xticklabels(labels[:20], rotation=45, ha="right")
        ax.set_ylabel("% of total")
        ax.set_xlabel(insight.breakdown)
        ax.set_title(f"{insight.pattern}: {insight.measure} by {insight.breakdown}")
    elif P == OUTSTANDING_VALUE:
        ax.bar(labels[:20], values[:20])
        ax.set_xticklabels(labels[:20], rotation=45, ha="right")
        ax.set_ylabel(insight.measure)
        ax.set_xlabel(insight.breakdown)
        ax.set_title(f"{insight.pattern}: {insight.measure} by {insight.breakdown}")
    elif P == DISTRIBUTION_DIFFERENCE:
        total = sum(values)
        if total > 0:
            sizes = [v / total for v in values[:15]]
            lbls = labels[:15]
            ax.pie(sizes, labels=lbls, autopct="%1.1f%%", startangle=90)
        ax.set_title(f"Distribution: {insight.breakdown}")
    else:
        ax.bar(labels[:20], values[:20])
        ax.set_xticklabels(labels[:20], rotation=45, ha="right")
        ax.set_title(f"{insight.measure} by {insight.breakdown}")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches="tight")
        plt.close()
        return save_path
    plt.close()
    return None
