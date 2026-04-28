#!/usr/bin/env python3
"""
Aggregate 3-way comparison results across multiple datasets.

Reads comparison_table_3way.csv from each dataset's results directory
and produces:
  - aggregated_summary.csv   : per-metric averages across datasets (for numeric metrics)
  - aggregated_per_dataset.csv : all datasets side-by-side (wide format)
  - aggregated_report.md     : human-readable report for paper/thesis

Usage:
    python evaluation/aggregate_results.py
    python evaluation/aggregate_results.py --datasets adidas employee_attrition online_sales
"""

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from typing import Optional

# ── project root ────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from evaluation.configs.eval_config import EvalConfig  # noqa: E402

# ── helpers ──────────────────────────────────────────────────────────────────

PERCENT_RE = re.compile(r"^([\d.]+)%")
FLOAT_RE = re.compile(r"^-?([\d]+\.[\d]+)$")
INT_RE = re.compile(r"^-?(\d+)$")
FRACTION_RE = re.compile(r"^(\d+)/(\d+)")
DELTA_RE = re.compile(r"Δ=([-\d.]+),\s*x=([-\d.]+)")
MEAN_STD_RE = re.compile(r"^([\d.]+)\s*±")


def parse_numeric(val: str) -> Optional[float]:
    """Try to extract a primary numeric value from a cell string.
    Returns None if the value is non-numeric / informational."""
    if not val or val.strip() in ("", "N/A", "Tie", "nan", "—"):
        return None
    v = val.strip()
    m = PERCENT_RE.match(v)
    if m:
        return float(m.group(1))
    m = FRACTION_RE.match(v)
    if m:
        num, den = int(m.group(1)), int(m.group(2))
        return 100.0 * num / den if den else None
    m = DELTA_RE.search(v)
    if m:
        return float(m.group(2))          # use the ratio (x=…) as primary value
    m = MEAN_STD_RE.match(v)
    if m:
        return float(m.group(1))          # use the mean from "mean ± std"
    m = FLOAT_RE.match(v)
    if m:
        return float(v)
    m = INT_RE.match(v)
    if m:
        return float(v)
    return None


def safe_mean(values: list) -> Optional[float]:
    nums = [v for v in values if v is not None and not math.isnan(v)]
    return sum(nums) / len(nums) if nums else None


def fmt(val: Optional[float], is_pct: bool = False) -> str:
    if val is None:
        return "N/A"
    if is_pct:
        return f"{val:.1f}%"
    return f"{val:.4f}"


def is_pct_metric(raw_val: str) -> bool:
    """Heuristic: original cell was a percentage."""
    if not raw_val:
        return False
    return bool(PERCENT_RE.match(raw_val.strip())) or bool(FRACTION_RE.match(raw_val.strip()))


# ── metric classification ─────────────────────────────────────────────────

# Metrics where we average numeric values across datasets
AVERAGE_METRICS = {
    "1. Faithfulness",
    "2. Statistical Significance (Overall)",
    "2a. Significance — TREND",
    "2a. Significance — OUTSTANDING_VALUE",
    "2a. Significance — ATTRIBUTION",
    "2a. Significance — DISTRIBUTION_DIFFERENCE",
    "3. Insight Novelty",
    "4a. Diversity — Semantic",
    "4b. Diversity — Subspace Entropy",
    "4c. Diversity — Value",
    "4d. Diversity — Dedup Rate",
    "7. Subspace Rate",
    "7a. Subspace Faithfulness",
    "7b. Subspace Significance",
    "10a. BM — NMI mean",
    "10b. BM — Interestingness",
    "10c. BM — Actionability",
    "10d. BM — Diversity",
    "11a. Question Semantic Diversity",
    "11b. Question Specificity",
    "11c. Question–Insight Alignment",
    "11d. Question Novelty (cross-system)",
    "11e. Reason–Insight Coherence",
    "12. Structural Validity Rate",
}

# Metrics kept per-dataset (totals / fractions / textual)
PER_DATASET_ONLY = {
    "0. Total insights",
    "2b. Pattern Coverage",
    "2b1. Uncovered Patterns",
    "8. Score Uplift from Subspace",
    "10. Total (B,M) pairs evaluated",
    "12a. SVR — OUTSTANDING_VALUE",
    "12a. SVR — TREND",
    "12a. SVR — ATTRIBUTION",
    "12a. SVR — DISTRIBUTION_DIFFERENCE",
}

SYSTEMS = ["QUIS", "Baseline", "ONLYSTATS"]


# ── winner determination ──────────────────────────────────────────────────

# For these metrics lower is better
LOWER_IS_BETTER = {"4d. Diversity — Dedup Rate"}


def determine_winner(metric: str, values: dict) -> str:
    """Determine winner from averaged values dict {system: float|None}."""
    nums = {s: v for s, v in values.items() if v is not None}
    if not nums:
        return "N/A"
    if len(set(nums.values())) == 1:
        return "Tie"
    best_fn = min if metric in LOWER_IS_BETTER else max
    best_val = best_fn(nums.values())
    winners = [s for s, v in nums.items() if v == best_val]
    return winners[0] if len(winners) == 1 else "Tie"


# ── main ──────────────────────────────────────────────────────────────────

def load_table(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if any(row.values()):
                rows.append(dict(row))
    return rows


def aggregate(datasets: list[str], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    # ── load all tables ───────────────────────────────────────────────────
    tables: dict[str, list[dict]] = {}
    for ds in datasets:
        path = os.path.join(PROJECT_ROOT, "evaluation", "evaluation_results", ds, "comparison_table_3way.csv")
        if not os.path.exists(path):
            print(f"  ⚠  Missing: {path} — skipping {ds}")
            continue
        tables[ds] = load_table(path)
        print(f"  ✓  Loaded {ds}: {len(tables[ds])} rows")

    if not tables:
        print("No tables found. Aborting.")
        return

    # Build an ordered list of (group, metric, description) from first table
    first = next(iter(tables.values()))
    ordered_metrics = [(r["Group"], r["Metric"], r.get("Description", "")) for r in first if r.get("Metric")]

    # metric → dataset → {system: raw_value}
    data: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for ds, rows in tables.items():
        for row in rows:
            m = row.get("Metric", "").strip()
            if not m:
                continue
            data[m][ds] = {s: row.get(s, "") for s in SYSTEMS}

    # ── aggregated_summary.csv  (avg across datasets) ─────────────────────
    summary_rows = []
    for group, metric, desc in ordered_metrics:
        avg_vals: dict[str, float | None] = {}
        is_pct_hint = False
        for sys in SYSTEMS:
            raw_list = []
            for ds in tables:
                raw = data.get(metric, {}).get(ds, {}).get(sys, "")
                raw_list.append(raw)
                if raw and not is_pct_hint:
                    is_pct_hint = is_pct_metric(raw)
            nums = [parse_numeric(r) for r in raw_list]
            avg_vals[sys] = safe_mean(nums)

        if metric in AVERAGE_METRICS:
            winner = determine_winner(metric, avg_vals)
            summary_rows.append({
                "Group": group,
                "Metric": metric,
                "QUIS": fmt(avg_vals["QUIS"], is_pct_hint),
                "Baseline": fmt(avg_vals["Baseline"], is_pct_hint),
                "ONLYSTATS": fmt(avg_vals["ONLYSTATS"], is_pct_hint),
                "Winner": winner,
                "Description": desc,
                "Aggregation": f"avg over {len(tables)} datasets",
            })
        else:
            # Keep per-dataset rows
            for ds in tables:
                ds_vals = data.get(metric, {}).get(ds, {})
                summary_rows.append({
                    "Group": group,
                    "Metric": metric,
                    "QUIS": ds_vals.get("QUIS", ""),
                    "Baseline": ds_vals.get("Baseline", ""),
                    "ONLYSTATS": ds_vals.get("ONLYSTATS", ""),
                    "Winner": data.get(metric, {}).get(ds, {}).get("Winner",
                              next((r.get("Winner","") for r in tables[ds] if r.get("Metric")==metric), "")),
                    "Description": desc,
                    "Aggregation": f"per-dataset ({ds})",
                })

    summary_path = os.path.join(output_dir, "aggregated_summary.csv")
    fieldnames = ["Group", "Metric", "QUIS", "Baseline", "ONLYSTATS", "Winner", "Description", "Aggregation"]
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"\n  ✓  aggregated_summary.csv  →  {summary_path}")

    # ── aggregated_per_dataset.csv  (wide, all datasets side-by-side) ──────
    wide_rows = []
    col_quis  = [f"QUIS_{ds}"  for ds in tables]
    col_base  = [f"Baseline_{ds}" for ds in tables]
    col_only  = [f"ONLYSTATS_{ds}" for ds in tables]
    extra_cols = col_quis + col_base + col_only

    for group, metric, desc in ordered_metrics:
        row: dict = {"Group": group, "Metric": metric}
        for ds in tables:
            ds_vals = data.get(metric, {}).get(ds, {})
            row[f"QUIS_{ds}"]      = ds_vals.get("QUIS", "")
            row[f"Baseline_{ds}"]  = ds_vals.get("Baseline", "")
            row[f"ONLYSTATS_{ds}"] = ds_vals.get("ONLYSTATS", "")

        # Avg columns for numeric metrics
        if metric in AVERAGE_METRICS:
            for sys in SYSTEMS:
                raw_list = [data.get(metric, {}).get(ds, {}).get(sys, "") for ds in tables]
                is_pct_hint = any(is_pct_metric(r) for r in raw_list if r)
                nums = [parse_numeric(r) for r in raw_list]
                row[f"AVG_{sys}"] = fmt(safe_mean(nums), is_pct_hint)
        else:
            for sys in SYSTEMS:
                row[f"AVG_{sys}"] = "—"

        row["Description"] = desc
        wide_rows.append(row)

    wide_path = os.path.join(output_dir, "aggregated_per_dataset.csv")
    wide_fields = ["Group", "Metric"] + extra_cols + ["AVG_QUIS", "AVG_Baseline", "AVG_ONLYSTATS", "Description"]
    with open(wide_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=wide_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(wide_rows)
    print(f"  ✓  aggregated_per_dataset.csv →  {wide_path}")

    # ── aggregated_report.md ───────────────────────────────────────────────
    _write_markdown_report(tables, ordered_metrics, data, output_dir, datasets)


def _write_markdown_report(tables, ordered_metrics, data, output_dir, datasets):
    ds_list = list(tables.keys())
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Aggregated 3-Way Evaluation Report",
        f"",
        f"Generated: {now}  ",
        f"Datasets: {', '.join(ds_list)}  ",
        f"Systems: QUIS | Baseline | ONLYSTATS",
        f"",
        f"> **Aggregation rules**",
        f"> - *Averaged metrics* (%) — mean across datasets reported in the summary table.",
        f"> - *Per-dataset metrics* (counts, fractions, text) — kept separately below.",
        f"",
    ]

    # ── Win count summary ─────────────────────────────────────────────────
    win_counts: dict[str, int] = {s: 0 for s in SYSTEMS}
    for group, metric, _ in ordered_metrics:
        if metric not in AVERAGE_METRICS:
            continue
        avg_vals: dict[str, float | None] = {}
        for sys in SYSTEMS:
            raw_list = [data.get(metric, {}).get(ds, {}).get(sys, "") for ds in ds_list]
            avg_vals[sys] = safe_mean([parse_numeric(r) for r in raw_list])
        w = determine_winner(metric, avg_vals)
        if w in win_counts:
            win_counts[w] += 1

    avg_metric_count = sum(1 for _, m, _ in ordered_metrics if m in AVERAGE_METRICS)
    lines += [
        f"## Win Count Summary (averaged metrics, {avg_metric_count} total)",
        f"",
        f"| System | Wins |",
        f"|--------|------|",
    ]
    for s, c in win_counts.items():
        lines.append(f"| {s} | {c} |")
    lines.append("")

    # ── Averaged metrics table ────────────────────────────────────────────
    current_group = None
    lines += [
        "## Averaged Metrics (mean across datasets)",
        "",
    ]

    for group, metric, desc in ordered_metrics:
        if metric not in AVERAGE_METRICS:
            continue
        if group != current_group:
            current_group = group
            lines += [
                f"### {group}",
                "",
                f"| Metric | QUIS | Baseline | ONLYSTATS | Winner | Description |",
                f"|--------|------|----------|-----------|--------|-------------|",
            ]
        avg_vals: dict[str, float | None] = {}
        is_pct_hint = False
        for sys in SYSTEMS:
            raw_list = [data.get(metric, {}).get(ds, {}).get(sys, "") for ds in ds_list]
            if not is_pct_hint:
                is_pct_hint = any(is_pct_metric(r) for r in raw_list if r)
            avg_vals[sys] = safe_mean([parse_numeric(r) for r in raw_list])
        winner = determine_winner(metric, avg_vals)
        row_vals = {s: fmt(avg_vals[s], is_pct_hint) for s in SYSTEMS}
        lines.append(
            f"| {metric} | {row_vals['QUIS']} | {row_vals['Baseline']} | {row_vals['ONLYSTATS']} | **{winner}** | {desc} |"
        )
    lines.append("")

    # ── Per-dataset breakdown for selected key metrics ─────────────────────
    lines += [
        "## Per-Dataset Detail (non-averaged metrics)",
        "",
    ]
    current_group = None
    for group, metric, desc in ordered_metrics:
        if metric not in PER_DATASET_ONLY:
            continue
        if group != current_group:
            current_group = group
            lines += [f"### {group}", ""]

        lines += [f"**{metric}** — {desc}", ""]
        lines += [
            f"| Dataset | QUIS | Baseline | ONLYSTATS |",
            f"|---------|------|----------|-----------|",
        ]
        for ds in ds_list:
            dv = data.get(metric, {}).get(ds, {})
            lines.append(
                f"| {ds} | {dv.get('QUIS','')} | {dv.get('Baseline','')} | {dv.get('ONLYSTATS','')} |"
            )
        lines.append("")

    # ── Per-dataset full table in appendix ────────────────────────────────
    lines += [
        "## Appendix — Full Results Per Dataset",
        "",
    ]
    for ds in ds_list:
        lines += [
            f"### {ds}",
            "",
            f"| Group | Metric | QUIS | Baseline | ONLYSTATS | Winner |",
            f"|-------|--------|------|----------|-----------|--------|",
        ]
        for group, metric, _ in ordered_metrics:
            dv = data.get(metric, {}).get(ds, {})
            winner_val = next(
                (r.get("Winner", "") for r in tables[ds] if r.get("Metric") == metric), ""
            )
            lines.append(
                f"| {group} | {metric} | {dv.get('QUIS','')} | {dv.get('Baseline','')} | {dv.get('ONLYSTATS','')} | {winner_val} |"
            )
        lines.append("")

    md_path = os.path.join(output_dir, "aggregated_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  ✓  aggregated_report.md      →  {md_path}")


# ── entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Aggregate 3-way comparison results across datasets.")
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=["adidas", "employee_attrition", "online_sales"],
        help="Datasets to include (default: adidas employee_attrition online_sales)",
    )
    parser.add_argument(
        "--output_dir",
        default=os.path.join(PROJECT_ROOT, "evaluation", "evaluation_results", "aggregated"),
        help="Directory to write aggregated outputs",
    )
    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"Aggregating 3-way results for: {', '.join(args.datasets)}")
    print(f"Output dir: {args.output_dir}")
    print(f"{'='*70}\n")

    aggregate(args.datasets, args.output_dir)

    print(f"\n✅ Done.\n")


if __name__ == "__main__":
    main()
