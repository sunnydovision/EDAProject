"""
Model comparison module.

Compares two systems across all metrics.
"""

import pandas as pd
from typing import Dict, Any


def create_comparison_table(
    results_a: Dict[str, Any],
    results_b: Dict[str, Any],
    name_a: str = "System A",
    name_b: str = "System B"
) -> pd.DataFrame:
    """
    Create comparison table for 4 CORE METRICS.
    
    Args:
        results_a: Evaluation results for system A
        results_b: Evaluation results for system B
        name_a: Name of system A
        name_b: Name of system B
        
    Returns:
        DataFrame with side-by-side comparison
    """
    metrics = []
    
    # 1. Faithfulness
    # Add total insights summary at beginning of Group 1
    total_a = results_a['faithfulness']['total_count']
    total_b = results_b['faithfulness']['total_count']
    metrics.append({
        'Group': 'Core & Efficiency',
        'Metric': '0. Total insights',
        name_a: str(total_a),
        name_b: str(total_b),
        'Winner': 'N/A',
        'Description': 'Total insight cards generated'
    })

    metrics.append({
        'Group': 'Core & Efficiency',
        'Metric': '1. Faithfulness',
        name_a: format_metric_value(results_a['faithfulness']['faithfulness'], 'percentage'),
        name_b: format_metric_value(results_b['faithfulness']['faithfulness'], 'percentage'),
        'Winner': name_a if results_a['faithfulness']['faithfulness'] > results_b['faithfulness']['faithfulness'] else name_b if results_b['faithfulness']['faithfulness'] > results_a['faithfulness']['faithfulness'] else 'Tie',
        'Description': 'Correctness - đúng dữ liệu'
    })
    
    # 2. Statistical Significance (4 sub-metrics)
    sig_a = results_a['insight_significance']
    sig_b = results_b['insight_significance']

    # Overall significance
    metrics.append({
        'Group': 'Core & Efficiency',
        'Metric': '2. Statistical Significance (Overall)',
        name_a: format_metric_value(sig_a.get('pattern_avg_significance', sig_a['significant_rate']), 'percentage'),
        name_b: format_metric_value(sig_b.get('pattern_avg_significance', sig_b['significant_rate']), 'percentage'),
        'Winner': name_a if sig_a.get('pattern_avg_significance', sig_a['significant_rate']) > sig_b.get('pattern_avg_significance', sig_b['significant_rate']) else name_b if sig_b.get('pattern_avg_significance', sig_b['significant_rate']) > sig_a.get('pattern_avg_significance', sig_a['significant_rate']) else 'Tie',
        'Description': 'Validity - pattern-averaged (fair comparison)'
    })

    # Per pattern significance
    bp_a = sig_a.get('by_pattern', {})
    bp_b = sig_b.get('by_pattern', {})

    for pattern in ['TREND', 'OUTSTANDING_VALUE', 'ATTRIBUTION', 'DISTRIBUTION_DIFFERENCE']:
        p_a = bp_a.get(pattern, {}).get('significant_rate', 0) or 0
        p_b = bp_b.get(pattern, {}).get('significant_rate', 0) or 0
        count_a = bp_a.get(pattern, {}).get('total_count', 0)
        count_b = bp_b.get(pattern, {}).get('total_count', 0)
        
        # Don't show insight details to avoid N/A clutter
        metrics.append({
            'Group': 'Core & Efficiency',
            'Metric': f'2a. Significance — {pattern}',
            name_a: f"{p_a*100:.1f}% ({count_a})" if count_a > 0 else 'N/A',
            name_b: f"{p_b*100:.1f}% ({count_b})" if count_b > 0 else 'N/A',
            'Winner': name_a if p_a > p_b else name_b if p_b > p_a else 'N/A',
            'Description': f'Validity - {pattern} pattern'
        })
    
    # 3. Insight Novelty
    metrics.append({
        'Group': 'Core & Efficiency',
        'Metric': '3. Insight Novelty',
        name_a: format_metric_value(results_a['insight_novelty']['novelty'], 'percentage'),
        name_b: format_metric_value(results_b['insight_novelty']['novelty'], 'percentage'),
        'Winner': name_a if results_a['insight_novelty']['novelty'] > results_b['insight_novelty']['novelty'] else name_b if results_b['insight_novelty']['novelty'] > results_a['insight_novelty']['novelty'] else 'Tie',
        'Description': 'Usefulness - khác baseline'
    })
    
    # 4. Insight Diversity (4 sub-metrics)
    div_a = results_a['question_diversity']
    div_b = results_b['question_diversity']

    sem_a = div_a.get('semantic_diversity', 0) or 0
    sem_b = div_b.get('semantic_diversity', 0) or 0
    metrics.append({
        'Group': 'Core & Efficiency',
        'Metric': '4a. Diversity — Semantic',
        name_a: format_metric_value(sem_a, 'default'),
        name_b: format_metric_value(sem_b, 'default'),
        'Winner': name_a if sem_a > sem_b else name_b if sem_b > sem_a else 'Tie',
        'Description': 'Semantic diversity (breakdown|measure|pattern|subspace)'
    })

    sub_ent_a = (div_a.get('subspace_diversity') or {}).get('subspace_diversity_entropy')
    sub_ent_b = (div_b.get('subspace_diversity') or {}).get('subspace_diversity_entropy')
    metrics.append({
        'Group': 'Core & Efficiency',
        'Metric': '4b. Diversity — Subspace Entropy',
        name_a: format_metric_value(sub_ent_a, 'default') if sub_ent_a is not None else 'N/A',
        name_b: format_metric_value(sub_ent_b, 'default') if sub_ent_b is not None else 'N/A',
        'Winner': (name_a if (sub_ent_a or 0) > (sub_ent_b or 0) else name_b if (sub_ent_b or 0) > (sub_ent_a or 0) else 'Tie') if sub_ent_a is not None or sub_ent_b is not None else 'N/A',
        'Description': 'Entropy of subspace filter columns used'
    })

    val_a = (div_a.get('value_diversity') or {}).get('value_diversity')
    val_b = (div_b.get('value_diversity') or {}).get('value_diversity')
    metrics.append({
        'Group': 'Core & Efficiency',
        'Metric': '4c. Diversity — Value',
        name_a: format_metric_value(val_a, 'default') if val_a is not None else 'N/A',
        name_b: format_metric_value(val_b, 'default') if val_b is not None else 'N/A',
        'Winner': (name_a if (val_a or 0) > (val_b or 0) else name_b if (val_b or 0) > (val_a or 0) else 'Tie') if val_a is not None or val_b is not None else 'N/A',
        'Description': 'Unique (column, value) pairs in subspace / total'
    })

    dedup_a = div_a.get('dedup_rate', 0) or 0
    dedup_b = div_b.get('dedup_rate', 0) or 0
    metrics.append({
        'Group': 'Core & Efficiency',
        'Metric': '4d. Diversity — Dedup Rate',
        name_a: format_metric_value(dedup_a, 'default'),
        name_b: format_metric_value(dedup_b, 'default'),
        'Winner': name_a if dedup_a < dedup_b else name_b if dedup_b < dedup_a else 'Tie',
        'Description': 'Duplicate rate — lower is better'
    })
    
    # 5. Time to Insight (Efficiency)
    if results_a.get('time_to_insight') and results_b.get('time_to_insight'):
        time_a = results_a['time_to_insight'].get('time_per_insight_seconds')
        time_b = results_b['time_to_insight'].get('time_per_insight_seconds')
        
        if time_a is not None and time_b is not None:
            metrics.append({
                'Group': 'Core & Efficiency',
                'Metric': '5. Time to Insight',
                name_a: f"{time_a:.2f}s",
                name_b: f"{time_b:.2f}s",
                'Winner': name_a if time_a < time_b else name_b if time_b < time_a else 'Tie',
                'Description': 'Speed - thời gian mỗi insight'
            })
        else:
            value_a = f"{time_a:.2f}s" if time_a is not None else "N/A"
            value_b = f"{time_b:.2f}s" if time_b is not None else "N/A"
            metrics.append({
                'Group': 'Core & Efficiency',
                'Metric': '5. Time to Insight',
                name_a: value_a,
                name_b: value_b,
                'Winner': 'N/A',
                'Description': 'Speed - thời gian mỗi insight'
            })
    
    # 6. Token Usage (Efficiency)
    if results_a.get('token_usage') and results_b.get('token_usage'):
        tokens_a = results_a['token_usage'].get('tokens_per_insight')
        tokens_b = results_b['token_usage'].get('tokens_per_insight')
        
        if tokens_a is not None and tokens_b is not None:
            metrics.append({
                'Group': 'Core & Efficiency',
                'Metric': '6. Token Usage',
                name_a: f"{tokens_a:.0f}",
                name_b: f"{tokens_b:.0f}",
                'Winner': name_a if tokens_a < tokens_b else name_b if tokens_b < tokens_a else 'Tie',
                'Description': 'Cost - tokens mỗi insight'
            })
        else:
            value_a = f"{tokens_a:.0f}" if tokens_a is not None else "N/A"
            value_b = f"{tokens_b:.0f}" if tokens_b is not None else "N/A"
            metrics.append({
                'Group': 'Core & Efficiency',
                'Metric': '6. Token Usage',
                name_a: value_a,
                name_b: value_b,
                'Winner': 'N/A',
                'Description': 'Cost - tokens mỗi insight'
            })
    
    # 7. Subspace Metrics
    sa = results_a.get('subspace_metrics', {})
    sb = results_b.get('subspace_metrics', {})
    sub_count_a = sa.get('total_with_subspace', 0)
    sub_count_b = sb.get('total_with_subspace', 0)
    total_a = results_a.get('num_insights', 1) or 1
    total_b = results_b.get('num_insights', 1) or 1
    metrics.append({
        'Group': 'Subspace Deep-dive',
        'Metric': '7. Subspace Rate',
        name_a: f"{sub_count_a}/{total_a} ({sub_count_a/total_a*100:.1f}%)",
        name_b: f"{sub_count_b}/{total_b} ({sub_count_b/total_b*100:.1f}%)",
        'Winner': name_a if sub_count_a / total_a > sub_count_b / total_b else name_b if sub_count_b / total_b > sub_count_a / total_a else 'Tie',
        'Description': 'Insights with subspace filter / total'
    })
    if sa.get('faithfulness') and sb.get('faithfulness'):
        sf_a = sa['faithfulness']['faithfulness']
        sf_b = sb['faithfulness']['faithfulness']
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '7a. Subspace Faithfulness',
            name_a: format_metric_value(sf_a, 'percentage'),
            name_b: format_metric_value(sf_b, 'percentage'),
            'Winner': name_a if sf_a > sf_b else name_b if sf_b > sf_a else 'Tie',
            'Description': 'Faithfulness restricted to subspace insights'
        })
    if sa.get('significance') and sb.get('significance'):
        ss_a = sa['significance']['significant_rate']
        ss_b = sb['significance']['significant_rate']
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '7b. Subspace Significance',
            name_a: format_metric_value(ss_a, 'percentage'),
            name_b: format_metric_value(ss_b, 'percentage'),
            'Winner': name_a if ss_a > ss_b else name_b if ss_b > ss_a else 'Tie',
            'Description': 'Significance restricted to subspace insights'
        })
    if sa.get('novelty') and sb.get('novelty'):
        sn_a = sa['novelty']['novelty']
        sn_b = sb['novelty']['novelty']
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '7c. Subspace Novelty',
            name_a: format_metric_value(sn_a, 'percentage'),
            name_b: format_metric_value(sn_b, 'percentage'),
            'Winner': name_a if sn_a > sn_b else name_b if sn_b > sn_a else 'Tie',
            'Description': 'Novelty restricted to subspace insights'
        })
    if sa.get('diversity') and sb.get('diversity'):
        sd_a = sa['diversity'].get('semantic_diversity', 0) or 0
        sd_b = sb['diversity'].get('semantic_diversity', 0) or 0
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '7d.1. Diversity — Semantic (Subspace)',
            name_a: format_metric_value(sd_a, 'default'),
            name_b: format_metric_value(sd_b, 'default'),
            'Winner': name_a if sd_a > sd_b else name_b if sd_b > sd_a else 'Tie',
            'Description': 'Semantic diversity restricted to subspace insights'
        })
        sub_ent_a = (sa['diversity'].get('subspace_diversity') or {}).get('subspace_diversity_entropy')
        sub_ent_b = (sb['diversity'].get('subspace_diversity') or {}).get('subspace_diversity_entropy')
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '7d.2. Diversity — Subspace Entropy (Subspace)',
            name_a: format_metric_value(sub_ent_a, 'default') if sub_ent_a is not None else 'N/A',
            name_b: format_metric_value(sub_ent_b, 'default') if sub_ent_b is not None else 'N/A',
            'Winner': (name_a if (sub_ent_a or 0) > (sub_ent_b or 0) else name_b if (sub_ent_b or 0) > (sub_ent_a or 0) else 'Tie') if sub_ent_a is not None or sub_ent_b is not None else 'N/A',
            'Description': 'Entropy of subspace filter columns used (subspace insights)'
        })
        val_a = (sa['diversity'].get('value_diversity') or {}).get('value_diversity')
        val_b = (sb['diversity'].get('value_diversity') or {}).get('value_diversity')
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '7d.3. Diversity — Value (Subspace)',
            name_a: format_metric_value(val_a, 'default') if val_a is not None else 'N/A',
            name_b: format_metric_value(val_b, 'default') if val_b is not None else 'N/A',
            'Winner': (name_a if (val_a or 0) > (val_b or 0) else name_b if (val_b or 0) > (val_a or 0) else 'Tie') if val_a is not None or val_b is not None else 'N/A',
            'Description': 'Unique (column, value) pairs in subspace / total (subspace insights)'
        })
        dedup_a = sa['diversity'].get('dedup_rate', 0) or 0
        dedup_b = sb['diversity'].get('dedup_rate', 0) or 0
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '7d.4. Diversity — Dedup Rate (Subspace)',
            name_a: format_metric_value(dedup_a, 'default'),
            name_b: format_metric_value(dedup_b, 'default'),
            'Winner': name_a if dedup_a < dedup_b else name_b if dedup_b < dedup_a else 'Tie',
            'Description': 'Duplicate rate restricted to subspace insights - lower is better'
        })

    # 8. Score uplift from subspace
    uplift_a = (results_a.get('score_uplift_from_subspace') or {}).get('score_uplift_abs')
    uplift_b = (results_b.get('score_uplift_from_subspace') or {}).get('score_uplift_abs')
    ratio_a = (results_a.get('score_uplift_from_subspace') or {}).get('score_uplift_ratio')
    ratio_b = (results_b.get('score_uplift_from_subspace') or {}).get('score_uplift_ratio')
    if uplift_a is not None or uplift_b is not None:
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '8. Score Uplift from Subspace',
            name_a: (
                f"Δ={uplift_a:.3f}, x={ratio_a:.3f}"
                if uplift_a is not None and ratio_a is not None
                else (f"Δ={uplift_a:.3f}" if uplift_a is not None else "N/A")
            ),
            name_b: (
                f"Δ={uplift_b:.3f}, x={ratio_b:.3f}"
                if uplift_b is not None and ratio_b is not None
                else (f"Δ={uplift_b:.3f}" if uplift_b is not None else "N/A")
            ),
            'Winner': name_a if (uplift_a or 0) > (uplift_b or 0) else name_b,
            'Description': 'Δ = mean(score|subspace) - mean(score|no-subspace)'
        })

    # 9. Simpson's Paradox Rate: proportion of subspace insights with statistically
    #    significant pattern reversals — true Simpson's Paradox cases
    spr_a = (results_a.get('simpson_paradox') or {}).get('simpson_paradox_rate')
    spr_b = (results_b.get('simpson_paradox') or {}).get('simpson_paradox_rate')
    sig_ct_a = (results_a.get('simpson_paradox') or {}).get('significant_paradox_count')
    sig_ct_b = (results_b.get('simpson_paradox') or {}).get('significant_paradox_count')
    total_ct_a = (results_a.get('simpson_paradox') or {}).get('paradox_count')
    total_ct_b = (results_b.get('simpson_paradox') or {}).get('paradox_count')
    if spr_a is not None or spr_b is not None:
        winner = name_a if (spr_a or 0) > (spr_b or 0) else name_b if (spr_b or 0) > (spr_a or 0) else 'Tie'
        def _fmt_spr(rate, sig_ct, total_ct):
            if rate is None:
                return 'N/A'
            if sig_ct is not None and total_ct is not None:
                return f"{rate:.1%} ({sig_ct}/{total_ct} sig)"
            return f"{rate:.1%}"
        metrics.append({
            'Group': 'Subspace Deep-dive',
            'Metric': '9. Simpson\'s Paradox Rate (SPR)',
            name_a: _fmt_spr(spr_a, sig_ct_a, total_ct_a),
            name_b: _fmt_spr(spr_b, sig_ct_b, total_ct_b),
            'Winner': winner,
            'Description': 'Rate of statistically significant pattern reversals (p<0.05) — true Simpson\'s Paradox cases'
        })

    # 10. BM Quality
    bm_a = results_a.get('bm_quality')
    bm_b = results_b.get('bm_quality')
    if bm_a and bm_b:
        # Add summary count at beginning of Group 3
        cat_pairs_a = f"{bm_a.get('total_categorical', 0)}/{bm_a.get('total_evaluated', 0)}"
        cat_pairs_b = f"{bm_b.get('total_categorical', 0)}/{bm_b.get('total_evaluated', 0)}"
        metrics.append({
            'Group': 'Intent Layer Quality',
            'Metric': '10. Total (B,M) pairs evaluated',
            name_a: cat_pairs_a,
            name_b: cat_pairs_b,
            'Winner': 'N/A',
            'Description': 'Total unique breakdown-measure pairs (categorical breakdowns only for NMI/Interestingness)'
        })

        for key, label, desc, higher_better in [
            ('nmi_mean',      '10a. BM — NMI mean',       'Mean NMI over categorical-B pairs',                    True),
            ('int_mean',      '10b. BM — Interestingness', 'Mean Coverage×EffectSize over categorical-B pairs',    True),
            ('actionability', '10c. BM — Actionability',  '% pairs with categorical breakdown',                   True),
            ('bm_diversity',  '10d. BM — Diversity',      'Unique (B,M) pairs / total insights',                  True),
        ]:
            va = bm_a.get(key, 0) or 0
            vb = bm_b.get(key, 0) or 0
            winner = (name_a if va > vb else name_b if vb > va else 'Tie') if higher_better \
                     else (name_a if va < vb else name_b if vb < va else 'Tie')
            metrics.append({
                'Group': 'Intent Layer Quality',
                'Metric': label,
                name_a: format_metric_value(va, 'default'),
                name_b: format_metric_value(vb, 'default'),
                'Winner': winner,
                'Description': desc,
            })

    # ── 11. Question Generation (QuGen) Quality ───────────────────────────
    qa = results_a.get('question_quality') or {}
    qb = results_b.get('question_quality') or {}

    if qa or qb:
        # 11a. Question Semantic Diversity (within-system)
        qd_a = (qa.get('question_diversity') or {}).get('question_diversity', 0) or 0
        qd_b = (qb.get('question_diversity') or {}).get('question_diversity', 0) or 0
        metrics.append({
            'Group': 'Intent Layer Quality',
            'Metric': '11a. Question Semantic Diversity',
            name_a: format_metric_value(qd_a, 'default'),
            name_b: format_metric_value(qd_b, 'default'),
            'Winner': name_a if qd_a > qd_b else name_b if qd_b > qd_a else 'Tie',
            'Description': '1 - mean cosine sim of question embeddings (within-system)'
        })

        # 11b. Question Specificity (avg word count) — std reported alongside
        sp_a = qa.get('question_specificity') or {}
        sp_b = qb.get('question_specificity') or {}
        m_a = sp_a.get('question_specificity_mean', 0) or 0
        m_b = sp_b.get('question_specificity_mean', 0) or 0
        s_a = sp_a.get('question_specificity_std', 0) or 0
        s_b = sp_b.get('question_specificity_std', 0) or 0
        metrics.append({
            'Group': 'Intent Layer Quality',
            'Metric': '11b. Question Specificity',
            name_a: f"{m_a:.2f} ± {s_a:.2f}",
            name_b: f"{m_b:.2f} ± {s_b:.2f}",
            'Winner': name_a if m_a > m_b else name_b if m_b > m_a else 'Tie',
            'Description': 'Avg word count per question (mean ± std) — higher = more specific'
        })

        # 11c. Question–Insight Alignment
        al_a = (qa.get('question_insight_alignment') or {}).get('question_insight_alignment', 0) or 0
        al_b = (qb.get('question_insight_alignment') or {}).get('question_insight_alignment', 0) or 0
        metrics.append({
            'Group': 'Intent Layer Quality',
            'Metric': '11c. Question–Insight Alignment',
            name_a: format_metric_value(al_a, 'default'),
            name_b: format_metric_value(al_b, 'default'),
            'Winner': name_a if al_a > al_b else name_b if al_b > al_a else 'Tie',
            'Description': 'Mean cosine(Embed(question), Embed(insight)) — semantic faithfulness'
        })

        # 11d. Question Novelty (cross-system)
        qn_a = (qa.get('question_novelty') or {}).get('question_novelty', None) or None
        qn_b = (qb.get('question_novelty') or {}).get('question_novelty', None) or None
        # Handle N/A for ONLYSTATS
        qn_a_display = 'N/A' if qn_a is None and name_a == 'ONLYSTATS' else qn_a
        qn_b_display = 'N/A' if qn_b is None and name_b == 'ONLYSTATS' else qn_b
        metrics.append({
            'Group': 'Intent Layer Quality',
            'Metric': '11d. Question Novelty (cross-system)',
            name_a: format_metric_value(qn_a_display, 'percentage') if qn_a_display != 'N/A' else 'N/A',
            name_b: format_metric_value(qn_b_display, 'percentage') if qn_b_display != 'N/A' else 'N/A',
            'Winner': name_a if qn_a is not None and qn_b is not None and qn_a > qn_b else name_b if qn_b is not None and qn_a is not None and qn_b > qn_a else 'Tie',
            'Description': '% of questions with cross-system max cosine sim < 0.85'
        })

        # 11e. Reason–Insight Coherence
        rc_a = (qa.get('reason_insight_coherence') or {}).get('reason_insight_coherence', None) or None
        rc_b = (qb.get('reason_insight_coherence') or {}).get('reason_insight_coherence', None) or None
        # Handle N/A for ONLYSTATS
        rc_a_display = 'N/A' if rc_a is None and name_a == 'ONLYSTATS' else rc_a
        rc_b_display = 'N/A' if rc_b is None and name_b == 'ONLYSTATS' else rc_b
        metrics.append({
            'Group': 'Intent Layer Quality',
            'Metric': '11e. Reason–Insight Coherence',
            name_a: format_metric_value(rc_a_display, 'default') if rc_a_display != 'N/A' else 'N/A',
            name_b: format_metric_value(rc_b_display, 'default') if rc_b_display != 'N/A' else 'N/A',
            'Winner': name_a if rc_a is not None and rc_b is not None and rc_a > rc_b else name_b if rc_b is not None and rc_a is not None and rc_b > rc_a else 'Tie',
            'Description': 'Mean cosine(Embed(reason), Embed(insight)) — reason grounding'
        })

    df = pd.DataFrame(metrics)
    return df


def format_metric_value(value: Any, metric_type: str = 'default') -> str:
    """Format metric value for display."""
    if isinstance(value, float):
        if metric_type == 'percentage':
            return f"{value*100:.1f}%"
        else:
            return f"{value:.3f}"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, dict):
        import json
        return json.dumps(value, indent=2)
    else:
        return str(value)


def generate_report(
    results_a: Dict[str, Any],
    results_b: Dict[str, Any],
    output_path: str = 'evaluation/results/comparison_report.md',
    name_a: str = "QUIS",
    name_b: str = "Baseline"
):
    """
    Generate markdown report with comparison results.
    
    Args:
        results_a: Evaluation results for system A
        results_b: Evaluation results for system B
        output_path: Path to save report
        name_a: Name of system A
        name_b: Name of system B
    """
    import os
    dir_path = os.path.dirname(output_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    comparison_df = create_comparison_table(results_a, results_b, name_a, name_b)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {name_a} vs {name_b}: Evaluation Report\n\n")
        f.write("**Generated**: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        f.write("---\n\n")

        # ── Executive Summary ─────────────────────────────────────────────
        f.write("## Executive Summary\n\n")

        a_wins = len(comparison_df[comparison_df['Winner'] == name_a])
        b_wins = len(comparison_df[comparison_df['Winner'] == name_b])
        winner_overall = name_a if a_wins > b_wins else name_b if b_wins > a_wins else "Tie"

        f.write(f"| | {name_a} | {name_b} |\n")
        f.write(f"|---|---|---|\n")
        f.write(f"| **Metrics Won** | {a_wins} | {b_wins} |\n")
        f.write(f"| **Overall Winner** | {'✓' if winner_overall == name_a else ''} | {'✓' if winner_overall == name_b else ''} |\n\n")

        f.write("---\n\n")

        # ── GROUP 1: Core & Efficiency ────────────────────────────────────
        f.write("## Group 1 — Core Metrics & Efficiency\n\n")

        g1_df = comparison_df[comparison_df['Group'] == 'Core & Efficiency'].drop(columns=['Group'])
        f.write(g1_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("---\n\n")

        # ── GROUP 2: Subspace Deep-dive ───────────────────────────────────
        f.write("## Group 2 — Subspace Deep-dive\n\n")

        g2_df = comparison_df[comparison_df['Group'] == 'Subspace Deep-dive'].drop(columns=['Group'])
        if not g2_df.empty:
            f.write(g2_df.to_markdown(index=False))
            f.write("\n\n")
        else:
            f.write("_No subspace metrics available._\n\n")

        f.write("---\n\n")

        # ── GROUP 3: Intent Layer Quality ─────────────────────────
        # Merged group: BM Deep-dive (target structure 10a-e) +
        # Question Generation text/reason (11a-e).  Both measure the same
        # QuGen module — split into two sub-sections for readability.
        f.write("## Group 3 — Intent Layer Quality\n\n")
        f.write(
            "> Đánh giá mô-đun *Question Generation (QuGen)* ở hai lớp: "
            "**(3.1) Target structure** — chất lượng cặp `(breakdown, measure)` mà "
            "QuGen chọn; **(3.2) Question text & reason** — chất lượng câu hỏi và "
            "lý do ở dạng ngôn ngữ tự nhiên.\n\n"
        )

        g3_df = comparison_df[
            comparison_df['Group'] == 'Intent Layer Quality'
        ].drop(columns=['Group'])

        # Split by metric prefix: "10*" => target structure, "11*" => text/reason.
        bm_mask = g3_df['Metric'].str.startswith(('10.', '10a', '10b', '10c', '10d', '10e'))
        qg_mask = g3_df['Metric'].str.startswith(('11a', '11b', '11c', '11d', '11e'))

        f.write("### 3.1 Target structure — `(breakdown, measure)`\n\n")
        bm_df = g3_df[bm_mask]
        if not bm_df.empty:
            f.write(bm_df.to_markdown(index=False))
            f.write("\n\n")
        else:
            f.write("_BM Quality not available (run with --profile to enable)._\n\n")

        f.write("### 3.2 Question text & reason\n\n")
        qg_df = g3_df[qg_mask]
        if not qg_df.empty:
            f.write(qg_df.to_markdown(index=False))
            f.write("\n\n")
        else:
            f.write("_QuGen text metrics not available._\n\n")

        f.write("---\n\n")

        # ── Conclusion ────────────────────────────────────────────────────
        f.write("## Conclusion\n\n")
        f.write(f"**Overall Winner**: {winner_overall} ({a_wins} vs {b_wins} metrics won)\n\n")

    print(f"\nReport saved: {output_path}")
