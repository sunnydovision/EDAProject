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
from configs.eval_config import EvalConfig
from utils.log_config import save_run_log, load_eval_config


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

    # ── 3. Insight Novelty (cross-system) ─────────────────────────────────
    # Extract from results since they were computed in pairwise comparisons
    nov_vals = [r.get('insight_novelty', {}).get('novelty', None) for r in results_list]
    nov_str = [format_metric_value(v, 'percentage') if v is not None else 'N/A' for v in nov_vals]
    winner_nov = _winner3(names, nov_vals)
    row('Core & Efficiency', '3. Insight Novelty',
        nov_str, winner_nov, 'Usefulness - khác baseline (from pairwise comparison results)')

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

    # ── 9. Simpson's Paradox Rate ─────────────────────────────────────────
    sprs = [r.get('simpson_paradox') for r in results_list]
    spr_vals = [sp.get('simpson_paradox_rate') if sp else None for sp in sprs]
    sig_counts = [sp.get('significant_paradox_count') if sp else None for sp in sprs]
    total_counts = [sp.get('paradox_count') if sp else None for sp in sprs]
    spr_str = [
        f"{v:.1%} ({sc}/{tc} sig)" if v is not None and sc is not None and tc is not None else 'N/A'
        for v, sc, tc in zip(spr_vals, sig_counts, total_counts)
    ]
    row('Subspace Deep-dive', '9. Simpson\'s Paradox Rate (SPR)',
        spr_str, _winner3(names, [v if isinstance(v, (int, float)) else None for v in spr_vals]),
        'Rate of statistically significant pattern reversals (p<0.05) — true Simpson\'s Paradox cases')

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

    # 11a — None for ONLYSTATS (single fixed template, not real questions)
    qd_raw = [(qq.get('question_diversity') or {}).get('question_diversity') for qq in qqs]
    qd_str = ['N/A' if (n == 'ONLYSTATS' or v is None) else format_metric_value(v, 'default')
              for n, v in zip(names, qd_raw)]
    row('Intent Layer Quality', '11a. Question Semantic Diversity',
        qd_str,
        _winner3(names, [v if v is not None and n != 'ONLYSTATS' else None for n, v in zip(names, qd_raw)]),
        '1 - mean cosine sim of question embeddings (within-system); N/A for ONLYSTATS (template)')

    # 11b — None for ONLYSTATS
    sp = [qq.get('question_specificity') or {} for qq in qqs]
    sp_m_raw = [s.get('question_specificity_mean') for s in sp]
    sp_s_raw = [s.get('question_specificity_std') for s in sp]
    sp_str = ['N/A' if (n == 'ONLYSTATS' or m is None) else f"{m:.2f} ± {(s or 0):.2f}"
              for n, m, s in zip(names, sp_m_raw, sp_s_raw)]
    row('Intent Layer Quality', '11b. Question Specificity',
        sp_str,
        _winner3(names, [v if v is not None and n != 'ONLYSTATS' else None for n, v in zip(names, sp_m_raw)]),
        'Avg word count per question (mean ± std) — higher = more specific; N/A for ONLYSTATS (template)')

    # 11c — None for ONLYSTATS
    al_raw = [(qq.get('question_insight_alignment') or {}).get('question_insight_alignment') for qq in qqs]
    al_str = ['N/A' if (n == 'ONLYSTATS' or v is None) else format_metric_value(v, 'default')
              for n, v in zip(names, al_raw)]
    al_valid = [v for n, v in zip(names, al_raw) if n != 'ONLYSTATS' and v is not None]
    al_winner = 'Tie' if (len(al_valid) == 2 and abs(al_valid[0] - al_valid[1]) < 0.005) else \
        _winner3(names, [v if v is not None and n != 'ONLYSTATS' else None for n, v in zip(names, al_raw)])
    row('Intent Layer Quality', '11c. Question–Insight Alignment',
        al_str,
        al_winner,
        'Mean cosine(Embed(question), Embed(insight)) — control metric; N/A for ONLYSTATS (template)')

    # ── 11d. Question Novelty (cross-system) ───────────────────────────────
    # Extract from results since they were computed in pairwise comparisons
    qn_vals = [(qq.get('question_novelty') or {}).get('question_novelty', None) for qq in qqs]
    qn_str = [format_metric_value(v, 'percentage') if v is not None else 'N/A' for v in qn_vals]
    winner_qn = _winner3(names, qn_vals)
    row('Intent Layer Quality', '11d. Question Novelty (cross-system)',
        qn_str, winner_qn, '% of questions with cross-system max cosine sim < 0.85 (from pairwise comparison results)')

    rc = [(qq.get('reason_insight_coherence') or {}).get('reason_insight_coherence') for qq in qqs]
    # If ONLYSTATS has None for reason_insight_coherence, treat it as N/A
    rc_display = []
    for name, val in zip(names, rc):
        if name == 'ONLYSTATS' and val is None:
            rc_display.append('N/A')
        else:
            rc_display.append(val if val is not None else 0)
    row('Intent Layer Quality', '11e. Reason–Insight Coherence',
        [format_metric_value(v, 'default') if v != 'N/A' else 'N/A' for v in rc_display],
        _winner3(names, [v if v != 'N/A' else 0 for v in rc]),
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
    parser.add_argument('--dataset', type=str, required=True, 
                        help=f'Dataset name: {", ".join(EvalConfig.list_datasets())}')
    parser.add_argument('--output', default=None, help='Output directory (default: dataset-specific)')
    args = parser.parse_args()
    
    # Get dataset configuration
    config = EvalConfig.get_dataset_config(args.dataset)
    
    # Use dataset-specific output directory if not provided
    output_dir = args.output or config.results_dir

    # Save run log
    args_dict = vars(args)
    config_dict = load_eval_config(args.dataset)
    save_run_log("compare3", args_dict, config_dict)

    # Load data
    print(f"Loading data: {config.data_path}")
    _, df_cleaned = load_and_clean_data(config.data_path)

    def load_json(p):
        with open(p) as f:
            return json.load(f)

    # Load results
    print("Loading results...")
    results_quis = load_json(f"{output_dir}/quis_results.json")
    results_baseline = load_json(f"{output_dir}/baseline_results.json")
    results_onlystats = load_json(f"{output_dir}/onlystats_results.json")

    # Load insights
    print("Loading insights...")
    insights_quis = load_json(config.quis_insights_path)
    insights_baseline = load_json(config.baseline_insights_path)
    insights_onlystats = load_json(config.onlystats_insights_path)

    df = create_comparison_table_3way(
        results_quis, results_baseline, results_onlystats,
        'QUIS', 'Baseline', 'ONLYSTATS',
        insights_quis, insights_baseline, insights_onlystats,
        df_cleaned, config.profile_path,
    )

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'comparison_table_3way.csv')
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(df.to_string(index=False))


if __name__ == '__main__':
    main()
