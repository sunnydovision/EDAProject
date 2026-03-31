"""
QUGEN filters (Section 3.1.2):
1. Schema relevance: remove questions not semantically relevant to table schema (all-MiniLM-L6-v2).
2. Deduplication: remove duplicate Insight Cards by question similarity.
3. Simple-question filter: discard if question yields only one row when converted to SQL and executed.
"""

from __future__ import annotations

import re
from typing import Callable

import numpy as np

from .models import InsightCard, TableSchema


# Default threshold for schema relevance (cosine similarity)
DEFAULT_SCHEMA_RELEVANCE_THRESHOLD = 0.25
# Default threshold for dedup (cosine similarity above this = duplicate)
DEFAULT_DEDUP_SIMILARITY_THRESHOLD = 0.85


_ENCODER_CACHE = None

def _get_encoder():
    """Lazy load and cache sentence-transformers all-MiniLM-L6-v2 (paper)."""
    global _ENCODER_CACHE
    if _ENCODER_CACHE is None:
        from sentence_transformers import SentenceTransformer
        _ENCODER_CACHE = SentenceTransformer("all-MiniLM-L6-v2")
    return _ENCODER_CACHE


def filter_by_schema_relevance(
    cards: list[InsightCard],
    schema: TableSchema,
    threshold: float = DEFAULT_SCHEMA_RELEVANCE_THRESHOLD,
) -> list[InsightCard]:
    """
    Remove cards whose question is not semantically relevant to the table schema.
    Uses all-MiniLM-L6-v2 and cosine similarity (paper).
    """
    if not cards:
        return []
    try:
        model = _get_encoder()
    except Exception:
        # If sentence_transformers not available, skip this filter
        return cards

    # Schema text: table name + column names (and optionally descriptions)
    schema_parts = [schema.table_name]
    for col in schema.columns:
        schema_parts.append(col.get("name", ""))
        if col.get("description"):
            schema_parts.append(col["description"])
    schema_text = " ".join(schema_parts)

    questions = [c.question for c in cards]
    schema_emb = model.encode([schema_text], normalize_embeddings=True)
    q_emb = model.encode(questions, normalize_embeddings=True)
    sims = np.dot(q_emb, schema_emb.T).flatten()

    return [c for c, s in zip(cards, sims) if s >= threshold]


def filter_duplicates(
    cards: list[InsightCard],
    threshold: float = DEFAULT_DEDUP_SIMILARITY_THRESHOLD,
) -> list[InsightCard]:
    """
    Eliminate duplicate Insight Cards based on semantic similarity between questions.
    Keeps first of each duplicate cluster.
    """
    if len(cards) <= 1:
        return cards
    try:
        model = _get_encoder()
    except Exception:
        return cards

    questions = [c.question for c in cards]
    embs = model.encode(questions, normalize_embeddings=True)
    keep = []
    for i, card in enumerate(cards):
        is_dup = False
        for j in keep:
            sim = float(np.dot(embs[i], embs[j]))
            if sim >= threshold:
                is_dup = True
                break
        if not is_dup:
            keep.append(i)
    return [cards[i] for i in keep]


def filter_simple_questions(
    cards: list[InsightCard],
    run_query_fn: Callable[[str], int] | None = None,
) -> list[InsightCard]:
    """
    Discard simple/rudimentary questions: convert to SQL, run on dataset;
    if result has only one row, discard (paper).
    run_query_fn(question) should return the number of rows returned by the query.
    If run_query_fn is None, we do a heuristic filter only (e.g. very short or single-value questions).
    """
    if run_query_fn is None:
        return _filter_simple_heuristic(cards)

    kept = []
    for c in cards:
        try:
            num_rows = run_query_fn(c.question)
            if num_rows is not None and num_rows > 1:
                kept.append(c)
            elif num_rows is None:
                kept.append(c)  # On error, keep
        except Exception:
            kept.append(c)
    return kept


def _filter_simple_heuristic(cards: list[InsightCard]) -> list[InsightCard]:
    """
    Heuristic when no SQL execution is available: drop very short questions
    or those that look like "what is the single X" (max/min one value).
    """
    kept = []
    for c in cards:
        q = c.question.strip().lower()
        if len(q) < 15:
            continue
        # Drop "what is the maximum/minimum/count of ..." that often yield one row
        if re.match(r"^what is the (total )?(number of|count of) ", q) and len(q) < 60:
            continue
        kept.append(c)
    return kept
