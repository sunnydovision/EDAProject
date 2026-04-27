"""
Time to insight metric computation.

Measures how long each system takes to generate insights.
"""

import json
import os
from typing import Dict, Any


def compute_time_to_insight(
    timing_file: str,
    system: str = "baseline"
) -> Dict[str, Any]:
    """
    Compute time to insight metrics.
    
    Args:
        timing_file: Path to timing.json file
        system: System name (baseline or quis)
        
    Returns:
        Dictionary with timing metrics
    """
    if not os.path.exists(timing_file):
        return {
            'total_time_seconds': None,
            'insights_generated': None,
            'time_per_insight_seconds': None,
            'throughput_insights_per_second': None
        }
    
    # Load timing data
    with open(timing_file, 'r', encoding='utf-8') as f:
        timing_data = json.load(f)
    
    # Extract system-specific data
    if system.lower() == 'baseline':
        time_seconds = timing_data['baseline']['total_time_seconds']
        insights_generated = timing_data['baseline']['insights_generated']
        throughput = timing_data['baseline']['throughput_insights_per_second']
    elif system.lower() == 'quis':
        time_seconds = timing_data['quis']['total_time_seconds']
        insights_generated = timing_data['quis']['insights_generated']
        throughput = insights_generated / time_seconds if time_seconds and insights_generated else 0
    else:
        raise ValueError(f"Unknown system: {system}")
    
    # Compute time per insight
    time_per_insight = time_seconds / insights_generated if insights_generated > 0 else 0
    
    return {
        'total_time_seconds': time_seconds,
        'insights_generated': insights_generated,
        'time_per_insight_seconds': time_per_insight,
        'throughput_insights_per_second': throughput
    }
