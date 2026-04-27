"""
Test script for question_quality.py - compares QUIS vs Baseline

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/test/test_question_quality.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.question_quality import (
    compute_question_diversity,
    compute_question_specificity,
    compute_question_insight_alignment,
    compute_question_novelty,
    compute_reason_insight_coherence,
    compute_question_quality
)
from evaluation.configs.test_config import (
    QUIS_INSIGHTS_PATH,
    BASELINE_INSIGHTS_PATH
)
import json

# Test question quality
print("Testing question_quality.py - QUIS vs Baseline")
print("="*70)

insights_ifq_path = QUIS_INSIGHTS_PATH
insights_baseline_path = BASELINE_INSIGHTS_PATH

print(f"Loading QUIS insights from: {insights_ifq_path}")
print(f"Loading Baseline insights from: {insights_baseline_path}")

try:
    # Load QUIS insights
    with open(insights_ifq_path, 'r', encoding='utf-8') as f:
        insights_ifq = json.load(f)
    print(f"QUIS insights loaded: {len(insights_ifq)} insights")
    
    # Load Baseline insights
    with open(insights_baseline_path, 'r', encoding='utf-8') as f:
        insights_baseline = json.load(f)
    print(f"Baseline insights loaded: {len(insights_baseline)} insights")
    
    # Compute question diversity for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Question Diversity...")
    print("-"*70)
    qdiv_ifq = compute_question_diversity(insights_ifq)
    
    print(f"QUIS Results:")
    print(f"  - Question Diversity: {qdiv_ifq['question_diversity']:.3f}")
    print(f"  - Avg Similarity: {qdiv_ifq['avg_similarity']:.3f}")
    print(f"  - Num Questions: {qdiv_ifq['num_questions']}")
    
    # Compute question diversity for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Question Diversity...")
    print("-"*70)
    qdiv_baseline = compute_question_diversity(insights_baseline)
    
    print(f"Baseline Results:")
    print(f"  - Question Diversity: {qdiv_baseline['question_diversity']:.3f}")
    print(f"  - Avg Similarity: {qdiv_baseline['avg_similarity']:.3f}")
    print(f"  - Num Questions: {qdiv_baseline['num_questions']}")
    
    # Compute question specificity for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Question Specificity...")
    print("-"*70)
    qspec_ifq = compute_question_specificity(insights_ifq)
    
    print(f"QUIS Results:")
    print(f"  - Specificity Mean: {qspec_ifq['question_specificity_mean']:.2f} tokens")
    print(f"  - Specificity Std: {qspec_ifq['question_specificity_std']:.2f}")
    print(f"  - Num Questions: {qspec_ifq['num_questions']}")
    
    # Compute question specificity for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Question Specificity...")
    print("-"*70)
    qspec_baseline = compute_question_specificity(insights_baseline)
    
    print(f"Baseline Results:")
    print(f"  - Specificity Mean: {qspec_baseline['question_specificity_mean']:.2f} tokens")
    print(f"  - Specificity Std: {qspec_baseline['question_specificity_std']:.2f}")
    print(f"  - Num Questions: {qspec_baseline['num_questions']}")
    
    # Compute question-insight alignment for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Question-Insight Alignment...")
    print("-"*70)
    qalign_ifq = compute_question_insight_alignment(insights_ifq)
    
    print(f"QUIS Results:")
    print(f"  - Alignment: {qalign_ifq['question_insight_alignment']:.3f}")
    print(f"  - Alignment Std: {qalign_ifq['question_insight_alignment_std']:.3f}")
    print(f"  - Num Pairs: {qalign_ifq['num_pairs']}")
    
    # Compute question-insight alignment for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Question-Insight Alignment...")
    print("-"*70)
    qalign_baseline = compute_question_insight_alignment(insights_baseline)
    
    print(f"Baseline Results:")
    print(f"  - Alignment: {qalign_baseline['question_insight_alignment']:.3f}")
    print(f"  - Alignment Std: {qalign_baseline['question_insight_alignment_std']:.3f}")
    print(f"  - Num Pairs: {qalign_baseline['num_pairs']}")
    
    # Compute reason-insight coherence for QUIS
    print("\n" + "-"*70)
    print("Computing QUIS Reason-Insight Coherence...")
    print("-"*70)
    rcoh_ifq = compute_reason_insight_coherence(insights_ifq, system_name="quis")
    
    print(f"QUIS Results:")
    print(f"  - Coherence: {rcoh_ifq['reason_insight_coherence']:.3f}")
    print(f"  - Coherence Std: {rcoh_ifq['reason_insight_coherence_std']:.3f}")
    print(f"  - Num Pairs: {rcoh_ifq['num_pairs']}")
    
    # Compute reason-insight coherence for Baseline
    print("\n" + "-"*70)
    print("Computing Baseline Reason-Insight Coherence...")
    print("-"*70)
    rcoh_baseline = compute_reason_insight_coherence(insights_baseline, system_name="baseline")
    
    print(f"Baseline Results:")
    print(f"  - Coherence: {rcoh_baseline['reason_insight_coherence']:.3f}")
    print(f"  - Coherence Std: {rcoh_baseline['reason_insight_coherence_std']:.3f}")
    print(f"  - Num Pairs: {rcoh_baseline['num_pairs']}")
    
    # Compute question novelty (cross-system)
    print("\n" + "-"*70)
    print("Computing Question Novelty (cross-system)...")
    print("-"*70)
    qnovelty = compute_question_novelty(insights_ifq, insights_baseline, system_name="quis")
    
    print(f"Question Novelty Results:")
    print(f"  - QUIS vs Baseline Novelty: {qnovelty['question_novelty']:.3f}")
    print(f"  - Novel Count: {qnovelty['novel_count']}")
    print(f"  - Total Count: {qnovelty['total_count']}")
    print(f"  - Avg Max Similarity: {qnovelty['avg_max_similarity']:.3f}")
    print(f"  - Tau: {qnovelty['tau']}")
    
    # Compute all question quality metrics for QUIS
    print("\n" + "-"*70)
    print("Computing All QUIS Question Quality Metrics...")
    print("-"*70)
    qq_ifq = compute_question_quality(insights_ifq, system_name="quis")
    
    print(f"QUIS All Metrics:")
    print(f"  - Question Diversity: {qq_ifq['question_diversity']['question_diversity']:.3f}")
    print(f"  - Question Specificity: {qq_ifq['question_specificity']['question_specificity_mean']:.2f}")
    print(f"  - Q-I Alignment: {qq_ifq['question_insight_alignment']['question_insight_alignment']:.3f}")
    print(f"  - R-I Coherence: {qq_ifq['reason_insight_coherence']['reason_insight_coherence']:.3f}")
    
    # Compute all question quality metrics for Baseline
    print("\n" + "-"*70)
    print("Computing All Baseline Question Quality Metrics...")
    print("-"*70)
    qq_baseline = compute_question_quality(insights_baseline, system_name="baseline")
    
    print(f"Baseline All Metrics:")
    print(f"  - Question Diversity: {qq_baseline['question_diversity']['question_diversity']:.3f}")
    print(f"  - Question Specificity: {qq_baseline['question_specificity']['question_specificity_mean']:.2f}")
    print(f"  - Q-I Alignment: {qq_baseline['question_insight_alignment']['question_insight_alignment']:.3f}")
    print(f"  - R-I Coherence: {qq_baseline['reason_insight_coherence']['reason_insight_coherence']:.3f}")
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    print(f"QUIS Question Diversity: {qdiv_ifq['question_diversity']:.3f}")
    print(f"Baseline Question Diversity: {qdiv_baseline['question_diversity']:.3f}")
    
    if qdiv_ifq['question_diversity'] > qdiv_baseline['question_diversity']:
        qdiv_winner = "QUIS"
        qdiv_diff = qdiv_ifq['question_diversity'] - qdiv_baseline['question_diversity']
    else:
        qdiv_winner = "Baseline"
        qdiv_diff = qdiv_baseline['question_diversity'] - qdiv_ifq['question_diversity']
    
    print(f"Question Diversity Winner: {qdiv_winner} (by {qdiv_diff:.3f})")
    
    print(f"\nQUIS Question Specificity: {qspec_ifq['question_specificity_mean']:.2f}")
    print(f"Baseline Question Specificity: {qspec_baseline['question_specificity_mean']:.2f}")
    
    if qspec_ifq['question_specificity_mean'] > qspec_baseline['question_specificity_mean']:
        qspec_winner = "QUIS"
        qspec_diff = qspec_ifq['question_specificity_mean'] - qspec_baseline['question_specificity_mean']
    else:
        qspec_winner = "Baseline"
        qspec_diff = qspec_baseline['question_specificity_mean'] - qspec_ifq['question_specificity_mean']
    
    print(f"Question Specificity Winner: {qspec_winner} (by {qspec_diff:.2f} tokens)")
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
