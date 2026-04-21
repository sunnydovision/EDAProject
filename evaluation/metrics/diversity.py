"""
Insight diversity metric computation.

Measures diversity from four complementary aspects:
1. Semantic diversity (meaning difference)
2. Subspace diversity (column exploration)
3. Value diversity (value exploration within columns)
4. Dedup rate (exact duplicate insights)
"""

import math
from collections import Counter
from typing import List, Dict, Any, Optional


def compute_semantic_diversity(
    insights: List[Dict],
    tau: float = 0.85
) -> Dict[str, Any]:
    """
    Compute semantic diversity using embedding-based similarity.
    
    D_sem = 1 - avg_similarity
    avg_similarity = (2 / (N(N-1))) * Σ_{i<j} cos_sim(e_i, e_j)
    
    Args:
        insights: List of insight dictionaries
        tau: Similarity threshold (default: 0.85)
        
    Returns:
        Dictionary with semantic diversity metrics
    """
    if len(insights) < 2:
        return {
            'semantic_diversity': 0.0,
            'avg_similarity': 0.0,
            'num_insights': len(insights)
        }
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Normalize insights to structured representation
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
            'semantic_diversity': float(diversity),
            'avg_similarity': float(avg_similarity),
            'num_insights': n
        }
    except Exception as e:
        print(f"Semantic diversity computation failed: {e}")
        return {
            'semantic_diversity': 0.0,
            'avg_similarity': 0.0,
            'num_insights': len(insights),
            'error': str(e)
        }


def compute_subspace_diversity(insights: List[Dict]) -> Optional[Dict[str, Any]]:
    """
    Compute subspace diversity (column exploration).
    
    D_sub = - Σ (p_c * log(p_c))
    p_c = count(column c) / total
    
    Args:
        insights: List of insight dictionaries
        
    Returns:
        Dictionary with subspace diversity metrics, or None if no subspace exists
    """
    columns_used = []
    has_subspace = False
    
    for ins in insights:
        insight_data = ins.get('insight', ins)
        subspace = insight_data.get('subspace', [])
        
        if subspace:
            has_subspace = True
            for col, val in subspace:
                columns_used.append(col)
    
    if not has_subspace or len(columns_used) == 0:
        return None
    
    # Compute entropy
    counter = Counter(columns_used)
    total = len(columns_used)
    
    entropy = 0.0
    for count in counter.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log(p)
    
    # Also compute simple count ratio
    unique_cols = len(counter)
    count_ratio = unique_cols / len(insights)
    
    return {
        'subspace_diversity_entropy': float(entropy),
        'subspace_diversity_count_ratio': float(count_ratio),
        'unique_columns': unique_cols,
        'total_columns': total,
        'column_distribution': dict(counter)
    }


def compute_value_diversity(insights: List[Dict]) -> Optional[Dict[str, Any]]:
    """
    Compute value diversity (value exploration within columns).
    
    D_val = |unique (column, value) pairs| / total_pairs
    
    Args:
        insights: List of insight dictionaries
        
    Returns:
        Dictionary with value diversity metrics, or None if no subspace exists
    """
    pairs = []
    has_subspace = False
    
    for ins in insights:
        insight_data = ins.get('insight', ins)
        subspace = insight_data.get('subspace', [])
        
        if subspace:
            has_subspace = True
            for col, val in subspace:
                pairs.append((col, val))
    
    if not has_subspace or len(pairs) == 0:
        return None
    
    unique_pairs = set(pairs)
    diversity = len(unique_pairs) / len(pairs)
    
    return {
        'value_diversity': float(diversity),
        'unique_pairs': len(unique_pairs),
        'total_pairs': len(pairs)
    }


def compute_dedup_rate(insights: List[Dict]) -> Dict[str, Any]:
    """
    Compute exact duplicate insight rate.
    
    Dedup = 1 - |unique insights| / |I|
    Unique = distinct by (pattern, breakdown, measure, subspace)
    
    Args:
        insights: List of insight dictionaries
        
    Returns:
        Dictionary with dedup rate metrics
    """
    seen = set()
    
    for ins in insights:
        insight_data = ins.get('insight', ins)
        
        # Create key from pattern, breakdown, measure, subspace
        subspace = insight_data.get('subspace', [])
        # Normalize subspace to tuple of tuples for hashing
        subspace_key = tuple(tuple(pair) for pair in subspace) if subspace else ()
        
        key = (
            insight_data.get('pattern', ''),
            insight_data.get('breakdown', ''),
            insight_data.get('measure', ''),
            subspace_key
        )
        seen.add(key)
    
    unique_count = len(seen)
    total_count = len(insights)
    dedup_rate = 1 - (unique_count / total_count) if total_count > 0 else 0.0
    
    return {
        'dedup_rate': float(dedup_rate),
        'unique_count': unique_count,
        'total_count': total_count,
        'duplicate_count': total_count - unique_count
    }


def compute_diversity(
    insights: List[Dict],
    tau: float = 0.85
) -> Dict[str, Any]:
    """
    Compute all diversity metrics.
    
    Returns 4 metrics:
    1. Semantic diversity (meaning difference)
    2. Subspace diversity (column exploration) - None if no subspace
    3. Value diversity (value exploration) - None if no subspace
    4. Dedup rate (exact duplicates)
    
    Args:
        insights: List of insight dictionaries
        tau: Similarity threshold for semantic diversity (default: 0.85)
        
    Returns:
        Dictionary with all diversity metrics
    """
    # Compute semantic diversity
    semantic_result = compute_semantic_diversity(insights, tau)
    
    # Compute subspace diversity (may be None)
    subspace_result = compute_subspace_diversity(insights)
    
    # Compute value diversity (may be None)
    value_result = compute_value_diversity(insights)
    
    # Compute dedup rate
    dedup_result = compute_dedup_rate(insights)
    
    # Combine all results
    result = {
        **semantic_result,
        'subspace_diversity': subspace_result,
        'value_diversity': value_result,
        **dedup_result
    }
    
    return result
