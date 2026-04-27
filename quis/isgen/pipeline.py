"""
ISGEN pipeline: load Insight Cards + DataFrame → Basic insight + Subspace search → NL explanation + Plotting → Insight Summary.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .models import Insight, Subspace
from .models import TREND, DISTRIBUTION_DIFFERENCE
from .views import compute_view, resolve_card_columns, parse_measure
from .scoring import score_view, get_threshold_scaled, score_dd_for_subspace
from .basic_insight import extract_basic_insights, _is_temporal_column
from .subspace_search import subspace_search
from .nl_explanation import explain_insight
from .plotting import plot_insight
from .llm_filter_columns import get_filter_column_candidates


def _deduplicate_insight_candidates(
    candidates: list[tuple[Any, str]],
    max_overall_per_key: int = 1,
    max_subspace_per_key: int = 2,
) -> list[tuple[Any, str]]:
    """
    Gom nhóm theo (question, breakdown, measure, pattern). Mỗi nhóm giữ tối đa:
    - max_overall_per_key insight có subspace rỗng (theo score cao),
    - max_subspace_per_key insight có subspace (theo score cao).
    candidates: list of (insight_dict, question). insight_dict phải có breakdown, measure, pattern, subspace, score.
    Returns list of (insight_dict, question) đã dedup.
    """
    from collections import defaultdict
    key_to_overall: dict[tuple, list[tuple[float, tuple]]] = defaultdict(list)
    key_to_subspace: dict[tuple, list[tuple[float, tuple]]] = defaultdict(list)
    for ins_d, q in candidates:
        ins = ins_d if isinstance(ins_d, dict) else getattr(ins_d, "insight", ins_d) or {}
        if not isinstance(ins, dict):
            ins = {"breakdown": getattr(ins_d, "breakdown", ""), "measure": getattr(ins_d, "measure", ""), "pattern": getattr(ins_d, "pattern", ""), "subspace": getattr(ins_d, "subspace", None) and getattr(getattr(ins_d, "subspace", None), "filters", []) or [], "score": getattr(ins_d, "score", 0)}
        b = ins.get("breakdown", "")
        m = ins.get("measure", "")
        p = ins.get("pattern", "")
        sub = ins.get("subspace") or []
        key = (q, b, m, p)
        score = float(ins.get("score") or 0)
        if not sub:
            key_to_overall[key].append((score, (ins_d, q)))
        else:
            key_to_subspace[key].append((score, (ins_d, q)))
    out: list[tuple[Any, str]] = []
    for key in key_to_overall:
        key_to_overall[key].sort(key=lambda x: -x[0])
        for _, item in key_to_overall[key][:max_overall_per_key]:
            out.append(item)
    for key in key_to_subspace:
        key_to_subspace[key].sort(key=lambda x: -x[0])
        for _, item in key_to_subspace[key][:max_subspace_per_key]:
            out.append(item)
    def _score(it):
        i = it[0]
        if isinstance(i, dict):
            return float(i.get("score") or 0)
        return float(getattr(i, "score", 0))
    out.sort(key=lambda item: -_score(item))
    return out


def _limit_per_question(
    candidates: list[tuple[Any, str]],
    max_per_question: int,
) -> list[tuple[Any, str]]:
    """
    Mỗi question chỉ giữ tối đa max_per_question insight. Ưu tiên **đa dạng pattern**:
    chọn tối đa 1 insight (score cao nhất) cho mỗi pattern trước, rồi fill phần còn lại theo score.
    """
    from collections import defaultdict
    by_question: dict[str, list[tuple[float, str, tuple]]] = defaultdict(list)
    for ins_d, q in candidates:
        ins = ins_d if isinstance(ins_d, dict) else {}
        score = float(ins.get("score", 0)) if isinstance(ins, dict) else float(getattr(ins_d, "score", 0))
        pattern = (ins.get("pattern", "") if isinstance(ins, dict) else getattr(ins_d, "pattern", ""))
        by_question[q].append((score, pattern, (ins_d, q)))
    out: list[tuple[Any, str]] = []
    for q in by_question:
        items = by_question[q]
        items.sort(key=lambda x: -x[0])
        selected: list[tuple[Any, str]] = []
        used_patterns: set[str] = set()
        # Round 1: best per pattern (diversity)
        for sc, pat, item in items:
            if pat not in used_patterns and len(selected) < max_per_question:
                selected.append(item)
                used_patterns.add(pat)
        # Round 2: fill remaining slots by score
        for sc, pat, item in items:
            if len(selected) >= max_per_question:
                break
            if item not in selected:
                selected.append(item)
        out.extend(selected)
    def _score(it):
        i = it[0]
        return float(i.get("score", 0) if isinstance(i, dict) else getattr(i, "score", 0))
    out.sort(key=lambda item: -_score(item))
    return out


@dataclass
class ISGENConfig:
    """Parameters (paper Appendix D.2)."""
    beam_width: int = 20
    exp_factor: int = 20
    max_depth: int = 1
    w_llm: float = 1.0
    run_subspace_search: bool = True
    max_insights_per_card: int = 3
    plot_dir: str | None = None
    # Giới hạn trùng: mỗi (question, breakdown, measure, pattern) giữ tối đa 1 overall + 2 subspace
    max_overall_per_key: int = 1
    max_subspace_per_key: int = 2
    # Mỗi question chỉ xuất tối đa N insight (ưu tiên đa dạng pattern: 1 OV + 1 Attr + 1 Trend...)
    max_insights_per_question: int = 3
    # UI demo: relax thresholds to avoid returning empty insights
    threshold_scale: float = 0.7


class ISGENPipeline:
    """
    Full ISGEN: for each Insight Card → basic insights + subspace insights → filter interesting → NL + plot → summary.
    """

    def __init__(self, config: ISGENConfig | None = None, llm_client=None):
        self.config = config or ISGENConfig()
        self.llm = llm_client

    def _llm_candidates(self, breakdown: str, measure: str, available: list[str]) -> list[str]:
        if not self.llm:
            return []
        return get_filter_column_candidates(breakdown, measure, available, self.llm, top_k=5)

    def run(self, df, cards: list[dict], output_dir: str | None = None) -> list[dict]:
        """
        Run ISGEN on DataFrame and list of Insight Cards (each dict: question, reason, breakdown, measure).
        Thu thập hết candidate → deduplicate → chỉ với insight được giữ mới ghi plot và đưa vào summary.
        Returns list of insight summary dicts: { insight, explanation, plot_path, card_question }.
        """
        plot_dir = output_dir or self.config.plot_dir
        if plot_dir:
            os.makedirs(plot_dir, exist_ok=True)
        candidates: list[tuple[Any, str]] = []
        seen = set()
        df_columns = list(df.columns)
        for idx, card in enumerate(cards):
            card_resolved = resolve_card_columns(card, df_columns)
            if card_resolved is None:
                continue
            breakdown = card_resolved.get("breakdown", "").strip()
            measure = card_resolved.get("measure", "").strip()
            if not breakdown or not measure:
                continue
            if breakdown not in df.columns:
                continue
            # Basic insights (use resolved column names)
            basic = extract_basic_insights(
                df,
                card_resolved,
                max_per_card=self.config.max_insights_per_card,
                threshold_scale=self.config.threshold_scale,
            )
            for ins in basic:
                key = (ins.breakdown, ins.measure, tuple(ins.subspace.filters), ins.pattern)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append((ins.to_dict(), card_resolved.get("question", "")))
                if len(candidates) >= 200:
                    break
            # Subspace search: OV, Attribution, Trend, và (nếu measure = COUNT) Distribution Difference
            if self.config.run_subspace_search and len(candidates) < 150:
                agg_name, _ = parse_measure(measure)
                patterns_subspace = ["Outstanding Value", "Attribution"]
                if breakdown in df.columns and _is_temporal_column(breakdown, df[breakdown]):
                    patterns_subspace.append(TREND)
                patterns_subspace.append(DISTRIBUTION_DIFFERENCE)
                for pattern in patterns_subspace:
                    th = get_threshold_scaled(pattern, self.config.threshold_scale)
                    cand_fn = lambda cols: self._llm_candidates(breakdown, measure, cols)
                    if pattern == DISTRIBUTION_DIFFERENCE:
                        dd_scorer = lambda S: score_dd_for_subspace(df, breakdown, measure, S)
                        subs = subspace_search(
                            df, breakdown, measure, lambda v: 0.0, th,
                            beam_width=self.config.beam_width,
                            exp_factor=self.config.exp_factor,
                            max_depth=self.config.max_depth,
                            llm_candidates_fn=cand_fn,
                            w_llm=self.config.w_llm,
                            score_func_subspace=dd_scorer,
                        )
                    else:
                        def _make_scf(p):
                            return lambda v: score_view(p, v)
                        scf = _make_scf(pattern)
                        subs = subspace_search(
                            df, breakdown, measure, scf, th,
                            beam_width=self.config.beam_width,
                            exp_factor=self.config.exp_factor,
                            max_depth=self.config.max_depth,
                            llm_candidates_fn=cand_fn,
                            w_llm=self.config.w_llm,
                        )
                    for S, sc in subs[:2]:
                        key = (breakdown, measure, S.filters, pattern)
                        if key in seen:
                            continue
                        labels, values = compute_view(df, breakdown, measure, S)
                        if len(values) < 2:
                            continue
                        if pattern == TREND and len(values) < 3:
                            continue
                        seen.add(key)
                        ins = Insight(breakdown=breakdown, measure=measure, subspace=S, pattern=pattern, score=sc, view_labels=labels, view_values=values, question=card_resolved.get("question", ""), reason=card_resolved.get("reason", ""))
                        if pattern == DISTRIBUTION_DIFFERENCE:
                            labels_base, values_base = compute_view(df, breakdown, measure, Subspace.empty())
                            ins.view_labels_baseline = labels_base
                            ins.view_values_baseline = values_base
                        candidates.append((ins.to_dict(), card_resolved.get("question", "")))
                        if len(candidates) >= 200:
                            break
                    if len(candidates) >= 200:
                        break
            if len(candidates) >= 200:
                break

        # Deduplicate: mỗi (question, breakdown, measure, pattern) giữ tối đa 1 overall + 2 subspace
        kept = _deduplicate_insight_candidates(
            candidates,
            max_overall_per_key=self.config.max_overall_per_key,
            max_subspace_per_key=self.config.max_subspace_per_key,
        )
        # Mỗi question chỉ giữ tối đa N insight (tránh cùng câu hỏi lặp)
        kept = _limit_per_question(kept, self.config.max_insights_per_question)
        # Chỉ với insight được giữ: tạo explanation, ghi plot, build summary
        summary = []
        for i, (ins_d, question) in enumerate(kept):
            # Reconstruct Insight for explain_insight/plot_insight (cần object có view_labels, view_values, subspace, pattern, ...)
            sub = ins_d.get("subspace") or []
            S = Subspace(filters=[(f[0], f[1]) for f in sub]) if sub else Subspace.empty()
            ins_obj = Insight(
                breakdown=ins_d.get("breakdown", ""),
                measure=ins_d.get("measure", ""),
                subspace=S,
                pattern=ins_d.get("pattern", ""),
                score=float(ins_d.get("score") or 0),
                view_labels=ins_d.get("view_labels") or [],
                view_values=ins_d.get("view_values") or [],
                view_values_baseline=ins_d.get("view_values_baseline"),
                view_labels_baseline=ins_d.get("view_labels_baseline"),
                question=question,
                reason=ins_d.get("reason", ""),
            )
            expl = explain_insight(ins_obj)
            plot_path = None
            if plot_dir:
                p = ins_d.get("pattern", "").replace(" ", "_")
                plot_path = os.path.join(plot_dir, f"insight_{i}_{p}.png")
                plot_insight(ins_obj, plot_path)
            summary.append({
                "insight": ins_d,
                "explanation": expl,
                "plot_path": plot_path,
                "question": question,
            })
        return summary
