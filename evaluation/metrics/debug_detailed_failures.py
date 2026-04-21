"""
Debug script to get detailed failure reasons for all failed insights
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_loader import load_and_clean_data
from significance import parse_measure, resolve_column, compute_p_value
import json

# Load data
csv_path = "../data/Adidas_cleaned.csv"
df_raw, df_cleaned = load_and_clean_data(csv_path)

# Load IFQ insights
insights_ifq_path = "../insights_summary_adidas_2.json"
with open(insights_ifq_path, 'r', encoding='utf-8') as f:
    insights_ifq = json.load(f)

# Load Baseline insights
insights_baseline_path = "../baseline/auto_eda_agent/ifq_compatible_output/insights_summary.json"
with open(insights_baseline_path, 'r', encoding='utf-8') as f:
    insights_baseline = json.load(f)

def debug_insights(insights, name):
    print(f"\n{'='*70}")
    print(f"{name} - Detailed Failure Analysis")
    print(f"{'='*70}")
    
    failures = []
    
    for i, ins in enumerate(insights):
        insight_data = ins.get('insight', ins)
        pattern = insight_data.get('pattern', '')
        measure = insight_data.get('measure', '')
        agg, col = parse_measure(measure)
        breakdown = insight_data.get('breakdown', '')
        
        # For COUNT(*), use breakdown column if available
        if not col or col == "*":
            if breakdown and breakdown in df_cleaned.columns:
                col = breakdown
            else:
                failures.append({
                    'idx': i,
                    'pattern': pattern,
                    'measure': measure,
                    'breakdown': breakdown,
                    'col': col,
                    'reason': 'COUNT(*) without valid breakdown'
                })
                continue
        
        # Resolve column names
        col_resolved = resolve_column(col, list(df_cleaned.columns)) or col
        breakdown_resolved = resolve_column(breakdown, list(df_cleaned.columns)) or breakdown if breakdown else None
        
        # Check columns
        if col_resolved not in df_cleaned.columns:
            failures.append({
                'idx': i,
                'pattern': pattern,
                'measure': measure,
                'breakdown': breakdown,
                'col': col,
                'col_resolved': col_resolved,
                'reason': f'Column not found: {col_resolved}'
            })
            continue
        
        if breakdown_resolved and breakdown_resolved not in df_cleaned.columns:
            failures.append({
                'idx': i,
                'pattern': pattern,
                'measure': measure,
                'breakdown': breakdown,
                'col': col,
                'breakdown_resolved': breakdown_resolved,
                'reason': f'Breakdown not found: {breakdown_resolved}'
            })
            continue
        
        # Compute p-value
        p_value = compute_p_value(pattern, df_cleaned, breakdown_resolved, col_resolved)
        
        if p_value is None:
            # Determine specific reason
            reason = 'Unknown'
            if pattern.upper() == 'TREND':
                if breakdown == col:
                    reason = 'TREND: breakdown equals col (invalid regression)'
                elif 'str' in str(df_cleaned[breakdown].dtype) or 'object' in str(df_cleaned[breakdown].dtype):
                    reason = f'TREND: categorical breakdown ({breakdown}) cannot convert to numeric'
                else:
                    reason = 'TREND: insufficient data points or conversion error'
            elif pattern.upper() == 'OUTSTANDING_VALUE':
                reason = 'OUTSTANDING_VALUE: insufficient data or std=0'
            elif pattern.upper() == 'ATTRIBUTION':
                reason = 'ATTRIBUTION: sparse contingency table or chi-square error'
            elif pattern.upper() == 'DISTRIBUTION_DIFFERENCE':
                if breakdown == col:
                    reason = 'DISTRIBUTION_DIFFERENCE: breakdown equals col (invalid KS-test)'
                else:
                    reason = 'DISTRIBUTION_DIFFERENCE: insufficient samples or KS-test error'
            
            failures.append({
                'idx': i,
                'pattern': pattern,
                'measure': measure,
                'breakdown': breakdown,
                'col': col,
                'breakdown_resolved': breakdown_resolved,
                'col_resolved': col_resolved,
                'reason': reason
            })
    
    print(f"\nTotal failures: {len(failures)}/{len(insights)}")
    
    # Group by reason
    reason_groups = {}
    for fail in failures:
        reason = fail['reason']
        if reason not in reason_groups:
            reason_groups[reason] = []
        reason_groups[reason].append(fail)
    
    print(f"\nFailure reasons summary:")
    for reason, items in sorted(reason_groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {reason}: {len(items)} insights")
    
    print(f"\nDetailed failures:")
    for fail in failures[:50]:  # Show first 50
        print(f"  Insight {fail['idx']}:")
        print(f"    Pattern: {fail['pattern']}")
        print(f"    Measure: {fail['measure']}")
        print(f"    Breakdown: {fail['breakdown']} -> {fail.get('breakdown_resolved', 'N/A')}")
        print(f"    Column: {fail['col']} -> {fail.get('col_resolved', 'N/A')}")
        print(f"    Reason: {fail['reason']}")
        print()
    
    if len(failures) > 50:
        print(f"  ... and {len(failures) - 50} more failures")
    
    return failures

# Debug both
ifq_failures = debug_insights(insights_ifq, "IFQ")
baseline_failures = debug_insights(insights_baseline, "Baseline")

# Save to file
with open('significance_failures_report.txt', 'w', encoding='utf-8') as f:
    f.write("Significance Evaluation Failure Report\n")
    f.write("="*70 + "\n\n")
    
    f.write(f"IFQ Failures: {len(ifq_failures)}/{len(insights_ifq)}\n")
    for fail in ifq_failures:
        f.write(f"  Insight {fail['idx']}: {fail['pattern']} | {fail['measure']} | {fail['breakdown']} | {fail['col']} | {fail['reason']}\n")
    
    f.write(f"\nBaseline Failures: {len(baseline_failures)}/{len(insights_baseline)}\n")
    for fail in baseline_failures:
        f.write(f"  Insight {fail['idx']}: {fail['pattern']} | {fail['measure']} | {fail['breakdown']} | {fail['col']} | {fail['reason']}\n")

print(f"\nDetailed report saved to: significance_failures_report.txt")
