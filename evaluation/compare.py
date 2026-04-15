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
    
    # 4. Insight Diversity
    metrics.append({
        'Metric': '4. Insight Diversity',
        name_a: format_metric_value(results_a['question_diversity']['diversity'], 'default'),
        name_b: format_metric_value(results_b['question_diversity']['diversity'], 'default'),
        'Winner': name_a if results_a['question_diversity']['diversity'] > results_b['question_diversity']['diversity'] else name_b,
        'Category': 'Core',
        'Description': 'Non-redundancy - không trùng lặp'
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
        f.write(f"- **Insight Diversity**: {results_a['question_diversity']['diversity']:.3f} vs {results_b['question_diversity']['diversity']:.3f}\n")
        
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
        
        # Detailed Metrics
        f.write("## Detailed Metrics Comparison\n\n")
        f.write(comparison_df.to_markdown(index=False))
        f.write("\n\n---\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        winner = name_a if a_wins > b_wins else name_b if b_wins > a_wins else "Tie"
        f.write(f"**Overall Winner**: {winner} ({a_wins} vs {b_wins} metrics)\n\n")
    
    print(f"\nReport saved: {output_path}")
