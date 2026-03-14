"""
ISGEN-based scoring functions for insights.

Based on the ISGEN paper scoring methodology:
- TREND: Mann-Kendall test (1 - p_value), threshold 0.95
- OUTSTANDING_VALUE: max/second_max ratio, threshold 1.4
- ATTRIBUTION: max/sum ratio, threshold 0.5
- QUALITY: For other insight types
"""

from typing import List, Dict, Any


def score_trend(values: List[float]) -> float:
    """
    ISGEN TREND scoring: 1 - p_value from Mann-Kendall test.
    
    Args:
        values: List of numerical values representing a trend
        
    Returns:
        Score between 0 and 1 (higher = stronger trend)
    """
    if len(values) < 3:
        return 0.0
    try:
        import pymannkendall as mk
        result = mk.original_test(values)
        return 1.0 - result.p if result.p is not None else 0.0
    except:
        return 0.0


def score_outstanding_value(values: List[float]) -> float:
    """
    ISGEN OUTSTANDING_VALUE scoring: ratio of max to second max.
    
    Args:
        values: List of numerical values
        
    Returns:
        Ratio (>1.4 indicates outstanding value)
    """
    if len(values) < 2:
        return 0.0
    abs_vals = sorted([abs(v) for v in values if v != 0], reverse=True)
    if len(abs_vals) < 2:
        return 0.0
    if abs_vals[1] == 0:
        return float(abs_vals[0]) if abs_vals[0] > 0 else 0.0
    return abs_vals[0] / abs_vals[1]


def score_attribution(values: List[float]) -> float:
    """
    ISGEN ATTRIBUTION scoring: max/sum ratio.
    
    Args:
        values: List of numerical values (e.g., category counts)
        
    Returns:
        Ratio between 0 and 1 (>0.5 indicates dominant category)
    """
    if not values:
        return 0.0
    s = sum(values)
    if s == 0:
        return 0.0
    return max(values) / s


def score_quality(insight_data: Dict[str, Any]) -> float:
    """
    Quality score for insights without specific ISGEN pattern.
    
    Args:
        insight_data: Insight dictionary with description, variables, evidence
        
    Returns:
        Quality score between 0 and 1
    """
    quality = 0.0
    
    # Has description (0.3)
    if insight_data.get('description') and len(insight_data['description']) > 50:
        quality += 0.3
    
    # Has variables (0.3)
    if insight_data.get('variables') and len(insight_data['variables']) > 0:
        quality += 0.3
    
    # Has evidence with numbers (0.4)
    evidence_str = str(insight_data.get('evidence', ''))
    if any(char.isdigit() for char in evidence_str):
        quality += 0.4
    
    return quality


def score_insight(insight_data: Dict[str, Any], values: List[float]) -> Dict[str, Any]:
    """
    Score an insight using appropriate ISGEN scoring function.
    
    Args:
        insight_data: Insight dictionary with type, description, etc.
        values: Numerical values extracted from data for scoring
        
    Returns:
        Score dictionary with pattern_score, threshold, passed, overall
    """
    insight_type = insight_data.get('type', '')
    
    score = {
        'pattern_score': 0.0,
        'threshold': 0.0,
        'passed': False,
        'pattern_type': None,
        'overall': 0.0
    }
    
    # Map insight type to ISGEN pattern and calculate score
    if insight_type == 'TREND' and len(values) >= 3:
        score['pattern_type'] = 'TREND'
        score['pattern_score'] = score_trend(values)
        score['threshold'] = 0.95
        score['passed'] = score['pattern_score'] >= 0.95
        
    elif insight_type in ['OUTLIER', 'ANOMALY'] and len(values) >= 2:
        score['pattern_type'] = 'OUTSTANDING_VALUE'
        score['pattern_score'] = score_outstanding_value(values)
        score['threshold'] = 1.4
        score['passed'] = score['pattern_score'] >= 1.4
        
    elif insight_type == 'COMPARISON' and len(values) >= 2:
        score['pattern_type'] = 'ATTRIBUTION'
        score['pattern_score'] = score_attribution(values)
        score['threshold'] = 0.5
        score['passed'] = score['pattern_score'] >= 0.5
        
    elif insight_type in ['DISTRIBUTION', 'PATTERN', 'CORRELATION']:
        score['pattern_type'] = 'QUALITY'
        score['pattern_score'] = score_quality(insight_data)
        score['threshold'] = 0.6
        score['passed'] = score['pattern_score'] >= 0.6
    
    score['overall'] = score['pattern_score']
    
    return score
