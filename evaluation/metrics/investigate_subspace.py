import json
import pandas as pd

# Load baseline insights
with open("../baseline/auto_eda_agent/output/ifq_format/insights_summary.json", 'r') as f:
    baseline_insights = json.load(f)

# Load actual data
df = pd.read_csv("../data/Adidas_cleaned.csv", sep=';')

print("="*70)
print("DEEP INVESTIGATION: Subspace Filtering Issues")
print("="*70)

# Analyze a specific failed insight
insight_idx = 7
insight = baseline_insights[insight_idx]['insight']

print(f"\n--- Failed Insight #{insight_idx} ---")
print(f"Breakdown: {insight.get('breakdown')}")
print(f"Measure: {insight.get('measure')}")
print(f"Subspace: {insight.get('subspace')}")
print(f"Pattern: {insight.get('pattern')}")

# Check subspace values
subspace = insight.get('subspace', [])
if subspace:
    print(f"\nSubspace conditions:")
    for col, val in subspace:
        print(f"  {col} = {val}")
        
        # Check if column exists
        if col in df.columns:
            unique_vals = df[col].unique()
            print(f"  ✓ Column '{col}' exists")
            print(f"  Unique values in data: {list(unique_vals)[:10]}")
            
            # Check if the subspace value exists
            if val in unique_vals:
                print(f"  ✓ Value '{val}' exists in column")
                # Show filtered data
                filtered = df[df[col] == val]
                print(f"  Filtered data shape: {filtered.shape}")
            else:
                print(f"  ✗ Value '{val}' NOT found in column")
        else:
            print(f"  ✗ Column '{col}' NOT found in data")

# Test actual computation
breakdown = insight.get('breakdown')
measure = insight.get('measure')
if breakdown and breakdown in df.columns:
    print(f"\n--- Testing computation ---")
    
    # Global computation (no subspace)
    if measure == "MEAN(Operating Profit)":
        global_result = df.groupby(breakdown)['Operating Profit'].mean()
        print(f"Global computation result (first 10):")
        print(global_result.head(10))
        
    # Subspace computation
    if subspace:
        filtered_df = df.copy()
        for col, val in subspace:
            if col in df.columns and val in df[col].unique():
                filtered_df = filtered_df[filtered_df[col] == val]
        
        print(f"\nFiltered data shape: {filtered_df.shape}")
        if measure == "MEAN(Operating Profit)" and len(filtered_df) > 0:
            subspace_result = filtered_df.groupby(breakdown)['Operating Profit'].mean()
            print(f"Subspace computation result (first 10):")
            print(subspace_result.head(10))

# Check view_labels
view_labels = baseline_insights[insight_idx].get('view_labels', [])
print(f"\n--- View Labels from LLM ---")
print(f"View labels (first 20): {view_labels[:20]}")

print("\n" + "="*70)
print("ANALYSIS OF ALL SUBSPACE-RELATED FAILURES")
print("="*70)

# Count insights with subspace
with_subspace = 0
with_subspace_failed = 0

for i, item in enumerate(baseline_insights):
    insight = item['insight']
    subspace = insight.get('subspace', [])
    
    if subspace:
        with_subspace += 1
        
        # Check if this insight failed
        # Load failed indices from eval results
        # For now, just count

print(f"\nTotal insights with subspace: {with_subspace}")

# Check specific subspace values that failed
print("\n--- Checking common subspace values ---")
common_columns = ['Sales Method', 'Retailer', 'Region', 'Product']
for col in common_columns:
    if col in df.columns:
        unique_vals = df[col].unique()
        print(f"\n{col}: {len(unique_vals)} unique values")
        print(f"  Sample: {list(unique_vals)[:5]}")
