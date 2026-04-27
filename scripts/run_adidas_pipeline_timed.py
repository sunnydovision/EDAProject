#!/usr/bin/env python3
"""
Full Adidas (cleaned) pipeline: QUGEN (question/cards) → ISGEN (insights), with timing + LLM token usage.
Usage: python scripts/run_adidas_pipeline_timed.py [--suffix v4] [--csv data/Adidas_cleaned.csv]
Outputs: quis_results/quis_{yyyymmdd_hhiiss}_{dataset}_{suffix}/insight_cards.json, insights_summary.json,
         timing.json, usage.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_usage(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _usage_tokens(d: dict) -> tuple[int, int, int, int]:
    """input, output, total, requests"""
    return (
        int(d.get("input_tokens", 0)),
        int(d.get("output_tokens", 0)),
        int(d.get("total_tokens", 0)),
        int(d.get("requests", 0)),
    )


def create_output_dir(csv_path: str, suffix: str, base_dir: str = "quis_results") -> Path:
    """Create timestamped output directory: {base_dir}/quis_{yyyymmdd_hhiiss}_{dataset}_{suffix}"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_name = csv_path.stem
    dir_name = f"quis_{timestamp}_{dataset_name}_{suffix}"
    output_dir = ROOT / base_dir / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_timing_json(output_dir: Path, total_time: float, qugen_time: float, isgen_time: float,
                     insights_generated: int, system: str = "quis") -> Path:
    """Save timing.json in format compatible with evaluation/metrics/time_to_insight.py"""
    throughput = insights_generated / total_time if total_time > 0 else 0
    
    timing_data = {
        system: {
            "total_time_seconds": total_time,
            "insights_generated": insights_generated,
            "throughput_insights_per_second": throughput,
            "step_times": {
                "qugen": qugen_time,
                "isgen": isgen_time
            }
        }
    }
    
    timing_path = output_dir / "timing.json"
    with open(timing_path, 'w', encoding='utf-8') as f:
        json.dump(timing_data, f, indent=2)
    return timing_path


def save_usage_json(output_dir: Path, usage_qugen: dict, usage_isgen: dict, model: str, 
                    system: str = "quis") -> Path:
    """Save usage.json in format compatible with evaluation/metrics/token_usage.py"""
    iq, oq, tq, rq = _usage_tokens(usage_qugen)
    ii, oi, ti, ri = _usage_tokens(usage_isgen)
    
    usage_data = {
        system: {
            "total": {
                "total_tokens": tq + ti,
                "input_tokens": iq + ii,
                "output_tokens": oq + oi,
                "requests": rq + ri,
                "model": model
            },
            "qugen": {
                "total_tokens": tq,
                "input_tokens": iq,
                "output_tokens": oq,
                "requests": rq
            },
            "isgen": {
                "total_tokens": ti,
                "input_tokens": ii,
                "output_tokens": oi,
                "requests": ri
            }
        }
    }
    
    usage_path = output_dir / "usage.json"
    with open(usage_path, 'w', encoding='utf-8') as f:
        json.dump(usage_data, f, indent=2)
    return usage_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run QUGEN + ISGEN on an Adidas CSV with timing.")
    parser.add_argument(
        "--suffix",
        default="v4",
        help="Output directory suffix, e.g. v4 → quis_results/quis_{timestamp}_{dataset}_v4/",
    )
    parser.add_argument(
        "--csv",
        default="data/Adidas_cleaned.csv",
        help="CSV path relative to project root (default: data/Adidas_cleaned.csv)",
    )
    args = parser.parse_args()
    suffix = args.suffix.strip() or "v4"

    os.chdir(ROOT)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    csv_path = (ROOT / args.csv).resolve() if not os.path.isabs(args.csv) else Path(args.csv).resolve()
    if not csv_path.is_file():
        print(f"Missing {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Create timestamped output directory
    output_dir = create_output_dir(csv_path, suffix)
    print(f"Output directory: {output_dir}")

    cards_path = output_dir / "insight_cards.json"
    summary_path = output_dir / "insights_summary.json"
    
    py = sys.executable
    usage_qugen_path = output_dir / "usage_qugen_temp.json"
    usage_isgen_path = output_dir / "usage_isgen_temp.json"

    t0 = time.perf_counter()
    env_q = os.environ.copy()
    env_q["IFQ_USAGE_OUTPUT"] = str(usage_qugen_path)
    r1 = subprocess.run(
        [py, str(ROOT / "scripts" / "run_qugen.py"), "--csv", str(csv_path), "--output", str(cards_path)],
        cwd=str(ROOT),
        env=env_q,
    )
    t1 = time.perf_counter()
    if r1.returncode != 0:
        sys.exit(r1.returncode)

    env_i = os.environ.copy()
    env_i["IFQ_USAGE_OUTPUT"] = str(usage_isgen_path)
    r2 = subprocess.run(
        [
            py,
            str(ROOT / "scripts" / "run_isgen.py"),
            "--csv",
            str(csv_path),
            "--insight-cards",
            str(cards_path),
            "--output",
            str(summary_path),
        ],
        cwd=str(ROOT),
        env=env_i,
    )
    t2 = time.perf_counter()
    if r2.returncode != 0:
        sys.exit(r2.returncode)

    q_sec = t1 - t0
    i_sec = t2 - t1
    total_sec = t2 - t0

    uq = _load_usage(usage_qugen_path)
    ui = _load_usage(usage_isgen_path)

    # Count insights generated
    insights_generated = 0
    if summary_path.is_file():
        with open(summary_path, encoding='utf-8') as f:
            summary = json.load(f)
            insights_generated = len(summary) if isinstance(summary, list) else 1

    # Save timing.json in evaluation-compatible format
    timing_path = save_timing_json(output_dir, total_sec, q_sec, i_sec, insights_generated, system="quis")
    print(f"Saved timing: {timing_path}")

    # Save usage.json in evaluation-compatible format
    model = os.getenv("QUGEN_LLM_MODEL", "gpt-4o-mini")
    usage_path = save_usage_json(output_dir, uq, ui, model, system="quis")
    print(f"Saved usage: {usage_path}")

    # Clean up temp usage files
    usage_qugen_path.unlink(missing_ok=True)
    usage_isgen_path.unlink(missing_ok=True)

    # Print summary
    iq, oq, tq, rq = _usage_tokens(uq)
    ii, oi, ti, ri = _usage_tokens(ui)
    i_tot = iq + ii
    o_tot = oq + oi
    tok_tot = tq + ti
    req_tot = rq + ri

    print(f"\n{'='*70}")
    print("QUIS Pipeline Summary")
    print(f"{'='*70}")
    print(f"CSV: {csv_path}")
    print(f"QUGEN_LLM_MODEL={model}")
    print(f"OPENAI_USE_RESPONSES_API={os.getenv('OPENAI_USE_RESPONSES_API', '')}")
    print(f"\nWall-clock seconds:")
    print(f"  QUGEN (question/card generation): {q_sec:.3f}")
    print(f"  ISGEN (insight generation):       {i_sec:.3f}")
    print(f"  Total (start → insights complete): {total_sec:.3f}")
    print(f"\nLLM token usage:")
    print(f"  QUGEN:  input={iq:,}  output={oq:,}  total={tq:,}  requests={rq:,}")
    print(f"  ISGEN:  input={ii:,}  output={oi:,}  total={ti:,}  requests={ri:,}")
    print(f"  Sum:    input={i_tot:,}  output={o_tot:,}  total={tok_tot:,}  requests={req_tot:,}")
    print(f"\nInsights generated: {insights_generated}")
    print(f"\nOutputs:")
    print(f"  {cards_path.name}")
    print(f"  {summary_path.name}")
    print(f"  {timing_path.name}")
    print(f"  {usage_path.name}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
