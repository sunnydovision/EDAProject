"""
Insight diversity metric computation.

Measures how spread out the insights are (non-redundancy).
"""

import pandas as pd
from typing import List, Dict, Any


def compute_diversity(
    insights: List[Dict],
    tau: float = 0.85
) -> Dict[str, Any]:
    """
    Compute diversity of insights.
    
    Diversity = (2 / (N(N-1))) * Sigma_{i<j} (1 - sim(i, j))
    
    Args:
        insights: List of insight dictionaries
        tau: Similarity threshold (default: 0.85)
        
    Returns:
        Dictionary with diversity metrics
    """
    if len(insights) < 2:
        return {
            'diversity': 0.0,
            'avg_similarity': 0.0,
            'num_questions': len(insights)
        }
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Normalize insights to structured representation per newEvaluation.md
        # Format: "{breakdown} | {measure} | {pattern} | {condition}"
        representations = []
        for ins in insights:
            insight_data = ins.get('insight', ins)
            breakdown = insight_data.get('breakdown', '')
            measure = insight_data.get('measure', '')
            pattern = insight_data.get('pattern', '')
            subspace = insight_data.get('subspace', [])
            
            # Convert subspace to condition string
            if subspace:
                condition_strs = [f"{k}={v}" for k, v in subspace]
                condition = ", ".join(condition_strs)
            else:
                condition = ''
            
            rep = f"{breakdown} | {measure} | {pattern} | {condition}"
            representations.append(rep)
        
        # Embed representations
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(representations)
        
        # Compute pairwise cosine similarity
        similarity_matrix = cosine_similarity(embeddings)
        
        # Calculate average similarity (excluding diagonal)
        n = len(similarity_matrix)
        total_similarity = similarity_matrix.sum() - similarity_matrix.trace()
        avg_similarity = total_similarity / (n * (n - 1))
        
        # Diversity = 1 - avg_similarity
        diversity = 1 - avg_similarity
        
        return {
            'diversity': float(diversity),
            'avg_similarity': float(avg_similarity),
            'num_questions': n
        }
    except Exception as e:
        print(f"Diversity computation failed: {e}")
        return {
            'diversity': 0.0,
            'avg_similarity': 0.0,
            'num_questions': len(insights),
            'error': str(e)
        }
