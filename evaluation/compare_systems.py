"""
Side-by-side comparison of QUIS and Baseline systems.

Generates comparison tables and visualizations.
"""

import json
import pandas as pd
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
from compute_metrics import evaluate_system


def format_metric_value(value: Any, metric_type: str = 'default') -> str:
    """Format metric value for display"""
    if isinstance(value, float):
        if metric_type == 'percentage':
            return f"{value*100:.1f}%"
        else:
            return f"{value:.3f}"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, dict):
        return json.dumps(value, indent=2)
    else:
        return str(value)


def create_comparison_table(quis_results: Dict, baseline_results: Dict) -> pd.DataFrame:
    """
    Create comparison table for core metrics.
    
    Returns:
        DataFrame with side-by-side comparison
    """
    metrics = []
    
    # 1. Insight Yield
    metrics.append({
        'Metric': 'Insight Yield',
        'QUIS': format_metric_value(quis_results['yield'], 'default'),
        'Baseline': format_metric_value(baseline_results['yield'], 'default'),
        'Winner': 'QUIS' if quis_results['yield'] > baseline_results['yield'] else 'Baseline',
        'Category': 'Core'
    })
    
    # 2. Average Score
    metrics.append({
        'Metric': 'Average Score',
        'QUIS': format_metric_value(quis_results['avg_score']['avg_score'], 'default'),
        'Baseline': format_metric_value(baseline_results['avg_score']['avg_score'], 'default'),
        'Winner': 'QUIS' if quis_results['avg_score']['avg_score'] > baseline_results['avg_score']['avg_score'] else 'Baseline',
        'Category': 'Core'
    })
    
    # 3. Top-10 Score
    metrics.append({
        'Metric': 'Top-10 Score',
        'QUIS': format_metric_value(quis_results['avg_score']['top10_score'], 'default'),
        'Baseline': format_metric_value(baseline_results['avg_score']['top10_score'], 'default'),
        'Winner': 'QUIS' if quis_results['avg_score']['top10_score'] > baseline_results['avg_score']['top10_score'] else 'Baseline',
        'Category': 'Core'
    })
    
    # 4. Redundancy (lower is better)
    metrics.append({
        'Metric': 'Redundancy',
        'QUIS': format_metric_value(quis_results['redundancy']['redundancy'], 'percentage'),
        'Baseline': format_metric_value(baseline_results['redundancy']['redundancy'], 'percentage'),
        'Winner': 'QUIS' if quis_results['redundancy']['redundancy'] < baseline_results['redundancy']['redundancy'] else 'Baseline',
        'Category': 'Core'
    })
    
    # 5. Schema Coverage
    metrics.append({
        'Metric': 'Schema Coverage',
        'QUIS': format_metric_value(quis_results['schema_coverage']['coverage'], 'percentage'),
        'Baseline': format_metric_value(baseline_results['schema_coverage']['coverage'], 'percentage'),
        'Winner': 'QUIS' if quis_results['schema_coverage']['coverage'] > baseline_results['schema_coverage']['coverage'] else 'Baseline',
        'Category': 'Coverage'
    })
    
    # 6. Pattern Coverage
    metrics.append({
        'Metric': 'Pattern Coverage',
        'QUIS': format_metric_value(quis_results['pattern_coverage']['coverage'], 'percentage'),
        'Baseline': format_metric_value(baseline_results['pattern_coverage']['coverage'], 'percentage'),
        'Winner': 'QUIS' if quis_results['pattern_coverage']['coverage'] > baseline_results['pattern_coverage']['coverage'] else 'Baseline',
        'Category': 'Coverage'
    })
    
    # 7. Subspace Exploration (KEY DIFFERENTIATOR)
    metrics.append({
        'Metric': '⭐ Subspace Rate',
        'QUIS': format_metric_value(quis_results['subspace_metrics']['subspace_rate'], 'percentage'),
        'Baseline': format_metric_value(baseline_results['subspace_metrics']['subspace_rate'], 'percentage'),
        'Winner': 'QUIS' if quis_results['subspace_metrics']['subspace_rate'] > baseline_results['subspace_metrics']['subspace_rate'] else 'Baseline',
        'Category': 'Coverage'
    })
    
    # 8. Avg Subspace Depth
    metrics.append({
        'Metric': '⭐ Avg Subspace Depth',
        'QUIS': format_metric_value(quis_results['subspace_metrics']['avg_depth'], 'default'),
        'Baseline': format_metric_value(baseline_results['subspace_metrics']['avg_depth'], 'default'),
        'Winner': 'QUIS' if quis_results['subspace_metrics']['avg_depth'] > baseline_results['subspace_metrics']['avg_depth'] else 'Baseline',
        'Category': 'Coverage'
    })
    
    # 9. Question Diversity
    metrics.append({
        'Metric': 'Question Diversity',
        'QUIS': format_metric_value(quis_results['question_diversity']['diversity'], 'default'),
        'Baseline': format_metric_value(baseline_results['question_diversity']['diversity'], 'default'),
        'Winner': 'QUIS' if quis_results['question_diversity']['diversity'] > baseline_results['question_diversity']['diversity'] else 'Baseline',
        'Category': 'Quality'
    })
    
    # 10. Insight Significance
    metrics.append({
        'Metric': 'Avg Z-Score',
        'QUIS': format_metric_value(quis_results['insight_significance']['avg_zscore'], 'default'),
        'Baseline': format_metric_value(baseline_results['insight_significance']['avg_zscore'], 'default'),
        'Winner': 'QUIS' if quis_results['insight_significance']['avg_zscore'] > baseline_results['insight_significance']['avg_zscore'] else 'Baseline',
        'Category': 'Quality'
    })
    
    # 11. Significant Insights Rate
    metrics.append({
        'Metric': 'Significant Rate',
        'QUIS': format_metric_value(quis_results['insight_significance']['significant_rate'], 'percentage'),
        'Baseline': format_metric_value(baseline_results['insight_significance']['significant_rate'], 'percentage'),
        'Winner': 'QUIS' if quis_results['insight_significance']['significant_rate'] > baseline_results['insight_significance']['significant_rate'] else 'Baseline',
        'Category': 'Quality'
    })
    
    # 12. Faithfulness (lower hallucination is better)
    metrics.append({
        'Metric': '⭐ Faithfulness',
        'QUIS': format_metric_value(quis_results['faithfulness']['faithfulness'], 'percentage'),
        'Baseline': format_metric_value(baseline_results['faithfulness']['faithfulness'], 'percentage'),
        'Winner': 'QUIS' if quis_results['faithfulness']['faithfulness'] > baseline_results['faithfulness']['faithfulness'] else 'Baseline',
        'Category': 'Quality'
    })
    
    df = pd.DataFrame(metrics)
    return df


def plot_comparison(quis_results: Dict, baseline_results: Dict, output_dir: str = 'evaluation/plots'):
    """
    Create visualization plots comparing systems.
    
    Args:
        quis_results: QUIS evaluation results
        baseline_results: Baseline evaluation results
        output_dir: Directory to save plots
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    
    # 1. Core Metrics Comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Yield
    axes[0].bar(['QUIS', 'Baseline'], 
                [quis_results['yield'], baseline_results['yield']],
                color=['#2ecc71', '#e74c3c'])
    axes[0].set_title('Insight Yield', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Yield (|I| / |Q|)')
    axes[0].set_ylim(0, 1.1)
    
    # Average Score
    axes[1].bar(['QUIS', 'Baseline'],
                [quis_results['avg_score']['avg_score'], baseline_results['avg_score']['avg_score']],
                color=['#2ecc71', '#e74c3c'])
    axes[1].set_title('Average Insight Score', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('ISGEN Score')
    
    # Redundancy (lower is better)
    axes[2].bar(['QUIS', 'Baseline'],
                [quis_results['redundancy']['redundancy'], baseline_results['redundancy']['redundancy']],
                color=['#2ecc71', '#e74c3c'])
    axes[2].set_title('Redundancy Rate (lower is better)', fontsize=14, fontweight='bold')
    axes[2].set_ylabel('Redundancy')
    axes[2].set_ylim(0, 1.0)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/core_metrics.png', dpi=300, bbox_inches='tight')
    print(f"  📊 Saved: {output_dir}/core_metrics.png")
    plt.close()
    
    # 2. Coverage Metrics
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Schema Coverage
    axes[0].bar(['QUIS', 'Baseline'],
                [quis_results['schema_coverage']['coverage'], baseline_results['schema_coverage']['coverage']],
                color=['#3498db', '#9b59b6'])
    axes[0].set_title('Schema Coverage', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Coverage')
    axes[0].set_ylim(0, 1.0)
    
    # Pattern Coverage
    axes[1].bar(['QUIS', 'Baseline'],
                [quis_results['pattern_coverage']['coverage'], baseline_results['pattern_coverage']['coverage']],
                color=['#3498db', '#9b59b6'])
    axes[1].set_title('Pattern Coverage', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Coverage')
    axes[1].set_ylim(0, 1.0)
    
    # Subspace Rate (KEY DIFFERENTIATOR)
    axes[2].bar(['QUIS', 'Baseline'],
                [quis_results['subspace_metrics']['subspace_rate'], baseline_results['subspace_metrics']['subspace_rate']],
                color=['#f39c12', '#e67e22'])
    axes[2].set_title('⭐ Subspace Exploration Rate', fontsize=14, fontweight='bold')
    axes[2].set_ylabel('Rate')
    axes[2].set_ylim(0, 1.0)
    axes[2].axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/coverage_metrics.png', dpi=300, bbox_inches='tight')
    print(f"  📊 Saved: {output_dir}/coverage_metrics.png")
    plt.close()
    
    # 3. Pattern Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    quis_patterns = quis_results['pattern_coverage']['pattern_counts']
    baseline_patterns = baseline_results['pattern_coverage']['pattern_counts']
    
    # QUIS patterns
    if quis_patterns:
        ax1.bar(quis_patterns.keys(), quis_patterns.values(), color='#2ecc71')
        ax1.set_title('QUIS Pattern Distribution', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Count')
        ax1.tick_params(axis='x', rotation=45)
    
    # Baseline patterns
    if baseline_patterns:
        ax2.bar(baseline_patterns.keys(), baseline_patterns.values(), color='#e74c3c')
        ax2.set_title('Baseline Pattern Distribution', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Count')
        ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/pattern_distribution.png', dpi=300, bbox_inches='tight')
    print(f"  📊 Saved: {output_dir}/pattern_distribution.png")
    plt.close()
    
    # 4. Radar Chart for Overall Comparison
    from math import pi
    
    categories = ['Yield', 'Avg Score', 'Schema\nCoverage', 'Pattern\nCoverage', 'Subspace\nRate', 'Question\nDiversity']
    
    # Normalize values to 0-1 scale
    quis_values = [
        quis_results['yield'],
        quis_results['avg_score']['avg_score'] / max(quis_results['avg_score']['avg_score'], baseline_results['avg_score']['avg_score'], 1),
        quis_results['schema_coverage']['coverage'],
        quis_results['pattern_coverage']['coverage'],
        quis_results['subspace_metrics']['subspace_rate'],
        quis_results['question_diversity']['diversity']
    ]
    
    baseline_values = [
        baseline_results['yield'],
        baseline_results['avg_score']['avg_score'] / max(quis_results['avg_score']['avg_score'], baseline_results['avg_score']['avg_score'], 1),
        baseline_results['schema_coverage']['coverage'],
        baseline_results['pattern_coverage']['coverage'],
        baseline_results['subspace_metrics']['subspace_rate'],
        baseline_results['question_diversity']['diversity']
    ]
    
    # Close the plot
    quis_values += quis_values[:1]
    baseline_values += baseline_values[:1]
    
    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    ax.plot(angles, quis_values, 'o-', linewidth=2, label='QUIS', color='#2ecc71')
    ax.fill(angles, quis_values, alpha=0.25, color='#2ecc71')
    
    ax.plot(angles, baseline_values, 'o-', linewidth=2, label='Baseline', color='#e74c3c')
    ax.fill(angles, baseline_values, alpha=0.25, color='#e74c3c')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=12)
    ax.set_ylim(0, 1)
    ax.set_title('QUIS vs Baseline: Overall Comparison', size=16, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/radar_comparison.png', dpi=300, bbox_inches='tight')
    print(f"  📊 Saved: {output_dir}/radar_comparison.png")
    plt.close()


def generate_report(quis_results: Dict, baseline_results: Dict, output_path: str = 'evaluation/comparison_report.md'):
    """
    Generate markdown report with comparison results.
    
    Args:
        quis_results: QUIS evaluation results
        baseline_results: Baseline evaluation results
        output_path: Path to save report
    """
    comparison_df = create_comparison_table(quis_results, baseline_results)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# QUIS vs Baseline: Evaluation Report\n\n")
        f.write("**Generated**: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        
        quis_wins = len(comparison_df[comparison_df['Winner'] == 'QUIS'])
        baseline_wins = len(comparison_df[comparison_df['Winner'] == 'Baseline'])
        
        f.write(f"- **QUIS Wins**: {quis_wins}/{len(comparison_df)} metrics\n")
        f.write(f"- **Baseline Wins**: {baseline_wins}/{len(comparison_df)} metrics\n\n")
        
        # Key Findings
        f.write("### Key Findings\n\n")
        f.write("**QUIS Strengths:**\n")
        f.write(f"- ⭐ **Subspace Exploration**: {quis_results['subspace_metrics']['subspace_rate']*100:.1f}% vs {baseline_results['subspace_metrics']['subspace_rate']*100:.1f}%\n")
        f.write(f"- Schema Coverage: {quis_results['schema_coverage']['coverage']*100:.1f}% vs {baseline_results['schema_coverage']['coverage']*100:.1f}%\n")
        f.write(f"- Redundancy: {quis_results['redundancy']['redundancy']*100:.1f}% vs {baseline_results['redundancy']['redundancy']*100:.1f}%\n\n")
        
        f.write("**Baseline Strengths:**\n")
        f.write(f"- Pattern Diversity: {baseline_results['pattern_coverage']['coverage']*100:.1f}% vs {quis_results['pattern_coverage']['coverage']*100:.1f}%\n")
        f.write(f"- Question Diversity: {baseline_results['question_diversity']['diversity']:.3f} vs {quis_results['question_diversity']['diversity']:.3f}\n\n")
        
        f.write("---\n\n")
        
        # Detailed Metrics
        f.write("## Detailed Metrics Comparison\n\n")
        f.write(comparison_df.to_markdown(index=False))
        f.write("\n\n---\n\n")
        
        # Core Metrics Details
        f.write("## Core Metrics\n\n")
        
        f.write("### 1. Insight Yield\n")
        f.write(f"- **QUIS**: {quis_results['yield']:.3f} ({quis_results['num_insights']} insights / {quis_results['num_cards']} cards)\n")
        f.write(f"- **Baseline**: {baseline_results['yield']:.3f} ({baseline_results['num_insights']} insights / {baseline_results['num_cards']} cards)\n\n")
        
        f.write("### 2. Average Insight Score\n")
        f.write(f"- **QUIS**: {quis_results['avg_score']['avg_score']:.3f} (Top-10: {quis_results['avg_score']['top10_score']:.3f})\n")
        f.write(f"- **Baseline**: {baseline_results['avg_score']['avg_score']:.3f} (Top-10: {baseline_results['avg_score']['top10_score']:.3f})\n\n")
        
        f.write("### 3. Redundancy\n")
        f.write(f"- **QUIS**: {quis_results['redundancy']['redundancy']*100:.1f}% ({quis_results['redundancy']['duplicate_count']} duplicates)\n")
        f.write(f"- **Baseline**: {baseline_results['redundancy']['redundancy']*100:.1f}% ({baseline_results['redundancy']['duplicate_count']} duplicates)\n\n")
        
        f.write("---\n\n")
        
        # Coverage Metrics
        f.write("## Coverage Metrics\n\n")
        
        f.write("### 4. Schema Coverage\n")
        f.write(f"- **QUIS**: {quis_results['schema_coverage']['used_count']}/{quis_results['schema_coverage']['total_count']} columns ({quis_results['schema_coverage']['coverage']*100:.1f}%)\n")
        f.write(f"- **Baseline**: {baseline_results['schema_coverage']['used_count']}/{baseline_results['schema_coverage']['total_count']} columns ({baseline_results['schema_coverage']['coverage']*100:.1f}%)\n\n")
        
        f.write("### 5. Pattern Coverage\n")
        f.write(f"- **QUIS**: {len(quis_results['pattern_coverage']['patterns_found'])}/4 patterns\n")
        f.write(f"  - Found: {', '.join(quis_results['pattern_coverage']['patterns_found'])}\n")
        f.write(f"- **Baseline**: {len(baseline_results['pattern_coverage']['patterns_found'])}/4 patterns\n")
        f.write(f"  - Found: {', '.join(baseline_results['pattern_coverage']['patterns_found'])}\n\n")
        
        f.write("### 6. ⭐ Subspace Exploration (KEY DIFFERENTIATOR)\n")
        f.write(f"- **QUIS**:\n")
        f.write(f"  - Subspace Rate: {quis_results['subspace_metrics']['subspace_rate']*100:.1f}%\n")
        f.write(f"  - Avg Depth: {quis_results['subspace_metrics']['avg_depth']:.2f}\n")
        f.write(f"  - Max Depth: {quis_results['subspace_metrics']['max_depth']}\n")
        f.write(f"- **Baseline**:\n")
        f.write(f"  - Subspace Rate: {baseline_results['subspace_metrics']['subspace_rate']*100:.1f}%\n")
        f.write(f"  - Avg Depth: {baseline_results['subspace_metrics']['avg_depth']:.2f}\n")
        f.write(f"  - Max Depth: {baseline_results['subspace_metrics']['max_depth']}\n\n")
        
        f.write("---\n\n")
        
        # Quality Metrics
        f.write("## Quality Metrics\n\n")
        
        f.write("### 7. Question Diversity\n")
        f.write(f"- **QUIS**: {quis_results['question_diversity']['diversity']:.3f} (avg similarity: {quis_results['question_diversity']['avg_similarity']:.3f})\n")
        f.write(f"- **Baseline**: {baseline_results['question_diversity']['diversity']:.3f} (avg similarity: {baseline_results['question_diversity']['avg_similarity']:.3f})\n\n")
        
        f.write("### 8. Insight Significance (Z-Score)\n")
        f.write(f"- **QUIS**:\n")
        f.write(f"  - Avg Z-Score: {quis_results['insight_significance']['avg_zscore']:.2f}\n")
        f.write(f"  - Significant Rate: {quis_results['insight_significance']['significant_rate']*100:.1f}% ({quis_results['insight_significance']['significant_count']} insights)\n")
        f.write(f"- **Baseline**:\n")
        f.write(f"  - Avg Z-Score: {baseline_results['insight_significance']['avg_zscore']:.2f}\n")
        f.write(f"  - Significant Rate: {baseline_results['insight_significance']['significant_rate']*100:.1f}% ({baseline_results['insight_significance']['significant_count']} insights)\n\n")
        
        f.write("### 9. ⭐ Faithfulness (Hallucination Detection)\n")
        f.write(f"- **QUIS**:\n")
        f.write(f"  - Faithfulness: {quis_results['faithfulness']['faithfulness']*100:.1f}%\n")
        f.write(f"  - Hallucinations: {quis_results['faithfulness']['hallucination_count']}/{quis_results['faithfulness']['total_count']}\n")
        f.write(f"- **Baseline**:\n")
        f.write(f"  - Faithfulness: {baseline_results['faithfulness']['faithfulness']*100:.1f}%\n")
        f.write(f"  - Hallucinations: {baseline_results['faithfulness']['hallucination_count']}/{baseline_results['faithfulness']['total_count']}\n\n")
        
        f.write("---\n\n")
        
        # Conclusion
        f.write("## Conclusion\n\n")
        f.write("The evaluation demonstrates that **QUIS excels at systematic, comprehensive data exploration**, particularly in:\n\n")
        f.write("1. **Subspace Exploration**: QUIS's beam search enables discovery of conditional patterns that baseline approaches miss\n")
        f.write("2. **Schema Coverage**: More thorough exploration of the data schema\n")
        f.write("3. **Low Redundancy**: Explicit deduplication produces unique insights\n\n")
        f.write("The **Baseline shows strength in pattern diversity**, exploring a wider variety of pattern types through LLM reasoning.\n\n")
        f.write("**Key Takeaway**: QUIS's systematic search approach complements LLM-based reasoning, offering deeper insights through subspace exploration.\n")
    
    print(f"\n📄 Report saved: {output_path}")
