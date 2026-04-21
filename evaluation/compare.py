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
    metrics.append({
        'Metric': '1. Faithfulness',
        name_a: format_metric_value(results_a['faithfulness']['faithfulness'], 'percentage'),
        name_b: format_metric_value(results_b['faithfulness']['faithfulness'], 'percentage'),
        'Winner': name_a if results_a['faithfulness']['faithfulness'] > results_b['faithfulness']['faithfulness'] else name_b,
        'Category': 'Core',
        'Description': 'Correctness - đúng dữ liệu'
    })
    
    # 2. Statistical Significance
    metrics.append({
        'Metric': '2. Statistical Significance',
        name_a: format_metric_value(results_a['insight_significance']['significant_rate'], 'percentage'),
        name_b: format_metric_value(results_b['insight_significance']['significant_rate'], 'percentage'),
        'Winner': name_a if results_a['insight_significance']['significant_rate'] > results_b['insight_significance']['significant_rate'] else name_b,
        'Category': 'Core',
        'Description': 'Validity - không phải noise'
    })
    
    # 3. Insight Novelty
    metrics.append({
        'Metric': '3. Insight Novelty',
        name_a: format_metric_value(results_a['insight_novelty']['novelty'], 'percentage'),
        name_b: format_metric_value(results_b['insight_novelty']['novelty'], 'percentage'),
        'Winner': name_a if results_a['insight_novelty']['novelty'] > results_b['insight_novelty']['novelty'] else name_b,
        'Category': 'Core',
        'Description': 'Usefulness - khác baseline'
    })
    
    # 4. Insight Diversity (4 sub-metrics)
    div_a = results_a['question_diversity']
    div_b = results_b['question_diversity']

    sem_a = div_a.get('semantic_diversity', 0) or 0
    sem_b = div_b.get('semantic_diversity', 0) or 0
    metrics.append({
        'Metric': '4a. Diversity — Semantic',
        name_a: format_metric_value(sem_a, 'default'),
        name_b: format_metric_value(sem_b, 'default'),
        'Winner': name_a if sem_a > sem_b else name_b,
        'Category': 'Core',
        'Description': 'Semantic diversity (breakdown|measure|pattern|subspace)'
    })

    sub_ent_a = (div_a.get('subspace_diversity') or {}).get('subspace_diversity_entropy')
    sub_ent_b = (div_b.get('subspace_diversity') or {}).get('subspace_diversity_entropy')
    metrics.append({
        'Metric': '4b. Diversity — Subspace Entropy',
        name_a: format_metric_value(sub_ent_a, 'default') if sub_ent_a is not None else 'N/A',
        name_b: format_metric_value(sub_ent_b, 'default') if sub_ent_b is not None else 'N/A',
        'Winner': (name_a if (sub_ent_a or 0) > (sub_ent_b or 0) else name_b) if sub_ent_a is not None or sub_ent_b is not None else 'N/A',
        'Category': 'Core',
        'Description': 'Entropy of subspace filter columns used'
    })

    val_a = (div_a.get('value_diversity') or {}).get('value_diversity')
    val_b = (div_b.get('value_diversity') or {}).get('value_diversity')
    metrics.append({
        'Metric': '4c. Diversity — Value',
        name_a: format_metric_value(val_a, 'default') if val_a is not None else 'N/A',
        name_b: format_metric_value(val_b, 'default') if val_b is not None else 'N/A',
        'Winner': (name_a if (val_a or 0) > (val_b or 0) else name_b) if val_a is not None or val_b is not None else 'N/A',
        'Category': 'Core',
        'Description': 'Unique (column, value) pairs in subspace / total'
    })

    dedup_a = div_a.get('dedup_rate', 0) or 0
    dedup_b = div_b.get('dedup_rate', 0) or 0
    metrics.append({
        'Metric': '4d. Diversity — Dedup Rate',
        name_a: format_metric_value(dedup_a, 'default'),
        name_b: format_metric_value(dedup_b, 'default'),
        'Winner': name_a if dedup_a < dedup_b else name_b,
        'Category': 'Core',
        'Description': 'Duplicate rate — lower is better'
    })
    
    # 5. Time to Insight (Efficiency)
    if results_a.get('time_to_insight') and results_b.get('time_to_insight'):
        time_a = results_a['time_to_insight'].get('time_per_insight_seconds')
        time_b = results_b['time_to_insight'].get('time_per_insight_seconds')
        
        if time_a is not None and time_b is not None:
            metrics.append({
                'Metric': '5. Time to Insight',
                name_a: f"{time_a:.2f}s",
                name_b: f"{time_b:.2f}s",
                'Winner': name_a if time_a < time_b else name_b,
                'Category': 'Efficiency',
                'Description': 'Speed - thời gian mỗi insight'
            })
        else:
            # Show what data is available
            value_a = f"{time_a:.2f}s" if time_a is not None else "N/A"
            value_b = f"{time_b:.2f}s" if time_b is not None else "N/A"
            metrics.append({
                'Metric': '5. Time to Insight',
                name_a: value_a,
                name_b: value_b,
                'Winner': 'N/A',
                'Category': 'Efficiency',
                'Description': 'Speed - thời gian mỗi insight'
            })
    
    # 6. Token Usage (Efficiency)
    if results_a.get('token_usage') and results_b.get('token_usage'):
        tokens_a = results_a['token_usage'].get('tokens_per_insight')
        tokens_b = results_b['token_usage'].get('tokens_per_insight')
        
        if tokens_a is not None and tokens_b is not None:
            metrics.append({
                'Metric': '6. Token Usage',
                name_a: f"{tokens_a:.0f}",
                name_b: f"{tokens_b:.0f}",
                'Winner': name_a if tokens_a < tokens_b else name_b,
                'Category': 'Efficiency',
                'Description': 'Cost - tokens mỗi insight'
            })
        else:
            # Show what data is available
            value_a = f"{tokens_a:.0f}" if tokens_a is not None else "N/A"
            value_b = f"{tokens_b:.0f}" if tokens_b is not None else "N/A"
            metrics.append({
                'Metric': '6. Token Usage',
                name_a: value_a,
                name_b: value_b,
                'Winner': 'N/A',
                'Category': 'Efficiency',
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
        'Metric': '7. Subspace Rate',
        name_a: f"{sub_count_a}/{total_a} ({sub_count_a/total_a*100:.1f}%)",
        name_b: f"{sub_count_b}/{total_b} ({sub_count_b/total_b*100:.1f}%)",
        'Winner': name_a if sub_count_a / total_a > sub_count_b / total_b else name_b,
        'Category': 'Subspace',
        'Description': 'Insights with subspace filter / total'
    })
    if sa.get('faithfulness') and sb.get('faithfulness'):
        sf_a = sa['faithfulness']['faithfulness']
        sf_b = sb['faithfulness']['faithfulness']
        metrics.append({
            'Metric': '7a. Subspace Faithfulness',
            name_a: format_metric_value(sf_a, 'percentage'),
            name_b: format_metric_value(sf_b, 'percentage'),
            'Winner': name_a if sf_a > sf_b else name_b,
            'Category': 'Subspace',
            'Description': 'Faithfulness restricted to subspace insights'
        })
    if sa.get('significance') and sb.get('significance'):
        ss_a = sa['significance']['significant_rate']
        ss_b = sb['significance']['significant_rate']
        metrics.append({
            'Metric': '7b. Subspace Significance',
            name_a: format_metric_value(ss_a, 'percentage'),
            name_b: format_metric_value(ss_b, 'percentage'),
            'Winner': name_a if ss_a > ss_b else name_b,
            'Category': 'Subspace',
            'Description': 'Significance restricted to subspace insights'
        })
    if sa.get('novelty') and sb.get('novelty'):
        sn_a = sa['novelty']['novelty']
        sn_b = sb['novelty']['novelty']
        metrics.append({
            'Metric': '7c. Subspace Novelty',
            name_a: format_metric_value(sn_a, 'percentage'),
            name_b: format_metric_value(sn_b, 'percentage'),
            'Winner': name_a if sn_a > sn_b else name_b,
            'Category': 'Subspace',
            'Description': 'Novelty restricted to subspace insights'
        })
    if sa.get('diversity') and sb.get('diversity'):
        sd_a = sa['diversity'].get('semantic_diversity', 0) or 0
        sd_b = sb['diversity'].get('semantic_diversity', 0) or 0
        metrics.append({
            'Metric': '7d. Subspace Diversity',
            name_a: format_metric_value(sd_a, 'default'),
            name_b: format_metric_value(sd_b, 'default'),
            'Winner': name_a if sd_a > sd_b else name_b,
            'Category': 'Subspace',
            'Description': 'Semantic diversity restricted to subspace insights'
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
    name_a: str = "IFQ",
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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    comparison_df = create_comparison_table(results_a, results_b, name_a, name_b)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {name_a} vs {name_b}: Evaluation Report\n\n")
        f.write("## 4 CORE METRICS + 2 EFFICIENCY METRICS\n\n")
        f.write("**Generated**: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        
        a_wins = len(comparison_df[comparison_df['Winner'] == name_a])
        b_wins = len(comparison_df[comparison_df['Winner'] == name_b])
        
        f.write(f"- **{name_a} Wins**: {a_wins}/{len(comparison_df)} metrics\n")
        f.write(f"- **{name_b} Wins**: {b_wins}/{len(comparison_df)} metrics\n\n")
        
        # Key Findings
        f.write("### Key Findings\n\n")
        f.write(f"**{name_a} Strengths:**\n")
        f.write(f"- **Faithfulness**: {results_a['faithfulness']['faithfulness']*100:.1f}% vs {results_b['faithfulness']['faithfulness']*100:.1f}%\n")
        f.write(f"- **Statistical Significance**: {results_a['insight_significance']['significant_rate']*100:.1f}% vs {results_b['insight_significance']['significant_rate']*100:.1f}%\n")
        f.write(f"- **Insight Novelty**: {results_a['insight_novelty']['novelty']*100:.1f}% vs {results_b['insight_novelty']['novelty']*100:.1f}%\n")
        _sem_a = results_a['question_diversity'].get('semantic_diversity', 0) or 0
        _sem_b = results_b['question_diversity'].get('semantic_diversity', 0) or 0
        _sub_ent_a = (results_a['question_diversity'].get('subspace_diversity') or {}).get('subspace_diversity_entropy')
        _sub_ent_b = (results_b['question_diversity'].get('subspace_diversity') or {}).get('subspace_diversity_entropy')
        _val_a = (results_a['question_diversity'].get('value_diversity') or {}).get('value_diversity')
        _val_b = (results_b['question_diversity'].get('value_diversity') or {}).get('value_diversity')
        _dedup_a = results_a['question_diversity'].get('dedup_rate', 0) or 0
        _dedup_b = results_b['question_diversity'].get('dedup_rate', 0) or 0
        f.write(f"- **Insight Diversity (Semantic)**: {_sem_a:.3f} vs {_sem_b:.3f}\n")
        if _sub_ent_a is not None or _sub_ent_b is not None:
            _se_a_str = f"{_sub_ent_a:.3f}" if _sub_ent_a is not None else "N/A"
            _se_b_str = f"{_sub_ent_b:.3f}" if _sub_ent_b is not None else "N/A"
            f.write(f"- **Insight Diversity (Subspace Entropy)**: {_se_a_str} vs {_se_b_str}\n")
        if _val_a is not None or _val_b is not None:
            _va_str = f"{_val_a:.3f}" if _val_a is not None else "N/A"
            _vb_str = f"{_val_b:.3f}" if _val_b is not None else "N/A"
            f.write(f"- **Insight Diversity (Value)**: {_va_str} vs {_vb_str}\n")
        f.write(f"- **Insight Diversity (Dedup Rate)**: {_dedup_a:.3f} vs {_dedup_b:.3f}\n")
        
        if results_a.get('time_to_insight') and results_b.get('time_to_insight'):
            time_a = results_a['time_to_insight'].get('time_per_insight_seconds')
            time_b = results_b['time_to_insight'].get('time_per_insight_seconds')
            if time_a is not None and time_b is not None:
                f.write(f"- **Time to Insight**: {time_a:.2f}s vs {time_b:.2f}s per insight\n")
            else:
                f.write(f"- **Time to Insight**: N/A\n")
        
        if results_a.get('token_usage') and results_b.get('token_usage'):
            tokens_a = results_a['token_usage'].get('tokens_per_insight')
            tokens_b = results_b['token_usage'].get('tokens_per_insight')
            if tokens_a is not None and tokens_b is not None:
                f.write(f"- **Token Usage**: {tokens_a:.0f} vs {tokens_b:.0f} tokens per insight\n")
            else:
                f.write(f"- **Token Usage**: N/A\n")
        
        f.write("\n")
        
        f.write("---\n\n")

        # Subspace Metrics
        sa = results_a.get('subspace_metrics', {})
        sb = results_b.get('subspace_metrics', {})
        if sa or sb:
            f.write("### Subspace Insights Analysis\n\n")
            total_a = results_a.get('num_insights', 1) or 1
            total_b = results_b.get('num_insights', 1) or 1
            sub_a = sa.get('total_with_subspace', 0)
            sub_b = sb.get('total_with_subspace', 0)
            f.write(f"- **{name_a}**: {sub_a}/{total_a} insights have subspace filter ({sub_a/total_a*100:.1f}%)\n")
            f.write(f"- **{name_b}**: {sub_b}/{total_b} insights have subspace filter ({sub_b/total_b*100:.1f}%)\n")
            if sa.get('faithfulness') and sb.get('faithfulness'):
                f.write(f"- Subspace Faithfulness: {name_a}={sa['faithfulness']['faithfulness']*100:.1f}%  {name_b}={sb['faithfulness']['faithfulness']*100:.1f}%\n")
            if sa.get('significance') and sb.get('significance'):
                f.write(f"- Subspace Significance: {name_a}={sa['significance']['significant_rate']*100:.1f}%  {name_b}={sb['significance']['significant_rate']*100:.1f}%\n")
            if sa.get('novelty') and sb.get('novelty'):
                f.write(f"- Subspace Novelty: {name_a}={sa['novelty']['novelty']*100:.1f}%  {name_b}={sb['novelty']['novelty']*100:.1f}%\n")
            if sa.get('diversity') and sb.get('diversity'):
                _sd_a = sa['diversity'].get('semantic_diversity', 0) or 0
                _sd_b = sb['diversity'].get('semantic_diversity', 0) or 0
                f.write(f"- Subspace Diversity: {name_a}={_sd_a:.3f}  {name_b}={_sd_b:.3f}\n")
            f.write("\n")

        f.write("---\n\n")

        # Detailed Metrics
        f.write("## Detailed Metrics Comparison\n\n")
        f.write(comparison_df.to_markdown(index=False))
        f.write("\n\n---\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        winner = name_a if a_wins > b_wins else name_b if b_wins > a_wins else "Tie"
        f.write(f"**Overall Winner**: {winner} ({a_wins} vs {b_wins} metrics)\n\n")
    
    print(f"\nReport saved: {output_path}")
