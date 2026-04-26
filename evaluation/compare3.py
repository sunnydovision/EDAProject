"""
Three-system comparison: QUIS vs Baseline vs ONLYSTATS.
Produces comparison_table_3way.csv with all metrics including SVR and Pattern Coverage.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metrics.pattern_coverage import compute_structural_validity, compute_pattern_coverage
from metrics.data_loader import load_and_clean_data
from compare import format_metric_value


def _winner3(names, values, higher_better=True):
    """Return best system name among 3, or 'Tie' if top 2 tied."""
    valid = [(n, v) for n, v in zip(names, values) if v is not None]
    if not valid:
        return 'N/A'
    if higher_better:
        best = max(v for _, v in valid)
    else:
        best = min(v for _, v in valid)
    winners = [n for n, v in valid if v == best]
    return winners[0] if len(winners) == 1 else 'Tie'


def create_comparison_table_3way(
    results_a: dict, results_b: dict, results_c: dict,
    name_a: str, name_b: str, name_c: str,
    insights_a: list, insights_b: list, insights_c: list,
    df_cleaned, profile_path: str | None = None,
) -> pd.DataFrame:
    names = [name_a, name_b, name_c]
    results_list = [results_a, results_b, results_c]
    metrics = []

    def row(group, metric, vals, winner, desc):
        d = {'Group': group, 'Metric': metric, 'Winner': winner, 'Description': desc}
        for n, v in zip(names, vals):
            d[n] = v
        metrics.append(d)

    # ── 0. Total insights ─────────────────────────────────────────────────
    totals = [r['num_insights'] for r in results_list]
    row('Core & Efficiency', '0. Total insights',
        [str(t) for t in totals], 'N/A', 'Total insight cards generated')

    # ── 1. Faithfulness ───────────────────────────────────────────────────
    fa = [r['faithfulness']['faithfulness'] for r in results_list]
    row('Core & Efficiency', '1. Faithfulness',
        [format_metric_value(v, 'percentage') for v in fa],
        _winner3(names, fa), 'Correctness - đúng dữ liệu')

    # ── 2. Statistical Significance (Overall, pattern-averaged) ───────────
    sig_all = [r['insight_significance'] for r in results_list]
    sig_vals = [s.get('pattern_avg_significance', s['significant_rate']) for s in sig_all]
    row('Core & Efficiency', '2. Statistical Significance (Overall)',
        [format_metric_value(v, 'percentage') for v in sig_vals],
        _winner3(names, sig_vals),
        'Validity - pattern-averaged (fair comparison)')

    # per-pattern significance
    for pattern in ['TREND', 'OUTSTANDING_VALUE', 'ATTRIBUTION', 'DISTRIBUTION_DIFFERENCE']:
        pv, pc_ = [], []
        for s in sig_all:
            bp = s.get('by_pattern', {}).get(pattern, {})
            pv.append(bp.get('significant_rate', 0) or 0)
            pc_.append(bp.get('total_count', 0))
        vals_str = [f"{v*100:.1f}% ({c})" if c > 0 else 'N/A' for v, c in zip(pv, pc_)]
        winner = _winner3(names, [v if c > 0 else None for v, c in zip(pv, pc_)])
        row('Core & Efficiency', f'2a. Significance — {pattern}',
            vals_str, winner, f'Validity - {pattern} pattern')

    # ── 2b. Pattern Coverage & 2b1 ────────────────────────────────────────
    pc_results = [
        compute_pattern_coverage(ins, df_cleaned, profile_path)
        for ins in [insights_a, insights_b, insights_c]
    ]
    cov_vals = [pc['pattern_coverage'] for pc in pc_results]
    cov_str = [
        f"{pc['covered_count']}/{pc['total_patterns']} ({pc['pattern_coverage']*100:.0f}%)"
        for pc in pc_results
    ]
    row('Core & Efficiency', '2b. Pattern Coverage',
        cov_str, _winner3(names, cov_vals),
        'Patterns with ≥1 structurally valid insight / 4 total patterns')
    uncov_str = [
        '—' if not pc['uncovered_patterns'] else ', '.join(pc['uncovered_patterns'])
        for pc in pc_results
    ]
    row('Core & Efficiency', '2b1. Uncovered Patterns',
        uncov_str, 'N/A', 'Patterns with 0 valid insights (breakdown type mismatch)')

    # ── 3. Insight Novelty ────────────────────────────────────────────────
    nov_vals = [r.get('insight_novelty', {}).get('novelty', 0) or 0 for r in results_list]
    row('Core & Efficiency', '3. Insight Novelty',
        [format_metric_value(v, 'percentage') for v in nov_vals],
        _winner3(names, nov_vals), 'Usefulness - khác baseline')

    # ── 4. Diversity ──────────────────────────────────────────────────────
    divs = [r.get('question_diversity', {}) for r in results_list]
    sem = [d.get('semantic_diversity', 0) or 0 for d in divs]
    row('Core & Efficiency', '4a. Diversity — Semantic',
        [format_metric_value(v, 'default') for v in sem],
        _winner3(names, sem), 'Semantic diversity (breakdown|measure|pattern|subspace)')

    sub_ent = [(d.get('subspace_diversity') or {}).get('subspace_diversity_entropy') for d in divs]
    row('Core & Efficiency', '4b. Diversity — Subspace Entropy',
        [format_metric_value(v, 'default') if v is not None else 'N/A' for v in sub_ent],
        _winner3(names, [v or 0 for v in sub_ent]),
        'Entropy of subspace filter columns used')

    val_div = [(d.get('value_diversity') or {}).get('value_diversity') for d in divs]
    row('Core & Efficiency', '4c. Diversity — Value',
        [format_metric_value(v, 'default') if v is not None else 'N/A' for v in val_div],
        _winner3(names, [v or 0 for v in val_div]),
        'Unique (column, value) pairs in subspace / total')

    dedup = [d.get('dedup_rate', 0) or 0 for d in divs]
    row('Core & Efficiency', '4d. Diversity — Dedup Rate',
        [format_metric_value(v, 'default') for v in dedup],
        _winner3(names, dedup, higher_better=False),
        'Duplicate rate — lower is better')

    # ── 7. Subspace metrics ───────────────────────────────────────────────
    subs = [r.get('subspace_metrics', {}) for r in results_list]
    tots = [r.get('num_insights', 1) or 1 for r in results_list]
    sub_cnts = [s.get('total_with_subspace', 0) for s in subs]
    sub_rates = [c / t for c, t in zip(sub_cnts, tots)]
    sub_str = [f"{c}/{t} ({r*100:.1f}%)" for c, t, r in zip(sub_cnts, tots, sub_rates)]
    row('Subspace Deep-dive', '7. Subspace Rate',
        sub_str, _winner3(names, sub_rates),
        'Insights with subspace filter / total')

    if all(s.get('faithfulness') for s in subs):
        sf = [s['faithfulness']['faithfulness'] for s in subs]
        row('Subspace Deep-dive', '7a. Subspace Faithfulness',
            [format_metric_value(v, 'percentage') for v in sf],
            _winner3(names, sf), 'Faithfulness restricted to subspace insights')

    if all(s.get('significance') for s in subs):
        ss = [s['significance']['significant_rate'] for s in subs]
        row('Subspace Deep-dive', '7b. Subspace Significance',
            [format_metric_value(v, 'percentage') for v in ss],
            _winner3(names, ss), 'Significance restricted to subspace insights')

    # ── 8. Score Uplift ───────────────────────────────────────────────────
    ups = [r.get('score_uplift_from_subspace') or {} for r in results_list]
    up_vals = [u.get('score_uplift_abs') for u in ups]
    up_ratio = [u.get('score_uplift_ratio') for u in ups]
    up_str = [
        f"Δ={v:.3f}, x={x:.3f}" if v is not None and x is not None else 'N/A'
        for v, x in zip(up_vals, up_ratio)
    ]
    row('Subspace Deep-dive', '8. Score Uplift from Subspace',
        up_str, _winner3(names, [v or 0 for v in up_vals]),
        'Δ = mean(score|subspace) - mean(score|no-subspace)')

    # ── 10. BM Quality ────────────────────────────────────────────────────
    bms = [r.get('bm_quality') for r in results_list]
    if any(bms):
        cat_str = [
            f"{bm.get('total_categorical', 0)}/{bm.get('total_evaluated', 0)}" if bm else 'N/A'
            for bm in bms
        ]
        row('Intent Layer Quality', '10. Total (B,M) pairs evaluated',
            cat_str, 'N/A',
            'Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness)')

        for key, label, desc, higher_better in [
            ('nmi_mean',      '10a. BM — NMI mean',       'Mean NMI over categorical-B pairs',               True),
            ('int_mean',      '10b. BM — Interestingness', 'Mean Coverage×EffectSize over categorical-B pairs', True),
            ('actionability', '10c. BM — Actionability',  '% pairs with categorical breakdown',              True),
            ('bm_diversity',  '10d. BM — Diversity',      'Unique (B,M) pairs / total insights',             True),
        ]:
            vs = [bm.get(key, 0) or 0 if bm else 0 for bm in bms]
            row('Intent Layer Quality', label,
                [format_metric_value(v, 'default') for v in vs],
                _winner3(names, vs, higher_better),
                desc)

    # ── 11. Question Quality ──────────────────────────────────────────────
    qqs = [r.get('question_quality') or {} for r in results_list]

    qd = [(qq.get('question_diversity') or {}).get('question_diversity', 0) or 0 for qq in qqs]
    row('Intent Layer Quality', '11a. Question Semantic Diversity',
        [format_metric_value(v, 'default') for v in qd],
        _winner3(names, qd),
        '1 - mean cosine sim of question embeddings (within-system)')

    sp = [qq.get('question_specificity') or {} for qq in qqs]
    sp_m = [s.get('question_specificity_mean', 0) or 0 for s in sp]
    sp_s = [s.get('question_specificity_std', 0) or 0 for s in sp]
    row('Intent Layer Quality', '11b. Question Specificity',
        [f"{m:.2f} ± {s:.2f}" for m, s in zip(sp_m, sp_s)],
        _winner3(names, sp_m),
        'Avg word count per question (mean ± std) — higher = more specific')

    al = [(qq.get('question_insight_alignment') or {}).get('question_insight_alignment', 0) or 0 for qq in qqs]
    al_gap = abs(al[0] - al[1])  # QUIS vs Baseline gap
    al_winner = 'Tie' if al_gap < 0.005 else _winner3(names, al)
    row('Intent Layer Quality', '11c. Question–Insight Alignment',
        [format_metric_value(v, 'default') for v in al],
        al_winner,
        'Mean cosine(Embed(question), Embed(insight)) — control metric (Tie = both execute faithfully)')

    qn = [(qq.get('question_novelty') or {}).get('question_novelty', 0) or 0 for qq in qqs]
    row('Intent Layer Quality', '11d. Question Novelty (cross-system)',
        [format_metric_value(v, 'percentage') for v in qn],
        _winner3(names, qn),
        '% of questions with cross-system max cosine sim < 0.85')

    rc = [(qq.get('reason_insight_coherence') or {}).get('reason_insight_coherence', 0) or 0 for qq in qqs]
    row('Intent Layer Quality', '11e. Reason–Insight Coherence',
        [format_metric_value(v, 'default') for v in rc],
        _winner3(names, rc),
        'Mean cosine(Embed(reason), Embed(insight)) — reason grounding')

    # ── 12. Structural Validity Rate ──────────────────────────────────────
    svr_results = [
        compute_structural_validity(ins, df_cleaned, profile_path)
        for ins in [insights_a, insights_b, insights_c]
    ]
    svr_vals = [s['structural_validity_rate'] for s in svr_results]
    svr_str = [f"{s['structural_validity_rate']*100:.1f}% ({s['valid_count']}/{s['total_count']})" for s in svr_results]
    row('Intent Layer Quality', '12. Structural Validity Rate',
        svr_str, _winner3(names, svr_vals),
        '% insights with breakdown type valid for their pattern — measures QuGen structural understanding')

    for pattern in ['OUTSTANDING_VALUE', 'TREND', 'ATTRIBUTION', 'DISTRIBUTION_DIFFERENCE']:
        psvr = [s['by_pattern'].get(pattern, {}) for s in svr_results]
        psvr_str = [
            f"{p['valid_count']}/{p['total_count']}" if p.get('total_count', 0) > 0 else 'N/A'
            for p in psvr
        ]
        psvr_vals = [p.get('valid_rate') for p in psvr]
        row('Intent Layer Quality', f'12a. SVR — {pattern}',
            psvr_str,
            _winner3(names, [v if v is not None else 0 for v in psvr_vals]),
            f'Structural validity for {pattern} pattern')

    df = pd.DataFrame(metrics)
    # Column order: Group, Metric, name_a, name_b, name_c, Winner, Description
    cols = ['Group', 'Metric', name_a, name_b, name_c, 'Winner', 'Description']
    return df[cols]


def main():
    parser = argparse.ArgumentParser(description='3-way comparison: QUIS vs Baseline vs ONLYSTATS')
    parser.add_argument('--data', required=True)
    parser.add_argument('--system_a', required=True)
    parser.add_argument('--path_a', required=True, help='Insights JSON for system A')
    parser.add_argument('--results_a', required=True, help='Results JSON for system A')
    parser.add_argument('--system_b', required=True)
    parser.add_argument('--path_b', required=True)
    parser.add_argument('--results_b', required=True)
    parser.add_argument('--system_c', required=True)
    parser.add_argument('--path_c', required=True)
    parser.add_argument('--results_c', required=True)
    parser.add_argument('--profile', default=None)
    parser.add_argument('--output', default='evaluation_results', help='Output directory')
    args = parser.parse_args()

    _, df_cleaned = load_and_clean_data(args.data)

    def load_json(p):
        with open(p) as f:
            return json.load(f)

    results_a = load_json(args.results_a)
    results_b = load_json(args.results_b)
    results_c = load_json(args.results_c)
    insights_a = load_json(args.path_a)
    insights_b = load_json(args.path_b)
    insights_c = load_json(args.path_c)

    df = create_comparison_table_3way(
        results_a, results_b, results_c,
        args.system_a, args.system_b, args.system_c,
        insights_a, insights_b, insights_c,
        df_cleaned, args.profile,
    )

    os.makedirs(args.output, exist_ok=True)
    out_path = os.path.join(args.output, 'comparison_table_3way.csv')
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df.to_string(index=False))


if __name__ == '__main__':
    main()
