"""
Subspace search (paper Algorithm 1): beam search, expand by (X, y), score with SCOREFUNC, keep top-k.
"""

from __future__ import annotations

import random
from typing import Callable

from .models import Subspace
from .views import compute_view


def _sample_value_weights(series):
    """P(yi) ∝ log(1 + N(yi))."""
    import pandas as pd
    counts = series.value_counts()
    log_weights = [max(0, __import__("math").log(1 + c)) for c in counts]
    total = sum(log_weights)
    if total == 0:
        return list(counts.index), [1.0 / len(counts)] * len(counts)
    return list(counts.index), [w / total for w in log_weights]


def subspace_search(
    df,
    breakdown: str,
    measure: str,
    score_func: Callable[[list[float]], float],
    threshold: float,
    beam_width: int = 20,
    exp_factor: int = 20,
    max_depth: int = 1,
    llm_candidates_fn: Callable[[list[str]], list[str]] | None = None,
    w_llm: float = 0.5,
) -> list[tuple[Subspace, float]]:
    """
    Algorithm 1: start with S0=empty, expand with (X,y), score view(D_S, B, M), keep top beam_width.
    llm_candidates_fn(available_cols) returns preferred columns for filtering (get higher probability w_llm).
    """
    all_cols = [c for c in df.columns if c != breakdown and str(c) != "nan"]
    if not all_cols:
        return []

    def score_subspace(S: Subspace) -> float:
        labels, values = compute_view(df, breakdown, measure, S)
        if len(values) < 2:
            return 0.0
        return score_func(values)

    llm_cols = set()
    if llm_candidates_fn:
        llm_cols = set(llm_candidates_fn(all_cols))

    def sample_column(available: list[str]) -> str:
        if not available:
            return random.choice(all_cols)
        if not llm_cols or random.random() > w_llm:
            return random.choice(available)
        preferred = [c for c in available if c in llm_cols]
        if preferred:
            return random.choice(preferred)
        return random.choice(available)

    beam: list[tuple[Subspace, float]] = [(Subspace.empty(), score_subspace(Subspace.empty()))]
    for depth in range(max_depth):
        new_beam = []
        for S, _ in beam:
            used = S.used_cols()
            available = [c for c in all_cols if c not in used]
            if not available:
                continue
            for _ in range(exp_factor):
                X = sample_column(available)
                if X not in df.columns:
                    continue
                vals, probs = _sample_value_weights(df[X].dropna())
                if not vals:
                    continue
                y = random.choices(vals, weights=probs, k=1)[0]
                Snew = S.add(X, y)
                sc = score_subspace(Snew)
                new_beam.append((Snew, sc))
        if not new_beam:
            break
        new_beam.sort(key=lambda x: -x[1])
        beam = new_beam[:beam_width]

    return [(S, sc) for S, sc in beam if sc >= threshold]
