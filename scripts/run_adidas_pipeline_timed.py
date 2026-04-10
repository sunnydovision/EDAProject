#!/usr/bin/env python3
"""
Full Adidas pipeline: QUGEN (question/cards) → ISGEN (insights), with timing.
Usage: python scripts/run_adidas_pipeline_timed.py [--suffix 2]
Outputs: insight_cards_adidas_{suffix}.json, insights_summary_adidas_{suffix}.json, adidas_pipeline_timing_{suffix}.txt
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QUGEN + ISGEN on data/Adidas.csv with timing.")
    parser.add_argument("--suffix", default="2", help="File suffix, e.g. 2 → *_adidas_2.json")
    args = parser.parse_args()
    suf = args.suffix.strip() or "2"

    os.chdir(ROOT)
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    cards_path = ROOT / f"insight_cards_adidas_{suf}.json"
    summary_path = ROOT / f"insights_summary_adidas_{suf}.json"
    timing_path = ROOT / f"adidas_pipeline_timing_{suf}.txt"

    csv_path = ROOT / "data" / "Adidas.csv"
    if not csv_path.is_file():
        print(f"Missing {csv_path}", file=sys.stderr)
        sys.exit(1)

    py = sys.executable
    t0 = time.perf_counter()
    r1 = subprocess.run(
        [py, str(ROOT / "run_qugen.py"), "--csv", str(csv_path), "--output", str(cards_path)],
        cwd=str(ROOT),
    )
    t1 = time.perf_counter()
    if r1.returncode != 0:
        sys.exit(r1.returncode)

    r2 = subprocess.run(
        [
            py,
            str(ROOT / "run_isgen.py"),
            "--csv",
            str(csv_path),
            "--insight-cards",
            str(cards_path),
            "--output",
            str(summary_path),
        ],
        cwd=str(ROOT),
    )
    t2 = time.perf_counter()
    if r2.returncode != 0:
        sys.exit(r2.returncode)

    q_sec = t1 - t0
    i_sec = t2 - t1
    total_sec = t2 - t0

    model = os.getenv("QUGEN_LLM_MODEL", "(default from llm_client)")
    lines = [
        "Adidas pipeline — QUGEN (questions/cards) → ISGEN (insights)",
        f"QUGEN_LLM_MODEL={model}",
        f"OPENAI_USE_RESPONSES_API={os.getenv('OPENAI_USE_RESPONSES_API', '')}",
        "",
        "Wall-clock seconds:",
        f"  QUGEN (question/card generation): {q_sec:.3f}",
        f"  ISGEN (insight generation):       {i_sec:.3f}",
        f"  Total (start → insights complete): {total_sec:.3f}",
        "",
        f"Outputs: {cards_path.name}, {summary_path.name}",
    ]
    text = "\n".join(lines) + "\n"
    timing_path.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
