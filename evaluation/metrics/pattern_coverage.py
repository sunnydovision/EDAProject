"""
Pattern Coverage and Structural Validity Rate (SVR) metrics.

- Pattern Coverage: # patterns with ≥1 structurally valid insight / 4 total patterns
- Structural Validity Rate: % insights with breakdown type valid for their pattern

Validity rules (from paper):
  OUTSTANDING_VALUE     — no breakdown constraint
  TREND                 — breakdown must be Temporal
  ATTRIBUTION           — breakdown must be Categorical or ID
  DISTRIBUTION_DIFFERENCE — breakdown must be Categorical or ID
"""

from __future__ import annotations

import json
import pandas as pd

ALL_PATTERNS = ['TREND', 'OUTSTANDING_VALUE', 'ATTRIBUTION', 'DISTRIBUTION_DIFFERENCE']

_NEEDS_CATEGORICAL = {'ATTRIBUTION', 'DISTRIBUTION_DIFFERENCE'}
_NEEDS_TEMPORAL = {'TREND'}

# Pattern name normalization: IsGen uses spaces, we normalize to underscores
_NORMALIZE = {
    'Outstanding Value': 'OUTSTANDING_VALUE',
    'Trend': 'TREND',
    'Attribution': 'ATTRIBUTION',
    'Distribution Difference': 'DISTRIBUTION_DIFFERENCE',
}


def _normalize_pattern(pattern: str) -> str:
    p = pattern.strip()
    return _NORMALIZE.get(p, p.upper().replace(' ', '_'))


def _load_col_classes(profile_path: str | None) -> dict[str, str]:
    if not profile_path:
        return {}
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        return {col: info.get('data_type_class', '') for col, info in profile.get('columns', {}).items()}
    except Exception:
        return {}


def _is_temporal_column(col_name: str, series: pd.Series, col_classes: dict) -> bool:
    if col_classes:
        cls = col_classes.get(col_name, '')
        if cls == 'Temporal':
            return True
        if cls:
            return False
    # Fallback: try datetime parse
    try:
        parsed = pd.to_datetime(series, errors='coerce')
        return int(parsed.notna().sum()) >= 3
    except Exception:
        return False


def _is_categorical_column(col_name: str, series: pd.Series, col_classes: dict) -> bool:
    if col_classes:
        cls = col_classes.get(col_name, '')
        if cls in {'Categorical', 'ID'}:
            return True
        if cls:
            return False
    return series.dtype == object or str(series.dtype) == 'string'


def is_valid_for_pattern(pattern: str, breakdown: str, df: pd.DataFrame, col_classes: dict) -> bool:
    p = _normalize_pattern(pattern)
    if breakdown not in df.columns:
        return False
    series = df[breakdown]
    if p == 'OUTSTANDING_VALUE':
        return True
    elif p in _NEEDS_TEMPORAL:
        return _is_temporal_column(breakdown, series, col_classes)
    elif p in _NEEDS_CATEGORICAL:
        return _is_categorical_column(breakdown, series, col_classes)
    return True


def compute_structural_validity(
    insights: list,
    df_cleaned: pd.DataFrame,
    profile_path: str | None = None,
) -> dict:
    """
    Compute Structural Validity Rate (SVR).
    Returns: {
        structural_validity_rate, valid_count, invalid_count, total_count,
        by_pattern: {pattern: {valid_count, total_count, valid_rate}}
    }
    """
    col_classes = _load_col_classes(profile_path)
    by_pattern: dict[str, dict] = {p: {'valid': 0, 'total': 0} for p in ALL_PATTERNS}
    valid_total = 0
    total = 0

    for item in insights:
        ins = item.get('insight', {}) if isinstance(item, dict) and 'insight' in item else item
        breakdown = ins.get('breakdown', '')
        pattern = ins.get('pattern', '')
        if not breakdown or not pattern:
            continue
        p_norm = _normalize_pattern(pattern)
        if p_norm not in by_pattern:
            by_pattern[p_norm] = {'valid': 0, 'total': 0}
        valid = is_valid_for_pattern(pattern, breakdown, df_cleaned, col_classes)
        by_pattern[p_norm]['total'] += 1
        if valid:
            by_pattern[p_norm]['valid'] += 1
            valid_total += 1
        total += 1

    svr = valid_total / total if total > 0 else 0.0
    by_pattern_out = {}
    for p in ALL_PATTERNS:
        d = by_pattern.get(p, {'valid': 0, 'total': 0})
        by_pattern_out[p] = {
            'valid_count': d['valid'],
            'total_count': d['total'],
            'valid_rate': d['valid'] / d['total'] if d['total'] > 0 else None,
        }

    return {
        'structural_validity_rate': svr,
        'valid_count': valid_total,
        'invalid_count': total - valid_total,
        'total_count': total,
        'by_pattern': by_pattern_out,
    }


def compute_pattern_coverage(
    insights: list,
    df_cleaned: pd.DataFrame,
    profile_path: str | None = None,
) -> dict:
    """
    Compute Pattern Coverage: # patterns with ≥1 structurally valid insight / 4.
    Returns: {
        pattern_coverage, covered_count, total_patterns,
        covered_patterns, uncovered_patterns, by_pattern
    }
    """
    svr = compute_structural_validity(insights, df_cleaned, profile_path)
    covered = [p for p in ALL_PATTERNS if svr['by_pattern'][p]['valid_count'] > 0]
    uncovered = [p for p in ALL_PATTERNS if svr['by_pattern'][p]['valid_count'] == 0]
    return {
        'pattern_coverage': len(covered) / len(ALL_PATTERNS),
        'covered_count': len(covered),
        'total_patterns': len(ALL_PATTERNS),
        'covered_patterns': covered,
        'uncovered_patterns': uncovered,
        'by_pattern': svr['by_pattern'],
    }
