#!/usr/bin/env python3
"""
Run ISGEN: input = CSV + Insight Cards (JSON from QUGEN), output = Insight Summary (JSON + optional plots).
Usage:
  python run_isgen.py --csv data/transactions.csv --insight-cards insight_cards.json --output insights_summary.json
  python run_isgen.py --csv data/transactions.csv --insight-cards insight_cards.json --output insights_summary.json --plot-dir plots
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pandas as pd

from quis.isgen.pipeline import ISGENPipeline, ISGENConfig

def _get_llm():
    try:
        from quis.qugen.llm_client import get_default_llm_client
        return get_default_llm_client(use_mock=False)
    except Exception:
        return None


def load_cards(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


def main():
    parser = argparse.ArgumentParser(description="ISGEN: Insight Generation from Insight Cards")
    parser.add_argument("--csv", type=str, required=True, help="Path to CSV dataset")
    parser.add_argument("--insight-cards", type=str, default="insight_cards.json", help="Path to Insight Cards JSON from QUGEN")
    parser.add_argument("--output", type=str, default="insights_summary.json", help="Output JSON path")
    parser.add_argument("--plot-dir", type=str, default=None, help="Directory to save insight plots")
    parser.add_argument("--beam-width", type=int, default=20, help="Beam width for subspace search")
    parser.add_argument("--exp-factor", type=int, default=20, help="Expansion factor per beam step")
    parser.add_argument("--max-depth", type=int, default=1, help="Max subspace depth")
    parser.add_argument("--no-subspace", action="store_true", help="Skip subspace search (only basic insights)")
    parser.add_argument("--no-llm", action="store_true", help="Subspace search không gọi OpenAI (chạy ngay, không tốn API/tránh 429)")
    parser.add_argument("--max-overall-per-key", type=int, default=1, help="Mỗi (câu hỏi, breakdown, measure, pattern) giữ tối đa N insight overall (mặc định 1)")
    parser.add_argument("--max-subspace-per-key", type=int, default=2, help="Mỗi nhóm giữ tối đa N insight subspace (mặc định 2)")
    parser.add_argument("--max-insights-per-question", type=int, default=2, help="Mỗi question chỉ giữ tối đa N insight (mặc định 2, tránh trùng câu hỏi)")
    args = parser.parse_args()

    if not os.path.isfile(args.csv):
        print(f"CSV not found: {args.csv}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.insight_cards):
        print(f"Insight cards not found: {args.insight_cards}", file=sys.stderr)
        sys.exit(1)

    with open(args.csv, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    df = pd.read_csv(args.csv, sep=sep, decimal="," if sep == ";" else ".")

    # Clean currency ($), percentage (%), and European number formatting so columns become numeric
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna().head(20).astype(str).str.strip()
            # Detect columns that look numeric: digits with optional $, %, dots, commas
            numeric_like = sample.str.match(r"^\$?\s*[\d.,]+\s*%?$")
            if numeric_like.sum() >= len(sample) * 0.8:
                cleaned = df[col].astype(str).str.replace(r"[$%]", "", regex=True).str.strip()
                if sep == ";":
                    cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
                converted = pd.to_numeric(cleaned, errors="coerce")
                if converted.notna().sum() >= len(df) * 0.5:
                    df[col] = converted

    cards = load_cards(args.insight_cards)
    config = ISGENConfig(
        beam_width=args.beam_width,
        exp_factor=args.exp_factor,
        max_depth=args.max_depth,
        run_subspace_search=not args.no_subspace,
        plot_dir=args.plot_dir,
        max_overall_per_key=args.max_overall_per_key,
        max_subspace_per_key=args.max_subspace_per_key,
        max_insights_per_question=args.max_insights_per_question,
    )
    llm = None if args.no_llm else (_get_llm() if config.run_subspace_search else None)
    pipeline = ISGENPipeline(config=config, llm_client=llm)
    summary = pipeline.run(df, cards, output_dir=args.plot_dir)

    out_data = []
    for s in summary:
        out_data.append({
            "question": s.get("question", ""),
            "explanation": s.get("explanation", ""),
            "plot_path": s.get("plot_path"),
            "insight": s.get("insight", {}),
        })
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(out_data)} insights to {args.output}" + (f", plots in {args.plot_dir}" if args.plot_dir else ""))


if __name__ == "__main__":
    main()
