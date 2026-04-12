import matplotlib.pyplot as plt
import numpy as np
import os


def plot_evaluation_results(results_a, results_b, output_path="evaluation_results", name_a="IFQ", name_b="Baseline"):
    """
    Generate evaluation plots using results directly.
    
    Args:
        results_a: Results for system A
        results_b: Results for system B
        output_path: Directory to save plots
        name_a: Name of system A
        name_b: Name of system B
    """
    print(f"\n{'='*70}")
    print("Generating Evaluation Plots")
    print(f"{'='*70}\n")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Extract metrics
    metrics_data = {
        'Faithfulness': {
            name_a: results_a['faithfulness']['faithfulness'] * 100,
            name_b: results_b['faithfulness']['faithfulness'] * 100,
            'Category': 'Core'
        },
        'Statistical Significance': {
            name_a: results_a['insight_significance']['significant_rate'] * 100,
            name_b: results_b['insight_significance']['significant_rate'] * 100,
            'Category': 'Core'
        },
        'Insight Novelty': {
            name_a: results_a['insight_novelty']['novelty'] * 100,
            name_b: results_b['insight_novelty']['novelty'] * 100,
            'Category': 'Core'
        },
        'Insight Diversity': {
            name_a: results_a['question_diversity']['diversity'] * 100,
            name_b: results_b['question_diversity']['diversity'] * 100,
            'Category': 'Core'
        }
    }
    
    # Add efficiency metrics if available
    if results_a.get('time_to_insight') and results_b.get('time_to_insight'):
        time_a = results_a['time_to_insight'].get('time_per_insight_seconds')
        time_b = results_b['time_to_insight'].get('time_per_insight_seconds')
        if time_a is not None and time_b is not None:
            metrics_data['Time per Insight (s)'] = {
                name_a: time_a,
                name_b: time_b,
                'Category': 'Efficiency'
            }
    
    if results_a.get('token_usage') and results_b.get('token_usage'):
        tokens_a = results_a['token_usage'].get('tokens_per_insight')
        tokens_b = results_b['token_usage'].get('tokens_per_insight')
        if tokens_a is not None and tokens_b is not None:
            metrics_data['Tokens per Insight'] = {
                name_a: tokens_a,
                name_b: tokens_b,
                'Category': 'Efficiency'
            }

    # Create figure with subplots (1x2)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'{name_a} vs {name_b}: So sánh Kết quả Đánh giá', fontsize=16, fontweight='bold')

    # 1. Core Metrics Bar Chart
    core_metrics = ['Độ tin cậy', 'Ý nghĩa thống kê', 'Tính mới', 'Đa dạng']
    a_core = [metrics_data[m][name_a] for m in ['Faithfulness', 'Statistical Significance', 'Insight Novelty', 'Insight Diversity']]
    b_core = [metrics_data[m][name_b] for m in ['Faithfulness', 'Statistical Significance', 'Insight Novelty', 'Insight Diversity']]

    x = np.arange(len(core_metrics))
    width = 0.35

    axes[0].bar(x - width/2, a_core, width, label=name_a, color='#2ecc71', alpha=0.8)
    axes[0].bar(x + width/2, b_core, width, label=name_b, color='#3498db', alpha=0.8)
    axes[0].set_ylabel('Điểm (%)', fontsize=12)
    axes[0].set_title('So sánh 4 Metrics Chính', fontsize=14, fontweight='bold', pad=20)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(core_metrics, rotation=45, ha='right')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)
    axes[0].set_ylim(0, 100)

    # Add value labels on bars
    for i, (a_val, b_val) in enumerate(zip(a_core, b_core)):
        axes[0].text(i - width/2, a_val + 2, f'{a_val:.1f}%', ha='center', va='bottom', fontsize=9)
        axes[0].text(i + width/2, b_val + 2, f'{b_val:.1f}%', ha='center', va='bottom', fontsize=9)

    # 2. Radar Chart for Core Metrics
    categories = core_metrics
    N = len(categories)

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    a_values = [metrics_data[m][name_a] for m in ['Faithfulness', 'Statistical Significance', 'Insight Novelty', 'Insight Diversity']]
    b_values = [metrics_data[m][name_b] for m in ['Faithfulness', 'Statistical Significance', 'Insight Novelty', 'Insight Diversity']]

    a_values += a_values[:1]
    b_values += b_values[:1]

    ax = fig.add_subplot(1, 2, 2, projection='polar')
    ax.plot(angles, a_values, 'o-', linewidth=2, label=name_a, color='#2ecc71')
    ax.fill(angles, a_values, alpha=0.25, color='#2ecc71')
    ax.plot(angles, b_values, 'o-', linewidth=2, label=name_b, color='#3498db')
    ax.fill(angles, b_values, alpha=0.25, color='#3498db')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 100)
    ax.set_title('Biểu đồ Radar 4 Metrics Chính', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    ax.tick_params(axis='x', pad=20)

    plt.tight_layout()
    plot1_path = f"{output_path}/evaluation_comparison.png"
    plt.savefig(plot1_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {plot1_path}")
    plt.close()

    # Create additional plot for resource usage (if data available)
    if results_a.get('time_to_insight') and results_b.get('time_to_insight') and \
       results_a.get('token_usage') and results_b.get('token_usage'):
        
        fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
        fig2.suptitle('So sánh Sử dụng Tài nguyên & Hiệu suất', fontsize=16, fontweight='bold')
        
        # Total time
        a_time_total = results_a['time_to_insight'].get('total_time_seconds', 0)
        b_time_total = results_b['time_to_insight'].get('total_time_seconds', 0)
        axes2[0, 0].bar([name_a, name_b], [a_time_total, b_time_total], color=['#9b59b6', '#3498db'], alpha=0.8)
        axes2[0, 0].set_ylabel('Thời gian (giây)', fontsize=12)
        axes2[0, 0].set_title('Tổng Thời gian', fontsize=14, fontweight='bold')
        axes2[0, 0].grid(axis='y', alpha=0.3)
        for i, val in enumerate([a_time_total, b_time_total]):
            axes2[0, 0].text(i, val + max(30, val*0.1), f'{val:.0f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Time per insight
        a_time_per = metrics_data.get('Time per Insight (s)', {}).get(name_a, 0)
        b_time_per = metrics_data.get('Time per Insight (s)', {}).get(name_b, 0)
        if a_time_per > 0 and b_time_per > 0:
            axes2[0, 1].bar([name_a, name_b], [a_time_per, b_time_per], color=['#9b59b6', '#3498db'], alpha=0.8)
            axes2[0, 1].set_ylabel('Thời gian (giây)', fontsize=12)
            axes2[0, 1].set_title('Thời gian / Insight', fontsize=14, fontweight='bold')
            axes2[0, 1].grid(axis='y', alpha=0.3)
            for i, val in enumerate([a_time_per, b_time_per]):
                axes2[0, 1].text(i, val + 0.5, f'{val:.2f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Total tokens
        a_tokens_total = results_a['token_usage'].get('total_tokens', 0)
        b_tokens_total = results_b['token_usage'].get('total_tokens', 0)
        axes2[1, 0].bar([name_a, name_b], [a_tokens_total, b_tokens_total], color=['#e74c3c', '#3498db'], alpha=0.8)
        axes2[1, 0].set_ylabel('Số Tokens', fontsize=12)
        axes2[1, 0].set_title('Tổng Tokens', fontsize=14, fontweight='bold')
        axes2[1, 0].grid(axis='y', alpha=0.3)
        for i, val in enumerate([a_tokens_total, b_tokens_total]):
            axes2[1, 0].text(i, val + max(2000, val*0.1), f'{val:,}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Tokens per insight
        a_tokens_per = metrics_data.get('Tokens per Insight', {}).get(name_a, 0)
        b_tokens_per = metrics_data.get('Tokens per Insight', {}).get(name_b, 0)
        if a_tokens_per > 0 and b_tokens_per > 0:
            axes2[1, 1].bar([name_a, name_b], [a_tokens_per, b_tokens_per], color=['#e74c3c', '#3498db'], alpha=0.8)
            axes2[1, 1].set_ylabel('Số Tokens', fontsize=12)
            axes2[1, 1].set_title('Tokens / Insight', fontsize=14, fontweight='bold')
            axes2[1, 1].grid(axis='y', alpha=0.3)
            for i, val in enumerate([a_tokens_per, b_tokens_per]):
                axes2[1, 1].text(i, val + max(20, val*0.1), f'{val:.0f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plot2_path = f"{output_path}/resource_usage.png"
        plt.savefig(plot2_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved: {plot2_path}")
        plt.close()
    
    print(f"\n✓ Evaluation plots generated successfully!")


if __name__ == "__main__":
    import json
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python plot_evaluation.py <results_a_json> <results_b_json> [output_path]")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        results_a = json.load(f)
    
    with open(sys.argv[2], 'r') as f:
        results_b = json.load(f)
    
    output_path = sys.argv[3] if len(sys.argv) > 3 else "evaluation_results"
    
    plot_evaluation_results(results_a, results_b, output_path)
