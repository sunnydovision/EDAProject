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
    
    # Extract data (flat format for both baseline and quis)
    time_seconds = timing_data.get('total_time')
    insights_generated = timing_data.get('insights_generated')
    throughput = timing_data.get('throughput')
    
    # Compute throughput if not provided
    if throughput is None and time_seconds and insights_generated:
        throughput = insights_generated / time_seconds
    elif throughput is None:
        throughput = 0
    
    # Compute time per insight
    time_per_insight = time_seconds / insights_generated if insights_generated and insights_generated > 0 else 0
    
    return {
        'total_time_seconds': time_seconds,
        'insights_generated': insights_generated,
        'time_per_insight_seconds': time_per_insight,
        'throughput_insights_per_second': throughput
    }
