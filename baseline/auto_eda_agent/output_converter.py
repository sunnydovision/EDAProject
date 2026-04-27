"""
Output Converter: Transform Agentic AutoEDA output to QUIS-compatible format

This module converts the baseline's custom output format to QUIS-compatible format
while preserving the 5-step EDA methodology.

Key transformations:
1. Generate InsightCards from insights (backward mapping)
2. Convert insights to (B, M, S, P) structure
3. Add view_labels and view_values
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import sys
import os

# Import QUIS views for compatibility only (not models)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from quis.isgen.views import compute_view, parse_measure
from agent import _clean_dataframe_like_ifq


class OutputConverter:
    """Convert Agentic AutoEDA output to ISGEN-compatible format"""
    
    # ISGEN pattern types (4 types from paper)
    ISGEN_PATTERN_TYPES = [
        'TREND',                    # Temporal trends
        'OUTSTANDING_VALUE',        # Outliers and anomalies
        'ATTRIBUTION',              # Correlation and attribution
        'DISTRIBUTION_DIFFERENCE'   # Distribution differences
    ]
    
    # Mapping from baseline insight_type to ISGEN pattern type
    PATTERN_MAP = {
        'TREND': 'TREND',
        'ANOMALY': 'OUTSTANDING_VALUE',
        'OUTLIER': 'OUTSTANDING_VALUE',
        'OUTLIER, ANOMALY': 'OUTSTANDING_VALUE',  # Combined type
        'CORRELATION': 'ATTRIBUTION',
        'DISTRIBUTION': 'DISTRIBUTION_DIFFERENCE',
        'COMPARISON': 'DISTRIBUTION_DIFFERENCE',  # Fixed: should be DISTRIBUTION_DIFFERENCE
        'DISTRIBUTION, COMPARISON': 'DISTRIBUTION_DIFFERENCE',  # Combined type
        'PATTERN': 'TREND'  # Generic patterns mapped to trend
    }
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize converter.
        
        Args:
            df: Original dataframe used in analysis
        """
        self.df = df
    
    def convert_insights(self, insights_path: str, output_dir: str):
        """
        Convert baseline insights.json to QUIS-compatible format.
        
        Args:
            insights_path: Path to baseline insights.json
            output_dir: Output directory for converted files
        
        Generates:
            - insight_cards.json: InsightCards with (Q, R, B, M)
            - insights_summary.json: QUIS format with question, explanation, plot_path, nested insight
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Load baseline insights
        with open(insights_path, 'r', encoding='utf-8') as f:
            baseline_insights = json.load(f)
        
        print(f"\n🔄 Converting {len(baseline_insights)} insights to QUIS format...")
        
        # Convert each insight
        insight_cards = []
        insights_summary = []
        
        for idx, baseline_insight in enumerate(baseline_insights):
            print(f"  {idx+1}/{len(baseline_insights)}: {baseline_insight.get('title', 'Untitled')[:60]}...")
            
            try:
                # Extract breakdown and measure from variables
                breakdown, measure = self._extract_breakdown_measure(baseline_insight)
                
                if not breakdown or not measure:
                    print(f"    ⚠️  Skipped: Cannot determine breakdown/measure")
                    continue
                
                # Generate InsightCard (backward mapping)
                card = self._generate_insight_card(baseline_insight, breakdown, measure)
                insight_cards.append(card)
                
                # Convert to QUIS Insight format
                ifq_insight = self._convert_to_ifq_insight(baseline_insight, breakdown, measure, idx)
                
                # Use existing chart path from baseline (already in QUIS format)
                chart_path = baseline_insight.get('chart_path', '')
                
                # Create insights_summary entry (QUIS format)
                summary_entry = {
                    'question': ifq_insight['insight']['question'],
                    'explanation': self._generate_explanation(ifq_insight['insight']),
                    'plot_path': chart_path,
                    'insight': ifq_insight['insight']
                }
                insights_summary.append(summary_entry)
                
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
                continue
        
        # Save InsightCards
        cards_path = f"{output_dir}/insight_cards.json"
        with open(cards_path, 'w', encoding='utf-8') as f:
            json.dump(insight_cards, f, indent=2, ensure_ascii=False)
        
        # Save Insights Summary (QUIS format)
        summary_path = f"{output_dir}/insights_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(insights_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Conversion complete!")
        print(f"  📄 InsightCards: {cards_path} ({len(insight_cards)} cards)")
        print(f"  📄 Insights Summary: {summary_path} ({len(insights_summary)} insights)")
        
        return {
            'insight_cards': insight_cards,
            'insights_summary': insights_summary
        }
    
    def _extract_breakdown_measure(self, baseline_insight: Dict) -> Tuple[str, str]:
        """
        Extract breakdown and measure from baseline insight.
        
        Strategy:
        1. For TREND/CORRELATION: breakdown = first var, measure = AGG(second var)
        2. For DISTRIBUTION/COMPARISON: breakdown = categorical var, measure = COUNT(*) or AGG(numerical)
        3. For OUTLIER/ANOMALY: breakdown = context var, measure = AGG(target var)
        """
        variables = baseline_insight.get('variables', [])
        insight_type = baseline_insight.get('insight_type', '')
        
        if not variables:
            return None, None
        
        # Filter to valid columns
        valid_vars = [v for v in variables if v in self.df.columns]
        if not valid_vars:
            return None, None
        
        # Determine breakdown and measure based on type
        if insight_type == 'TREND':
            # Trend: breakdown = time/categorical, measure = MEAN(numerical)
            breakdown = valid_vars[0]
            if len(valid_vars) > 1:
                measure_col = valid_vars[1]
                if self.df[measure_col].dtype in [np.float64, np.int64]:
                    measure = f"MEAN({measure_col})"
                else:
                    measure = "COUNT(*)"
            else:
                measure = "COUNT(*)"
        
        elif insight_type in ['OUTLIER', 'ANOMALY']:
            # Outlier: breakdown = grouping var, measure = AGG(target)
            if len(valid_vars) >= 2:
                breakdown = valid_vars[-1]  # Last var is often grouping
                measure_col = valid_vars[0]  # First var is target
                if self.df[measure_col].dtype in [np.float64, np.int64]:
                    measure = f"MEAN({measure_col})"
                else:
                    measure = "COUNT(*)"
            else:
                breakdown = valid_vars[0]
                measure = "COUNT(*)"
        
        elif insight_type == 'CORRELATION':
            # Correlation: breakdown = first var, measure = MEAN(second)
            breakdown = valid_vars[0]
            if len(valid_vars) > 1:
                measure_col = valid_vars[1]
                if self.df[measure_col].dtype in [np.float64, np.int64]:
                    measure = f"MEAN({measure_col})"
                else:
                    measure = "COUNT(*)"
            else:
                measure = "COUNT(*)"
        
        elif insight_type in ['DISTRIBUTION', 'COMPARISON']:
            # Distribution: breakdown = categorical, measure = COUNT or AGG
            categorical_vars = [v for v in valid_vars if self.df[v].dtype == 'object']
            numerical_vars = [v for v in valid_vars if self.df[v].dtype in [np.float64, np.int64]]
            
            if categorical_vars:
                breakdown = categorical_vars[0]
            else:
                breakdown = valid_vars[0]
            
            if numerical_vars:
                measure = f"MEAN({numerical_vars[0]})"
            else:
                measure = "COUNT(*)"
        
        else:
            # Default: first var as breakdown, COUNT or MEAN of second
            breakdown = valid_vars[0]
            if len(valid_vars) > 1:
                measure_col = valid_vars[1]
                if self.df[measure_col].dtype in [np.float64, np.int64]:
                    measure = f"MEAN({measure_col})"
                else:
                    measure = "COUNT(*)"
            else:
                measure = "COUNT(*)"
        
        return breakdown, measure
    
    def _generate_insight_card(self, baseline_insight: Dict, breakdown: str, measure: str) -> Dict:
        """
        Generate InsightCard from baseline insight (backward mapping).
        
        Creates a question that would have led to this insight.
        """
        insight_type = baseline_insight.get('insight_type', '')
        title = baseline_insight.get('title', '')
        description = baseline_insight.get('description', '')
        
        # Generate question based on pattern type
        question = self._generate_question(insight_type, breakdown, measure, title)
        
        # Use description as reason (preserve full content)
        reason = description
        
        return {
            'question': question,
            'reason': reason,
            'breakdown': breakdown,
            'measure': measure
        }
    
    def _generate_question(self, insight_type: str, breakdown: str, measure: str, title: str) -> str:
        """Generate analytical question based on insight type"""
        
        # Parse measure to get readable form
        if measure.startswith('MEAN('):
            measure_readable = measure[5:-1]
            agg = "average"
        elif measure.startswith('SUM('):
            measure_readable = measure[4:-1]
            agg = "total"
        elif measure.startswith('COUNT'):
            measure_readable = "count"
            agg = "number of"
        else:
            measure_readable = measure
            agg = "value of"
        
        # Generate question based on type
        if insight_type == 'TREND':
            return f"How does {measure_readable} change over {breakdown}?"
        
        elif insight_type in ['OUTLIER', 'ANOMALY']:
            return f"Are there any unusual values of {measure_readable} across {breakdown}?"
        
        elif insight_type == 'CORRELATION':
            return f"What is the relationship between {breakdown} and {measure_readable}?"
        
        elif insight_type == 'DISTRIBUTION':
            return f"How is {measure_readable} distributed across {breakdown}?"
        
        elif insight_type == 'COMPARISON':
            return f"How does {agg} {measure_readable} vary across {breakdown}?"
        
        elif insight_type == 'PATTERN':
            return f"What patterns exist in {measure_readable} by {breakdown}?"
        
        else:
            # Fallback: extract from title
            if title:
                return f"What insights can we find about {title.lower()}?"
            return f"How does {measure_readable} vary by {breakdown}?"
    
    def _fix_label_types(self, labels: List[str], breakdown: str) -> List[Any]:
        """
        Convert string labels back to original data types to match cleaned data.
        QUIS compute_view returns strings, but we need original types for faithfulness.
        Also handles datetime label conversion from ISO format to YYYY-MM-DD.
        """
        if breakdown not in self.df.columns:
            return labels
        
        # Get actual data type from cleaned dataframe
        sample_values = self.df[breakdown].dropna().head(10)
        
        if len(sample_values) == 0:
            return labels
        
        # Check if breakdown is datetime column
        if pd.api.types.is_datetime64_any_dtype(self.df[breakdown]):
            # Convert ISO datetime format to YYYY-MM-DD
            fixed_labels = []
            for label in labels:
                try:
                    # Handle ISO format: "2020-01-01T00:00:00" -> "2020-01-01"
                    if isinstance(label, str) and "T" in label:
                        fixed_labels.append(label.split("T")[0])
                    else:
                        fixed_labels.append(str(label))
                except:
                    fixed_labels.append(str(label))
            return fixed_labels
        
        # For non-datetime columns, keep labels as strings to match evaluation behavior
        # Evaluation converts labels to strings before comparison, so we should too
        fixed_labels = []
        for label in labels:
            fixed_labels.append(str(label))
        
        return fixed_labels

    def _convert_to_ifq_insight(self, baseline_insight: Dict, breakdown: str, measure: str, idx: int) -> Dict:
        """
        Convert baseline insight to ISGEN-compatible format.
        
        Returns dict with nested 'insight' object using ISGEN pattern types
        """
        # Map baseline insight_type to ISGEN pattern type
        baseline_type = baseline_insight.get('insight_type', 'PATTERN')
        pattern_type = self.PATTERN_MAP.get(baseline_type, 'TREND')
        
        # Validate pattern type
        if pattern_type not in self.ISGEN_PATTERN_TYPES:
            pattern_type = 'TREND'  # Default to trend
        
        # Extract score
        score_data = baseline_insight.get('score', {})
        score = float(score_data.get('overall', score_data.get('pattern_score', 0.0)))
        
        # Extract and convert subspace from baseline format to QUIS Subspace format
        # Baseline uses [["column", "value"]] (list of lists)
        # QUIS uses Subspace(filters=((col, val), ...)) (tuple of tuples)
        baseline_subspace = baseline_insight.get('subspace', [])
        if baseline_subspace:
            # Convert from [["col", "val"], ...] to ((col, val), ...)
            subspace_filters = tuple(tuple(filter_pair) for filter_pair in baseline_subspace)
            from quis.isgen.models import Subspace
            ifq_subspace = Subspace(filters=subspace_filters)
        else:
            ifq_subspace = None
        
        # Compute view (labels and values) with actual subspace
        try:
            labels, values = compute_view(self.df, breakdown, measure, ifq_subspace)
            print(f"      Computed with compute_view: {len(labels)} labels, first value: {values[0] if values else 'N/A'}")
            # Convert string labels back to original data types to match cleaned data
            labels = self._fix_label_types(labels, breakdown)
            # Remove duplicates to avoid faithfulness errors
            seen = set()
            unique_labels = []
            unique_values = []
            for label, value in zip(labels, values):
                if label not in seen:
                    seen.add(label)
                    unique_labels.append(label)
                    unique_values.append(value)
            labels, values = unique_labels, unique_values
            print(f"      After dedup: {len(labels)} labels, first value: {values[0] if values else 'N/A'}")
        except Exception as e:
            print(f"      compute_view failed: {e}, using fallback")
            import traceback
            traceback.print_exc()
            # Fallback: compute manually
            labels, values = self._compute_view_fallback(breakdown, measure)
        
        # Generate question and reason
        question = self._generate_question(baseline_type, breakdown, measure, baseline_insight.get('title', ''))
        reason = baseline_insight.get('description', '')
        
        result = {
            'insight': {
                'breakdown': breakdown,
                'measure': measure,
                'subspace': baseline_insight.get('subspace', []),  # Extract from LLM response
                'pattern': pattern_type,  # ISGEN pattern type
                'score': score,
                'question': question,
                'reason': reason,
                'view_labels': labels,
                'view_values': values
            }
        }
        
        # Debug: print first value to verify
        if values and len(values) > 0:
            print(f"      Writing to file: first value = {values[0]}")
        
        return result
    
    def _generate_explanation(self, insight: Dict) -> str:
        """
        Generate explanation text in ISGEN format.
        
        Format: "<pattern>: [subspace conditions], one category in <breakdown> has a value 
                much larger (or smaller) than the others when measuring <measure>."
        """
        pattern = insight['pattern']
        breakdown = insight['breakdown']
        measure = insight['measure']
        subspace = insight.get('subspace', [])
        
        # Build subspace description
        if subspace:
            subspace_desc = ', '.join([f"{col}={val}" for col, val in subspace])
            subspace_text = f"for {subspace_desc}, "
        else:
            subspace_text = ""
        
        # Pattern-specific explanations using ISGEN pattern types
        if pattern == 'OUTSTANDING_VALUE':
            return f"{pattern}: {subspace_text}one category in {breakdown} has a value much larger (or smaller) than the others when measuring {measure}."
        elif pattern == 'TREND':
            return f"{pattern}: {subspace_text}{measure} shows a monotonic trend across {breakdown}."
        elif pattern == 'ATTRIBUTION':
            return f"{pattern}: {subspace_text}one category in {breakdown} dominates the total {measure}."
        elif pattern == 'DISTRIBUTION_DIFFERENCE':
            return f"{pattern}: {subspace_text}the distribution of {measure} differs significantly across {breakdown}."
        else:
            return f"{pattern}: {subspace_text}interesting pattern found in {measure} by {breakdown}."
    
    def _compute_view_fallback(self, breakdown: str, measure: str) -> Tuple[List[str], List[float]]:
        """Fallback view computation if QUIS compute_view fails"""
        try:
            if measure == "COUNT(*)":
                # Count by breakdown
                counts = self.df[breakdown].value_counts()
                # Return actual values (not strings) to match cleaned data
                labels = counts.index.tolist()
                values = counts.values.tolist()
                # Remove duplicates by using dict to preserve order
                seen = set()
                unique_labels = []
                unique_values = []
                for label, value in zip(labels, values):
                    if label not in seen:
                        seen.add(label)
                        unique_labels.append(label)
                        unique_values.append(value)
                return unique_labels, unique_values
            
            # Parse measure
            if measure.startswith('MEAN('):
                col = measure[5:-1]
                agg_func = 'mean'
            elif measure.startswith('SUM('):
                col = measure[4:-1]
                agg_func = 'sum'
            elif measure.startswith('MAX('):
                col = measure[4:-1]
                agg_func = 'max'
            elif measure.startswith('MIN('):
                col = measure[4:-1]
                agg_func = 'min'
            else:
                col = measure
                agg_func = 'mean'
            
            # Group and aggregate
            grouped = self.df.groupby(breakdown)[col].agg(agg_func)
            labels = grouped.index.tolist()
            values = grouped.values.tolist()
            # Remove duplicates by using dict to preserve order
            seen = set()
            unique_labels = []
            unique_values = []
            for label, value in zip(labels, values):
                if label not in seen:
                    seen.add(label)
                    unique_labels.append(label)
                    unique_values.append(value)
            return unique_labels, unique_values
        
        except Exception as e:
            print(f"      ⚠️  View computation failed: {e}")
            return [], []


def convert_baseline_output(data_path: str, insights_path: str, output_dir: str):
    """
    Convenience function to convert baseline output.
    
    Args:
        data_path: Path to original CSV data
        insights_path: Path to baseline insights.json
        output_dir: Output directory for QUIS-compatible files
    """
    # Load data with same cleaning as baseline agent
    df = pd.read_csv(data_path, sep=None, engine='python')
    df = _clean_dataframe_like_ifq(df, data_path)
    
    # Parse datetime columns (same as evaluation data_loader)
    for col in df.columns:
        col_lower = col.lower()
        if any(date_keyword in col_lower for date_keyword in ['date', 'ngày', 'ngay', 'time']):
            if df[col].dtype == object or 'str' in str(df[col].dtype).lower():
                try:
                    df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                    if df[col].notna().sum() > 0:
                        print(f"Parsed {col} as datetime")
                except Exception:
                    pass
    
    # Convert
    converter = OutputConverter(df)
    result = converter.convert_insights(insights_path, output_dir)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert Agentic AutoEDA output to QUIS format')
    parser.add_argument('--data', type=str, required=True, help='Path to CSV data file')
    parser.add_argument('--insights', type=str, required=True, help='Path to baseline insights.json')
    parser.add_argument('--output', type=str, default='ifq_compatible_output', help='Output directory')
    
    args = parser.parse_args()
    
    convert_baseline_output(args.data, args.insights, args.output)
    
    print("\n✅ Conversion complete! Output is now QUIS-compatible.")
