"""
Metric computation functions for QUIS vs Baseline evaluation.

Based on EVALUATION_METRICS.md specification.
"""

import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from quis.isgen.models import Insight, Subspace, TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE
from quis.isgen.views import parse_measure


# Pattern definitions
PATTERNS = [TREND, OUTSTANDING_VALUE, ATTRIBUTION, DISTRIBUTION_DIFFERENCE]


def normalize_score(raw_score: float, pattern: str) -> float:
    """
    Normalize raw insight score to [0, 1] based on each pattern's natural range.
    
    Score ranges by pattern:
      - Trend:       1 - p_value(MK)    → [0, 1]   → already normalized
      - Attribution:  max(v)/sum(v)      → [0, 1]   → already normalized
      - Dist. Diff.:  JSD(p, q)          → [0, ~0.83] → already ~[0, 1]
      - Outstanding:  vmax1/vmax2        → [1, ∞)   → needs normalization
    
    For Outstanding Value, use:  1 - (1 / raw_score)
      This is equivalent to (vmax1 - vmax2) / vmax1,
      i.e. how much the top value exceeds the second-largest relative to itself.
      - raw=1 → 0  (no outstanding value)
      - raw=2 → 0.5
      - raw=10 → 0.9
      - raw→∞ → 1
    """
    if pattern == OUTSTANDING_VALUE:
        if raw_score <= 1.0:
            return 0.0
        return 1.0 - (1.0 / raw_score)
    # Trend, Attribution, Distribution Difference: already in [0, 1]
    return min(max(raw_score, 0.0), 1.0)


@dataclass
class InsightCard:
    """InsightCard model for evaluation"""
    question: str
    reason: str
    breakdown: str
    measure: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InsightCard':
        return cls(
            question=data.get('question', ''),
            reason=data.get('reason', ''),
            breakdown=data.get('breakdown', ''),
            measure=data.get('measure', '')
        )


def load_insights_from_summary(summary_path: str) -> Tuple[List[InsightCard], List[Dict]]:
    """
    Load insights from insights_summary.json format.
    
    Returns:
        (insight_cards, insights_data)
    """
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    cards = []
    insights_data = []
    
    for entry in summary:
        # Extract InsightCard
        card = InsightCard(
            question=entry.get('question', ''),
            reason=entry['insight'].get('reason', ''),
            breakdown=entry['insight'].get('breakdown', ''),
            measure=entry['insight'].get('measure', '')
        )
        cards.append(card)
        
        # Extract insight data
        insights_data.append(entry['insight'])
    
    return cards, insights_data


# ============================================================================
# 1. INSIGHT YIELD
# ============================================================================

def compute_yield(insights: List[Dict], cards: List[InsightCard]) -> float:
    """
    Compute insight yield: |I| / |Q|
    
    Args:
        insights: List of insights (already filtered by threshold)
        cards: List of insight cards
    
    Returns:
        Yield ratio (0-1, higher is better)
    """
    if len(cards) == 0:
        return 0.0
    return len(insights) / len(cards)


# ============================================================================
# 2. AVERAGE INSIGHT SCORE
# ============================================================================

def compute_avg_score(insights: List[Dict]) -> Dict[str, float]:
    """
    Compute average ISGEN scores (raw and normalized to [0,1]).
    
    Raw scores have different scales per pattern type (OV can be >>1).
    Normalized scores map all patterns to [0,1] for fair comparison:
      - OV: 1 - (1/raw)  i.e. (vmax1-vmax2)/vmax1
      - Others: already in [0,1]
    
    Returns:
        Dictionary with raw and normalized avg/top10/min/max scores
    """
    if len(insights) == 0:
        return {
            'avg_score': 0.0,
            'top10_score': 0.0,
            'min_score': 0.0,
            'max_score': 0.0,
            'avg_score_normalized': 0.0,
            'top10_score_normalized': 0.0,
            'min_score_normalized': 0.0,
            'max_score_normalized': 0.0
        }
    
    # Raw scores
    scores = [ins['score'] for ins in insights]
    avg_score = sum(scores) / len(scores)
    top_scores = sorted(scores, reverse=True)[:10]
    top10_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
    
    # Normalized scores [0, 1]
    norm_scores = [normalize_score(ins['score'], ins['pattern']) for ins in insights]
    avg_norm = sum(norm_scores) / len(norm_scores)
    top_norm = sorted(norm_scores, reverse=True)[:10]
    top10_norm = sum(top_norm) / len(top_norm) if top_norm else 0.0
    
    return {
        'avg_score': avg_score,
        'top10_score': top10_score,
        'min_score': min(scores),
        'max_score': max(scores),
        'avg_score_normalized': avg_norm,
        'top10_score_normalized': top10_norm,
        'min_score_normalized': min(norm_scores),
        'max_score_normalized': max(norm_scores)
    }


# ============================================================================
# 3. REDUNDANCY RATE
# ============================================================================

def compute_redundancy(insights: List[Dict]) -> Dict[str, Any]:
    """
    Compute redundancy rate based on (pattern, B, M, S) uniqueness.
    
    Returns:
        Dictionary with redundancy, unique_count, total_count, duplicate_count
    """
    if len(insights) == 0:
        return {
            'redundancy': 0.0,
            'unique_count': 0,
            'total_count': 0,
            'duplicate_count': 0
        }
    
    # Create keys
    keys = set()
    for ins in insights:
        subspace_tuple = tuple(tuple(f) for f in ins.get('subspace', []))
        key = (
            ins['pattern'],
            ins['breakdown'],
            ins['measure'],
            subspace_tuple
        )
        keys.add(key)
    
    redundancy = 1.0 - (len(keys) / len(insights))
    
    return {
        'redundancy': redundancy,
        'unique_count': len(keys),
        'total_count': len(insights),
        'duplicate_count': len(insights) - len(keys)
    }


# ============================================================================
# 4. SCHEMA COVERAGE
# ============================================================================

def compute_schema_coverage(insights: List[Dict], 
                           all_columns: List[str]) -> Dict[str, Any]:
    """
    Compute schema coverage: |C_I| / |C|
    
    Args:
        insights: List of insights
        all_columns: All column names in dataset
    
    Returns:
        Coverage metrics
    """
    used_columns = set()
    
    for ins in insights:
        # Breakdown column
        if ins.get('breakdown'):
            used_columns.add(ins['breakdown'])
        
        # Measure column (parse from "AGG(column)")
        measure = ins.get('measure', '')
        try:
            agg, col = parse_measure(measure)
            if col and col != "*":
                used_columns.add(col)
        except:
            pass
        
        # Subspace columns
        for col, val in ins.get('subspace', []):
            used_columns.add(col)
    
    coverage = len(used_columns) / len(all_columns) if all_columns else 0.0
    
    return {
        'coverage': coverage,
        'used_columns': sorted(used_columns),
        'unused_columns': sorted(set(all_columns) - used_columns),
        'used_count': len(used_columns),
        'total_count': len(all_columns)
    }


# ============================================================================
# 5. PATTERN COVERAGE
# ============================================================================

def compute_pattern_coverage(insights: List[Dict]) -> Dict[str, Any]:
    """
    Compute pattern coverage: |P_I| / |P|
    
    Returns:
        Pattern distribution and coverage
    """
    pattern_counts = {}
    for ins in insights:
        pattern = ins['pattern']
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    # Normalize pattern names
    pattern_set = set(pattern_counts.keys())
    all_patterns_set = set(PATTERNS)
    
    coverage = len(pattern_set) / len(all_patterns_set)
    
    return {
        'coverage': coverage,
        'pattern_counts': pattern_counts,
        'patterns_found': sorted(pattern_counts.keys()),
        'patterns_missing': sorted(all_patterns_set - pattern_set)
    }


# ============================================================================
# 6. SUBSPACE EXPLORATION
# ============================================================================

def compute_subspace_metrics(insights: List[Dict]) -> Dict[str, Any]:
    """
    Compute subspace exploration metrics.
    
    Returns:
        Subspace depth and coverage metrics
    """
    if len(insights) == 0:
        return {
            'avg_depth': 0.0,
            'max_depth': 0,
            'subspace_rate': 0.0,
            'unique_subspaces': 0,
            'depth_distribution': {
                'depth_0': 0,
                'depth_1': 0,
                'depth_2+': 0
            }
        }
    
    depths = [len(ins.get('subspace', [])) for ins in insights]
    subspaces = set()
    
    for ins in insights:
        subspace = ins.get('subspace', [])
        if len(subspace) > 0:
            subspaces.add(tuple(sorted(tuple(f) for f in subspace)))
    
    with_subspace = sum(1 for d in depths if d > 0)
    
    return {
        'avg_depth': sum(depths) / len(depths),
        'max_depth': max(depths) if depths else 0,
        'subspace_rate': with_subspace / len(insights),
        'unique_subspaces': len(subspaces),
        'depth_distribution': {
            'depth_0': sum(1 for d in depths if d == 0),
            'depth_1': sum(1 for d in depths if d == 1),
            'depth_2+': sum(1 for d in depths if d >= 2)
        }
    }


# ============================================================================
# 7. QUESTION DIVERSITY
# ============================================================================

def compute_question_diversity(cards: List[InsightCard]) -> Dict[str, float]:
    """
    Compute question diversity using sentence embeddings.
    
    Returns:
        Diversity score (0-1, higher is better)
    """
    if len(cards) < 2:
        return {
            'diversity': 1.0,
            'avg_similarity': 0.0,
            'num_questions': len(cards)
        }
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Extract questions
        questions = [card.question for card in cards]
        
        # Embed using sentence-transformers
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(questions)
        
        # Compute pairwise cosine similarity
        sim_matrix = cosine_similarity(embeddings)
        
        # Average similarity (excluding diagonal)
        n = len(questions)
        total_sim = (sim_matrix.sum() - n) / (n * (n - 1))
        
        diversity = 1.0 - total_sim
        
        return {
            'diversity': diversity,
            'avg_similarity': total_sim,
            'num_questions': n
        }
    except Exception as e:
        print(f"⚠️  Question diversity computation failed: {e}")
        return {
            'diversity': 0.0,
            'avg_similarity': 0.0,
            'num_questions': len(cards),
            'error': str(e)
        }


# ============================================================================
# 8. FAITHFULNESS (Hallucination Detection)
# ============================================================================

def _clean_dataframe_for_faithfulness(df: pd.DataFrame, csv_path: str = None) -> pd.DataFrame:
    """
    Clean dataframe using QUIS's exact cleaning logic (from run_isgen.py lines 71-82).
    This ensures faithfulness metric compares apples-to-apples.
    """
    import pandas as pd
    df = df.copy()
    
    # Detect separator from CSV file (same as QUIS)
    sep = ","
    if csv_path:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
            sep = ";" if first_line.count(";") > first_line.count(",") else ","
        except:
            pass
    
    # Clean currency ($), percentage (%), and European number formatting so columns become numeric
    for col in df.columns:
        # Check for object, str, or StringDtype
        dtype_str = str(df[col].dtype).lower()
        is_string_col = df[col].dtype == object or dtype_str in ['str', 'string'] or 'string' in dtype_str
        if is_string_col:
            sample = df[col].dropna().head(20).astype(str).str.strip()
            # Detect columns that look numeric: digits with optional $, %, dots, commas
            numeric_like = sample.str.match(r"^\$?\s*[\d.,]+\s*%?$")
            if numeric_like.sum() >= len(sample) * 0.8:
                cleaned = df[col].astype(str).str.replace(r"[$%]", "", regex=True).str.strip()
                if sep == ";":
                    # EU format: dot=thousands, comma=decimal
                    cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
                else:
                    # US format: comma=thousands, dot=decimal
                    cleaned = cleaned.str.replace(",", "", regex=False)
                converted = pd.to_numeric(cleaned, errors="coerce")
                if converted.notna().sum() >= len(df) * 0.5:
                    df[col] = converted
    
    return df


import re

def _clean_insight_values(value: Any, sep: str = ",") -> Any:
    """
    Clean insight view labels and subspace values using same logic as data cleaning.
    This ensures fair comparison between QUIS and Baseline.
    """
    if isinstance(value, (int, float)):
        return value
    
    if not isinstance(value, str):
        return value
    
    # Clean currency ($), percentage (%), and European number formatting (same as run_isgen.py)
    cleaned = re.sub(r"[$%]", "", value.strip())
    
    if sep == ";":
        # EU format: dot=thousands, comma=decimal
        # But first check if it's already a proper decimal number
        if '.' in cleaned and ',' not in cleaned:
            # Already in decimal format, don't apply EU conversion
            try:
                return float(cleaned)
            except:
                pass
        # Apply EU format conversion
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        # US format: comma=thousands, dot=decimal
        cleaned = cleaned.replace(",", "")
    
    try:
        return float(cleaned)
    except:
        return value


def _clean_insight_for_faithfulness(insight: Dict, sep: str = ",") -> Dict:
    """
    Clean insight view labels and subspace values using same logic as data cleaning.
    """
    # Handle both QUIS format (with nested 'insight') and direct format
    if 'insight' in insight:
        # QUIS format - extract the nested insight
        insight_data = insight['insight'].copy()
    else:
        # Direct format
        insight_data = insight.copy()
    
    # Clean view_labels
    if 'view_labels' in insight_data:
        original_labels = insight_data['view_labels']
        cleaned_labels = []
        for label in original_labels:
            cleaned_label = _clean_insight_values(label, sep)
            cleaned_labels.append(cleaned_label)
        insight_data['view_labels'] = cleaned_labels
    
    # Clean subspace values
    if 'subspace' in insight_data:
        original_subspace = insight_data['subspace']
        cleaned_subspace = []
        for col, val in original_subspace:
            cleaned_val = _clean_insight_values(val, sep)
            cleaned_subspace.append([col, cleaned_val])
        insight_data['subspace'] = cleaned_subspace
    
    return insight_data


def compute_faithfulness(insights: List[Dict], df: pd.DataFrame, 
                        use_llm: bool = False, csv_path: str = None) -> Dict[str, Any]:
    """
    Compute faithfulness - whether insights are grounded in actual data.
    
    Checks for hallucinations by verifying claims against the dataset.
    Uses QUIS's exact data cleaning logic to ensure fair comparison.
    
    Args:
        insights: List of insights
        df: Original dataframe (will be cleaned internally)
        use_llm: Whether to use LLM-as-judge (requires OpenAI API)
        csv_path: Path to CSV file (for separator detection)
    
    Returns:
        Faithfulness metrics
    """
    if len(insights) == 0:
        return {
            'faithfulness': 1.0,
            'verified_count': 0,
            'total_count': 0,
            'hallucination_count': 0
        }
    
    # Clean dataframe using QUIS's logic
    df_clean = _clean_dataframe_for_faithfulness(df, csv_path)
    
    # Detect separator for insight cleaning (same as data cleaning)
    sep = ","
    if csv_path:
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
            sep = ";" if first_line.count(";") > first_line.count(",") else ","
        except:
            pass
    
    verified_count = 0
    hallucination_count = 0
    total_checked = 0
    
    for ins in insights:
        try:
            # Clean insight values using same logic as data cleaning
            cleaned_insight = _clean_insight_for_faithfulness(ins, sep)
            
            # Check 1: Breakdown column exists
            breakdown = cleaned_insight.get('breakdown', '')
            if breakdown and breakdown not in df_clean.columns:
                hallucination_count += 1
                total_checked += 1
                continue
            
            # Check 2: Measure column exists
            measure = cleaned_insight.get('measure', '')
            try:
                agg, col = parse_measure(measure)
                if col and col != "*" and col not in df_clean.columns:
                    hallucination_count += 1
                    total_checked += 1
                    continue
            except:
                pass
            
            # Check 3: Subspace columns exist and values are valid
            subspace = cleaned_insight.get('subspace', [])
            subspace_valid = True
            for col, val in subspace:
                if col not in df_clean.columns:
                    hallucination_count += 1
                    total_checked += 1
                    subspace_valid = False
                    break
                
                # Check if value exists in cleaned data
                actual_values = df_clean[col].unique()
                
                # Direct comparison (data is already cleaned)
                found = False
                for av in actual_values:
                    # Try numeric comparison first (handles all numeric types)
                    try:
                        av_num = float(av) if not isinstance(av, (int, float)) else av
                        val_num = float(val) if not isinstance(val, (int, float)) else val
                        if abs(av_num - val_num) < 0.01:
                            found = True
                            break
                    except (ValueError, TypeError):
                        # Not numeric, try string comparison
                        if str(av) == str(val):
                            found = True
                            break
                
                if not found:
                    hallucination_count += 1
                    total_checked += 1
                    subspace_valid = False
                    break
            
            if not subspace_valid:
                continue
            
            # Check 4: View labels match actual data
            if breakdown and breakdown in df_clean.columns:
                view_labels = cleaned_insight.get('view_labels', [])
                actual_categories = df_clean[breakdown].unique().tolist()
                
                # Check if all view_labels exist in actual data
                if view_labels:
                    all_valid = True
                    for label in view_labels:
                        found = False
                        
                        for av in actual_categories:
                            # Try numeric comparison first (handles all numeric types)
                            try:
                                av_num = float(av) if not isinstance(av, (int, float)) else av
                                label_num = float(label) if not isinstance(label, (int, float)) else label
                                if abs(av_num - label_num) < 0.01:
                                    found = True
                                    break
                            except (ValueError, TypeError):
                                # Not numeric, try string comparison
                                if str(av) == str(label):
                                    found = True
                                    break
                        
                        if not found:
                            all_valid = False
                            break
                    
                    if all_valid:
                        verified_count += 1
                    else:
                        hallucination_count += 1
                    total_checked += 1
                else:
                    verified_count += 1
                    total_checked += 1
            else:
                verified_count += 1
                total_checked += 1
        except Exception as e:
            print(f"Error processing insight: {e}")
            hallucination_count += 1
            total_checked += 1
            continue
    
    faithfulness = verified_count / total_checked if total_checked > 0 else 1.0
    
    return {
        'faithfulness': faithfulness,
        'verified_count': verified_count,
        'total_count': total_checked,
        'hallucination_count': hallucination_count,
        'hallucination_rate': hallucination_count / total_checked if total_checked > 0 else 0.0
    }


# ============================================================================
# 9. INSIGHT SIGNIFICANCE (Z-Score)
# ============================================================================

def compute_insight_significance(insights: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute insight significance using Z-Score.
    
    Measures whether insights are statistically significant or just random noise.
    
    Returns:
        Significance metrics including avg_zscore and significant_count
    """
    if len(insights) == 0:
        return {
            'avg_zscore': 0.0,
            'significant_count': 0,
            'significant_rate': 0.0,
            'max_zscore': 0.0
        }
    
    try:
        from scipy import stats
        
        zscores = []
        significant_count = 0
        
        for ins in insights:
            try:
                # Get measure column
                measure = ins.get('measure', '')
                agg, col = parse_measure(measure)
                
                if not col or col == "*":
                    continue
                
                # Get view values (aggregated values in insight)
                view_values = ins.get('view_values', [])
                if not view_values or len(view_values) < 2:
                    continue
                
                # Compute Z-score: compare max view_value with distribution of view_values
                # (not with raw data, since view_values are already aggregated)
                if len(view_values) >= 3:  # Need at least 3 values for meaningful stats
                    view_mean = np.mean(view_values)
                    view_std = np.std(view_values)
                    max_val = max(view_values)
                    
                    if view_std > 0:
                        zscore = abs((max_val - view_mean) / view_std)
                        zscores.append(zscore)
                        
                        # Significant if |Z| > 1.96 (p < 0.05)
                        if zscore > 1.96:
                            significant_count += 1
            except Exception as e:
                continue
        
        if not zscores:
            return {
                'avg_zscore': 0.0,
                'significant_count': 0,
                'significant_rate': 0.0,
                'max_zscore': 0.0
            }
        
        return {
            'avg_zscore': np.mean(zscores),
            'significant_count': significant_count,
            'significant_rate': significant_count / len(insights),
            'max_zscore': max(zscores),
            'total_evaluated': len(zscores)
        }
    except Exception as e:
        print(f"⚠️  Significance computation failed: {e}")
        return {
            'avg_zscore': 0.0,
            'significant_count': 0,
            'significant_rate': 0.0,
            'max_zscore': 0.0,
            'error': str(e)
        }


# ============================================================================
# MAIN EVALUATION FUNCTION
# ============================================================================

def evaluate_system(system_name: str,
                   summary_path: str,
                   df: pd.DataFrame,
                   csv_path: str = None) -> Dict[str, Any]:
    """
    Complete evaluation of a system.
    
    Args:
        system_name: "QUIS" or "Baseline"
        summary_path: Path to insights_summary.json
        df: Original dataframe
    
    Returns:
        Dictionary with all metrics
    """
    print(f"\n{'='*70}")
    print(f"Evaluating {system_name}")
    print(f"{'='*70}\n")
    
    # Load data
    cards, insights_data = load_insights_from_summary(summary_path)
    
    print(f"📊 Loaded:")
    print(f"  - {len(cards)} insight cards")
    print(f"  - {len(insights_data)} insights")
    
    # Compute all metrics
    print(f"\n🔍 Computing metrics...")
    
    results = {
        'system': system_name,
        'num_cards': len(cards),
        'num_insights': len(insights_data),
        
        # Core metrics
        'yield': compute_yield(insights_data, cards),
        'avg_score': compute_avg_score(insights_data),
        'redundancy': compute_redundancy(insights_data),
        
        # Coverage metrics
        'schema_coverage': compute_schema_coverage(insights_data, df.columns.tolist()),
        'pattern_coverage': compute_pattern_coverage(insights_data),
        'subspace_metrics': compute_subspace_metrics(insights_data),
        
        # Quality metrics
        'question_diversity': compute_question_diversity(cards),
        'insight_significance': compute_insight_significance(insights_data, df),
        'faithfulness': compute_faithfulness(insights_data, df, csv_path=csv_path)
    }
    
    print(f"✅ Metrics computed successfully\n")
    
    return results
