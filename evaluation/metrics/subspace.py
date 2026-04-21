"""
Insight subspace count and comparison metric computation.

Counts the total number of subspaces for insights, grouped by pattern.
Also provides filtering and comparative metrics for insights that have subspaces.
"""

from typing import List, Dict, Any
from collections import Counter, defaultdict
import pandas as pd


def filter_insights_with_subspace(insights: List[Dict]) -> List[Dict]:
    """
    Filter and return only insights that have a non-empty subspace.
    
    Args:
        insights: List of insight dictionaries
    
    Returns:
        List of insights that have at least one subspace condition
    """
    return [
        ins for ins in insights
        if ins.get('insight', ins).get('subspace')
    ]


def compute_subspace_metrics(
    insights_a: List[Dict],
    insights_b: List[Dict],
    df_raw: pd.DataFrame,
    df_cleaned: pd.DataFrame,
    csv_path: str = None
) -> Dict[str, Any]:
    """
    Compare metrics between two systems, restricted to insights that have subspaces.
    
    Computes faithfulness, significance, novelty, and diversity
    separately for insights with subspace conditions only.
    
    Args:
        insights_a: Insights from system A
        insights_b: Insights from system B
        df_raw: Raw dataframe
        df_cleaned: Cleaned dataframe
        csv_path: Path to CSV file
    
    Returns:
        Dictionary with per-system subspace metrics and counts
    """
    from .faithfulness import compute_faithfulness
    from .significance import compute_significance
    from .novelty import compute_novelty
    from .diversity import compute_diversity

    a_sub = filter_insights_with_subspace(insights_a)
    b_sub = filter_insights_with_subspace(insights_b)

    def _eval(sub_insights, other_sub_insights, label):
        result = {
            'total_with_subspace': len(sub_insights),
            'total_original': len(sub_insights),
        }
        if len(sub_insights) == 0:
            result.update({
                'faithfulness': None,
                'significance': None,
                'novelty': None,
                'diversity': None,
            })
            return result
        result['faithfulness'] = compute_faithfulness(sub_insights, df_raw, df_cleaned, csv_path)
        result['significance'] = compute_significance(sub_insights, df_cleaned, csv_path)
        result['novelty'] = compute_novelty(sub_insights, other_sub_insights)
        result['diversity'] = compute_diversity(sub_insights)
        return result

    return {
        'system_a': _eval(a_sub, b_sub, 'system_a'),
        'system_b': _eval(b_sub, a_sub, 'system_b'),
    }


def compute_subspace_count(
    insights: List[Dict]
) -> Dict[str, Any]:
    """
    Compute subspace count of insights, grouped by pattern.
    
    Subspace refers to the condition/filter criteria (e.g., column=value pairs).
    
    Args:
        insights: List of insight dictionaries
        
    Returns:
        Dictionary with subspace count metrics
    """
    if len(insights) == 0:
        return {
            'total_subspaces': 0,
            'total_insights': 0,
            'insights_with_subspace': 0,
            'insights_without_subspace': 0,
            'subspaces_by_pattern': {},
            'pattern_distribution': {}
        }
    
    try:
        total_subspaces = 0
        insights_with_subspace = 0
        insights_without_subspace = 0
        subspaces_by_pattern = defaultdict(int)
        pattern_distribution = Counter()
        
        for ins in insights:
            insight_data = ins.get('insight', ins)
            pattern = insight_data.get('pattern', 'Unknown')
            subspace = insight_data.get('subspace', [])
            
            # Count pattern distribution
            pattern_distribution[pattern] += 1
            
            # Count subspaces (conditions)
            if subspace:
                insights_with_subspace += 1
                subspace_count = len(subspace)
                total_subspaces += subspace_count
                subspaces_by_pattern[pattern] += subspace_count
            else:
                insights_without_subspace += 1
        
        return {
            'total_subspaces': total_subspaces,
            'total_insights': len(insights),
            'insights_with_subspace': insights_with_subspace,
            'insights_without_subspace': insights_without_subspace,
            'subspaces_by_pattern': dict(subspaces_by_pattern),
            'pattern_distribution': dict(pattern_distribution)
        }
    except Exception as e:
        print(f"Subspace count computation failed: {e}")
        return {
            'total_subspaces': 0,
            'total_insights': len(insights),
            'insights_with_subspace': 0,
            'insights_without_subspace': 0,
            'subspaces_by_pattern': {},
            'pattern_distribution': {},
            'error': str(e)
        }
