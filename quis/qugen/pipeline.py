"""
QUGEN pipeline: iterative question generation with filtering (paper Section 3.1.2).
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass, field
from typing import Callable

from .models import InsightCard, TableSchema
from .prompts import build_qugen_prompt
from .llm_client import BaseLLMClient, get_default_llm_client
from .parser import parse_insight_cards_from_text
from .filters import (
    filter_by_schema_relevance,
    filter_duplicates,
    filter_simple_questions,
    filter_invalid_measures,
)
from .stats import BasicStatsGenerator
from .examples import get_default_few_shot_examples


@dataclass
class QUGENConfig:
    """Parameters for QUGEN (paper Appendix D.2)."""

    temperature: float = 1.1
    num_samples_per_iteration: int = 3
    num_iterations: int = 10
    num_in_context_examples: int = 6
    num_questions_per_prompt: int = 10
    # Filter thresholds
    schema_relevance_threshold: float = 0.25
    dedup_similarity_threshold: float = 0.85
    # Optional: callable(question) -> row_count for simple-question filter; None = heuristic only
    run_query_fn: Callable[[str], int] | None = None


class QUGENPipeline:
    """
    QUGEN pipeline: generates Insight Cards in iterations, refining with in-context examples.
    Input: TableSchema + optional dataframe (for basic stats); Output: list of InsightCard.
    """

    def __init__(
        self,
        config: QUGENConfig | None = None,
        llm_client: BaseLLMClient | None = None,
        few_shot_examples: list[tuple[TableSchema, list[InsightCard]]] | None = None,
    ):
        self.config = config or QUGENConfig()
        self.llm = llm_client or get_default_llm_client()
        self.few_shot = few_shot_examples or get_default_few_shot_examples()
        self.stats_generator = BasicStatsGenerator(llm_client=self.llm)

    def _get_natural_language_stats(
        self,
        table_schema: TableSchema,
        df=None,
    ) -> str:
        try:
            return self.stats_generator.generate(table_schema, df)
        except Exception:
            return "Basic statistics could not be generated."

    @staticmethod
    def _extract_measure_col(measure: str) -> str:
        import re
        m = re.match(r"(?:SUM|MEAN|COUNT|MIN|MAX)\s*\(\s*([^)]+)\s*\)", measure, re.IGNORECASE)
        return m.group(1).strip() if m else measure.strip()

    def _select_in_context_examples(
        self,
        pool: list[InsightCard],
        n: int,
        table_schema: TableSchema,
    ) -> list[tuple[TableSchema, list[InsightCard]]]:
        """Select up to n Insight Cards from pool, prioritising measure diversity."""
        if not pool or n <= 0:
            return self.few_shot

        seen_measures: set[str] = set()
        diverse: list[InsightCard] = []
        rest: list[InsightCard] = []

        shuffled = list(pool)
        random.shuffle(shuffled)
        for card in shuffled:
            mcol = self._extract_measure_col(card.measure)
            if mcol not in seen_measures:
                diverse.append(card)
                seen_measures.add(mcol)
            else:
                rest.append(card)

        selected = (diverse + rest)[:n]
        return [(table_schema, selected)] + self.few_shot

    def run_one_iteration(
        self,
        table_schema: TableSchema,
        natural_language_stats: str,
        in_context_examples: list[tuple[TableSchema, list[InsightCard]]],
        run_query_fn: Callable[[str], int] | None = None,
        used_measures: list[str] | None = None,
    ) -> list[InsightCard]:
        """
        One QUGEN iteration: prompt LLM s times, parse, filter, return new cards.
        """
        prompt = build_qugen_prompt(
            table_schema=table_schema,
            natural_language_stats=natural_language_stats,
            example_schemas_and_cards=in_context_examples,
            num_questions=self.config.num_questions_per_prompt,
            used_measures=used_measures,
        )

        raw_outputs = self.llm.complete_multi(
            prompt,
            num_samples=self.config.num_samples_per_iteration,
            temperature=self.config.temperature,
            max_tokens=2048,
        )

        all_cards: list[InsightCard] = []
        for text in raw_outputs:
            all_cards.extend(parse_insight_cards_from_text(text))

        # Debug: khi parse ra 0 card, ghi phản hồi thô để kiểm tra định dạng LLM
        if not all_cards and raw_outputs:
            try:
                debug_path = os.path.join(os.path.dirname(__file__), "..", "..", "debug_llm_response.txt")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(raw_outputs[0])
            except Exception:
                pass

        # Filters (paper order)
        all_cards = filter_by_schema_relevance(
            all_cards,
            table_schema,
            threshold=self.config.schema_relevance_threshold,
        )
        all_cards = filter_duplicates(all_cards, threshold=self.config.dedup_similarity_threshold)
        qfn = run_query_fn if run_query_fn is not None else self.config.run_query_fn
        all_cards = filter_simple_questions(all_cards, run_query_fn=qfn)
        all_cards = filter_invalid_measures(all_cards, table_schema)

        return all_cards

    def run(
        self,
        table_schema: TableSchema,
        df=None,
    ) -> list[InsightCard]:
        """
        Full QUGEN pipeline: multiple iterations, accumulating Insight Cards.
        After normal iterations, if measure diversity is low (>50% same column),
        run an extra diversity iteration explicitly avoiding overused measures.
        """
        nl_stats = self._get_natural_language_stats(table_schema, df)

        run_query_fn = self.config.run_query_fn
        if run_query_fn is None and df is not None:
            run_query_fn = _make_simple_row_count_fn(df)

        config = self.config
        pool: list[InsightCard] = []
        in_context = self.few_shot

        for _ in range(config.num_iterations):
            used_measures = [self._extract_measure_col(c.measure) for c in pool]
            new_cards = self.run_one_iteration(
                table_schema=table_schema,
                natural_language_stats=nl_stats,
                in_context_examples=in_context,
                run_query_fn=run_query_fn,
                used_measures=used_measures if pool else None,
            )
            pool.extend(new_cards)
            pool = filter_duplicates(pool, threshold=config.dedup_similarity_threshold)
            in_context = self._select_in_context_examples(
                pool,
                config.num_in_context_examples,
                table_schema,
            )

        pool = self._enforce_measure_diversity(
            pool, table_schema, nl_stats, run_query_fn,
        )
        return pool

    def _enforce_measure_diversity(
        self,
        pool: list[InsightCard],
        table_schema: TableSchema,
        nl_stats: str,
        run_query_fn,
    ) -> list[InsightCard]:
        """If >50% of cards share the same measure column, run one extra iteration avoiding it."""
        if len(pool) < 4:
            return pool
        from collections import Counter
        measure_counts = Counter(self._extract_measure_col(c.measure) for c in pool)
        top_measure, top_count = measure_counts.most_common(1)[0]
        if top_count / len(pool) <= 0.5:
            return pool

        overused = [m for m, cnt in measure_counts.items() if cnt / len(pool) > 0.25]
        in_context = self._select_in_context_examples(
            pool, self.config.num_in_context_examples, table_schema,
        )
        extra = self.run_one_iteration(
            table_schema=table_schema,
            natural_language_stats=nl_stats,
            in_context_examples=in_context,
            run_query_fn=run_query_fn,
            used_measures=overused,
        )
        pool.extend(extra)
        pool = filter_duplicates(pool, threshold=self.config.dedup_similarity_threshold)
        return pool


def _make_simple_row_count_fn(df):
    """Return a callable(question) -> number of rows, using simple heuristics (no full text2sql)."""
    import pandas as pd

    def row_count(_question: str) -> int:
        try:
            # Placeholder: run a trivial aggregation that returns one row per group count
            # Real implementation would use text2sql. For now return 2 so we don't filter out.
            return 2
        except Exception:
            return 2

    return row_count
