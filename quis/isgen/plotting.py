"""
Rule-based plotting per pattern (paper Appendix B).
"""

from __future__ import annotations

import os
import numpy as np
from .models import Insight, TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE

# ── Palette ──────────────────────────────────────────────────────────
_ACCENT = "#4C6FFF"
_ACCENT_TOP = "#FF6B6B"
_ACCENT_SECOND = "#51CF66"
_BAR_BASE = "#94B8FF"
_LINE_COLOR = "#4C6FFF"
_LINE_MARKER = "#FF6B6B"
_BG_COLOR = "#FAFBFF"
_GRID_COLOR = "#E8ECF4"
_TITLE_COLOR = "#1A1A2E"
_LABEL_COLOR = "#4A5568"
_PIE_COLORS = [
    "#4C6FFF", "#FF6B6B", "#51CF66", "#FFD43B", "#845EF7",
    "#FF922B", "#22B8CF", "#F06595", "#20C997", "#ADB5BD",
    "#E64980", "#7950F2", "#15AABF", "#82C91E", "#FAB005",
]

_FONT_FAMILY = "sans-serif"


def _apply_style(ax, fig):
    """Apply a clean, modern style to axes and figure."""
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor(_BG_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(_GRID_COLOR)
    ax.spines["bottom"].set_color(_GRID_COLOR)
    ax.tick_params(colors=_LABEL_COLOR, labelsize=9)
    ax.yaxis.grid(True, color=_GRID_COLOR, linewidth=0.7, linestyle="--")
    ax.set_axisbelow(True)


def _bar_colors(values: list[float], n: int) -> list[str]:
    """Highlight the top bar with accent red, second with green, rest with soft blue."""
    if n == 0:
        return []
    abs_vals = [abs(v) for v in values[:n]]
    sorted_idx = sorted(range(n), key=lambda i: -abs_vals[i])
    colors = [_BAR_BASE] * n
    if len(sorted_idx) >= 1:
        colors[sorted_idx[0]] = _ACCENT_TOP
    if len(sorted_idx) >= 2:
        colors[sorted_idx[1]] = _ACCENT_SECOND
    return colors


def _truncate_label(label: str, max_len: int = 22) -> str:
    return label if len(label) <= max_len else label[: max_len - 1] + "…"


def _thin_labels(labels: list[str], max_show: int = 25) -> tuple[list[int], list[str]]:
    """For large label sets, pick evenly-spaced tick positions."""
    n = len(labels)
    if n <= max_show:
        return list(range(n)), labels
    step = max(1, n // max_show)
    positions = list(range(0, n, step))
    if positions[-1] != n - 1:
        positions.append(n - 1)
    return positions, [labels[i] for i in positions]


def plot_insight(insight: Insight, save_path: str | None = None) -> str | None:
    """
    Generate plot for insight; save to save_path if provided.
    Returns path to saved file or None.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
    except ImportError:
        return None

    labels = insight.view_labels or []
    values = insight.view_values or []
    if len(values) < 2:
        return None

    P = insight.pattern
    n_bars = min(len(labels), 20)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    _apply_style(ax, fig)

    if P == TREND:
        sorted_pairs = sorted(zip(values, labels))
        sorted_values = [v for v, _ in sorted_pairs]
        sorted_labels = [l for _, l in sorted_pairs]
        x = list(range(len(sorted_values)))

        ax.fill_between(x, sorted_values, alpha=0.12, color=_LINE_COLOR)
        ax.plot(x, sorted_values, "-", color=_LINE_COLOR, linewidth=2.5)
        marker_size = max(2, min(7, 200 // max(len(x), 1)))
        ax.plot(x, sorted_values, "o", color=_LINE_MARKER, markersize=marker_size,
                markeredgecolor="#FFFFFF", markeredgewidth=1, zorder=5)

        tick_pos, tick_labels = _thin_labels(sorted_labels, max_show=20)
        ax.set_xticks(tick_pos)
        ax.set_xticklabels([_truncate_label(l, 15) for l in tick_labels],
                           rotation=40, ha="right", fontsize=8)

        ax.set_ylabel(insight.measure, fontsize=10, color=_LABEL_COLOR)
        ax.set_xlabel(insight.breakdown, fontsize=10, color=_LABEL_COLOR)
        ax.set_title(f"Trend: {insight.measure}\nby {insight.breakdown}",
                     fontsize=13, fontweight="bold", color=_TITLE_COLOR, pad=14)

    elif P == ATTRIBUTION and sum(values) > 0:
        show_labels = [_truncate_label(l) for l in labels[:n_bars]]
        pcts = [v / sum(values) * 100 for v in values[:n_bars]]
        colors = _bar_colors(pcts, len(pcts))

        x_pos = range(len(show_labels))
        bars = ax.bar(x_pos, pcts, color=colors, edgecolor="#FFFFFF", linewidth=0.8,
                       width=0.65, zorder=3)
        for bar, pct in zip(bars, pcts):
            if pct > 5:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                        f"{pct:.1f}%", ha="center", va="bottom",
                        fontsize=8, fontweight="bold", color=_TITLE_COLOR)

        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(show_labels, rotation=40, ha="right", fontsize=8)
        ax.set_ylabel("% of total", fontsize=10, color=_LABEL_COLOR)
        ax.set_xlabel(insight.breakdown, fontsize=10, color=_LABEL_COLOR)
        ax.set_title(f"Attribution: {insight.measure}\nby {insight.breakdown}",
                     fontsize=13, fontweight="bold", color=_TITLE_COLOR, pad=14)

    elif P == OUTSTANDING_VALUE:
        show_labels = [_truncate_label(l) for l in labels[:n_bars]]
        show_values = values[:n_bars]
        colors = _bar_colors(show_values, len(show_values))

        x_pos = range(len(show_labels))
        bars = ax.bar(x_pos, show_values, color=colors, edgecolor="#FFFFFF",
                       linewidth=0.8, width=0.65, zorder=3)

        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(show_labels, rotation=40, ha="right", fontsize=8)
        ax.set_ylabel(insight.measure, fontsize=10, color=_LABEL_COLOR)
        ax.set_xlabel(insight.breakdown, fontsize=10, color=_LABEL_COLOR)
        ax.set_title(f"Outstanding Value: {insight.measure}\nby {insight.breakdown}",
                     fontsize=13, fontweight="bold", color=_TITLE_COLOR, pad=14)

    elif P == DISTRIBUTION_DIFFERENCE:
        base_labels = insight.view_labels_baseline or []
        base_values = insight.view_values_baseline or []
        sub_labels = labels
        sub_values = values

        all_cats = list(dict.fromkeys(base_labels + sub_labels))
        show_n = min(15, len(all_cats))
        all_cats = all_cats[:show_n]

        base_map = dict(zip(base_labels, base_values))
        sub_map = dict(zip(sub_labels, sub_values))
        base_v = [base_map.get(c, 0) for c in all_cats]
        sub_v = [sub_map.get(c, 0) for c in all_cats]

        base_total = sum(base_v) or 1
        sub_total = sum(sub_v) or 1
        base_pct = [v / base_total * 100 for v in base_v]
        sub_pct = [v / sub_total * 100 for v in sub_v]

        show_cats = [_truncate_label(c, 18) for c in all_cats]
        x = np.arange(len(show_cats))
        bar_w = 0.35

        ax.bar(x - bar_w / 2, base_pct, bar_w, label="Overall",
               color=_ACCENT, edgecolor="#FFFFFF", linewidth=0.8, zorder=3)
        ax.bar(x + bar_w / 2, sub_pct, bar_w, label="Subspace",
               color=_ACCENT_TOP, edgecolor="#FFFFFF", linewidth=0.8, zorder=3)

        ax.set_xticks(list(x))
        ax.set_xticklabels(show_cats, rotation=40, ha="right", fontsize=8)
        ax.set_ylabel("% of total", fontsize=10, color=_LABEL_COLOR)
        ax.set_xlabel(insight.breakdown, fontsize=10, color=_LABEL_COLOR)
        ax.legend(fontsize=9, framealpha=0.9)

        filters_desc = ", ".join(f"{c}={v}" for c, v in insight.subspace.filters)
        ax.set_title(f"Distribution Difference: {insight.measure}\nby {insight.breakdown}  (filter: {_truncate_label(filters_desc, 40)})",
                     fontsize=12, fontweight="bold", color=_TITLE_COLOR, pad=14)

    else:
        show_labels = [_truncate_label(l) for l in labels[:n_bars]]
        colors = _bar_colors(values[:n_bars], n_bars)
        x_pos = range(len(show_labels))
        ax.bar(x_pos, values[:n_bars], color=colors, edgecolor="#FFFFFF",
               linewidth=0.8, width=0.65, zorder=3)
        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(show_labels, rotation=40, ha="right", fontsize=8)
        ax.set_title(f"{insight.measure} by {insight.breakdown}",
                     fontsize=13, fontweight="bold", color=_TITLE_COLOR, pad=14)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="#FFFFFF")
        plt.close()
        return save_path
    plt.close()
    return None
