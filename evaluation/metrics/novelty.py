"""
Insight novelty metric computation.

Measures how many insights are novel compared to another system.
"""

import pandas as pd
from typing import List, Dict, Any


def compute_novelty(
    insights_a: List[Dict],
    insights_b: List[Dict],
    tau: float = 0.85
) -> Dict[str, Any]:
    """
    Compute novelty of system A's insights compared to system B.
    
    Novelty = (1/|A|) * Sigma 1(max_j sim(i, j) < tau)
    
    Args:
        insights_a: Insights from system A
        insights_b: Insights from system B
        tau: Similarity threshold (default: 0.85)
        
    Returns:
        Dictionary with novelty metrics
    """
    if len(insights_a) == 0:
        return {
            'novelty': 0.0,
            'novel_count': 0,
            'total_count': 0,
            'avg_max_similarity': 0.0
        }
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Extract insight strings for comparison
        a_strings = [_insight_to_string(ins) for ins in insights_a]
        b_strings = [_insight_to_string(ins) for ins in insights_b]
        
        # Embed insights
        model = SentenceTransformer('all-MiniLM-L6-v2')
        a_embeddings = model.encode(a_strings)
        b_embeddings = model.encode(b_strings)
        
        # Compute pairwise similarities
        similarities = cosine_similarity(a_embeddings, b_embeddings)
        
        # For each insight in A, find max similarity to any insight in B
        max_similarities = similarities.max(axis=1)
        
        # Count novel insights (max similarity < tau)
        novel_count = (max_similarities < tau).sum()
        
        return {
            'novelty': novel_count / len(insights_a),
            'novel_count': int(novel_count),
            'total_count': len(insights_a),
            'avg_max_similarity': float(max_similarities.mean()),
            'tau': tau
        }
    except Exception as e:
        print(f"Novelty computation failed: {e}")
        return {
            'novelty': 0.0,
            'novel_count': 0,
            'total_count': len(insights_a),
            'avg_max_similarity': 0.0,
            'error': str(e)
        }


def _insight_to_string(insight: Dict) -> str:
    """Convert insight to structured representation per newEvaluation.md.
    
    Format: "{breakdown} | {measure} | {pattern} | {condition}"
    """
    ins = insight.get('insight', insight)
    breakdown = ins.get('breakdown', '')
    measure = ins.get('measure', '')
    pattern = ins.get('pattern', '')
    subspace = ins.get('subspace', [])
    
    # Convert subspace to condition string
    if subspace:
        condition_strs = [f"{k}={v}" for k, v in subspace]
        condition = ", ".join(condition_strs)
    else:
        condition = ''
    
    return f"{breakdown} | {measure} | {pattern} | {condition}"
