#!/usr/bin/env python3
"""
Run QUGEN pipeline: input = schema (or CSV path), output = list of Insight Cards (JSON).
Usage:
  python run_qugen.py --csv data/transactions_cleaned.csv --output insight_cards.json
  python run_qugen.py --schema data/transactions_schema.json --output insight_cards.json

Requires: OPENAI_API_KEY (or OPENAI_API_BASE) for real LLM calls; sentence-transformers for filters.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env (OPENAI_API_KEY, OPENAI_API_BASE, QUGEN_LLM_MODEL) nếu có
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ẩn cảnh báo urllib3/LibreSSL trên macOS (không ảnh hưởng kết nối API)
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

import pandas as pd

from quis.shared.data_loader import load_data
from quis.qugen.pipeline import QUGENPipeline, QUGENConfig
from quis.qugen.models import schema_from_dataframe, TableSchema, InsightCard
from quis.qugen.llm_client import get_default_llm_client


def load_schema_from_json(path_or_json: str) -> TableSchema:
    if path_or_json.strip().startswith("{"):
        d = json.loads(path_or_json)
    else:
        with open(path_or_json, "r", encoding="utf-8") as f:
            d = json.load(f)
    return TableSchema(
        table_name=d.get("table_name", "Table"),
        columns=d.get("columns", []),
    )


def main():
    parser = argparse.ArgumentParser(description="QUGEN: Question Generation for QUIS")
    parser.add_argument("--csv", type=str, help="Path to CSV file (schema inferred from dataframe)")
    parser.add_argument("--schema", type=str, help="Path to JSON schema file or inline JSON object")
    parser.add_argument("--output", type=str, default="insight_cards.json", help="Output JSON path")
    parser.add_argument("--iterations", type=int, default=10, help="Number of QUGEN iterations")
    parser.add_argument("--samples", type=int, default=3, help="Samples per iteration")
    parser.add_argument("--temperature", type=float, default=1.1, help="LLM temperature")
    parser.add_argument("--in-context", type=int, default=6, help="Number of in-context example cards")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock LLM (no API calls; for dry-run / offline)",
    )
    args = parser.parse_args()

    if not args.csv and not args.schema:
        parser.error("Provide either --csv or --schema")

    if args.csv:
        # Load CSV using shared data loader (includes validation)
        df = load_data(args.csv)
        table_schema = schema_from_dataframe(df, table_name=os.path.splitext(os.path.basename(args.csv))[0])
    else:
        table_schema = load_schema_from_json(args.schema)
        df = None

    config = QUGENConfig(
        temperature=args.temperature,
        num_samples_per_iteration=args.samples,
        num_iterations=args.iterations,
        num_in_context_examples=args.in_context,
    )

    if (
        not args.mock
        and not os.getenv("OPENAI_API_KEY")
        and not os.getenv("OPENAI_API_BASE")
    ):
        parser.error("OPENAI_API_KEY (hoặc OPENAI_API_BASE) là bắt buộc. Project chỉ chạy với API thật.")

    llm_client = get_default_llm_client(use_mock=args.mock)
    pipeline = QUGENPipeline(config=config, llm_client=llm_client)
    cards = pipeline.run(table_schema=table_schema, df=df)

    # Loại card trùng question (QUGEN đôi khi sinh cùng câu hỏi nhiều lần)
    seen_questions: set[str] = set()
    unique_cards = []
    for c in cards:
        q = (c.question or "").strip()
        q_norm = " ".join(q.lower().split())
        if q_norm and q_norm not in seen_questions:
            seen_questions.add(q_norm)
            unique_cards.append(c)
        elif not q_norm:
            unique_cards.append(c)
    cards = unique_cards

    out_data = [c.to_dict() for c in cards]
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(out_data)} Insight Cards to {args.output}")


if __name__ == "__main__":
    main()
