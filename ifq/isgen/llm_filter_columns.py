"""
LLM suggests candidate filter columns for subspace expansion (paper 3.2.2).
"""

from __future__ import annotations

from typing import Any


def get_filter_column_candidates(
    breakdown: str,
    measure: str,
    available_columns: list[str],
    llm_client: Any = None,
    top_k: int = 5,
) -> list[str]:
    """
    Prompt LLM with (B, M) to return candidate columns that can lead to semantically meaningful insights.
    Returns list of column names (subset of available_columns). If no LLM, return empty (all columns equally likely).
    """
    if not llm_client or not available_columns:
        return []
    prompt = f"""Given a data analysis with breakdown dimension "{breakdown}" and measure "{measure}",
which of the following columns would be most meaningful to filter on for deeper insights?
Return only column names from this list, one per line, no explanation:
{chr(10).join(available_columns[:50])}"""
    try:
        resp = llm_client.complete(prompt, temperature=0.2, max_tokens=200)
        candidates = []
        for line in resp.strip().split("\n"):
            col = line.strip().strip(".-").strip()
            if col in available_columns and col not in candidates:
                candidates.append(col)
                if len(candidates) >= top_k:
                    break
        return candidates
    except Exception:
        # 429 rate limit hoặc lỗi API khác → fallback: không dùng gợi ý LLM, subspace vẫn chạy
        return []
