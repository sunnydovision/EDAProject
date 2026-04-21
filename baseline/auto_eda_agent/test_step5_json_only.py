"""
Test script to test step 5 insight extraction without plot generation.
Uses _run_insight_agent — loads context from existing output_adidas_cleaned step 1-4 files.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import AgenticAutoEDA
import json

# Use existing baseline output (output_adidas_cleaned) which has all steps completed
data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/Adidas_cleaned.csv"))
existing_output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "new_output"))
step5_dir = f"{existing_output_dir}/step5_insights_json_only"

print("Testing step 5 (insight extraction) without plot generation...")
print(f"Data: {data_file}")
print(f"Output: {step5_dir}")
print(f"Using existing outputs from: {existing_output_dir}")

os.makedirs(step5_dir, exist_ok=True)

# Initialize agent
agent = AgenticAutoEDA(data_file)

# Skip chart generation to save time and cost
agent._generate_chart = lambda insight_data, output_path: output_path

print("\n🤖 Extracting insights (no charts)...")
print("="*70)

# _run_insight_agent loads context automatically from step5_dir/../step{1-4}*/
final_insights = agent._run_insight_agent(step5_dir, max_iterations=1)

print(f"✓ Insights saved: {step5_dir}/insights.json")

# Analyze per-category distribution
print(f"\n{'='*70}")
print(f"Per-Category Distribution")
print(f"{'='*70}")
category_counts = {}
for ins in final_insights:
    itype = ins.get('insight_type', 'UNKNOWN')
    category_counts[itype] = category_counts.get(itype, 0) + 1
for cat, count in sorted(category_counts.items()):
    print(f"  {cat}: {count} insights")

# Analyze subspace generation
print(f"\n{'='*70}")
print(f"Subspace Generation Analysis")
print(f"{'='*70}")
print(f"Total insights: {len(final_insights)}")

with_subspace = 0
without_subspace = 0
subspace_examples = []
subspace_columns = {}

for i, insight in enumerate(final_insights):
    subspace = insight.get('subspace', [])
    if subspace and len(subspace) > 0:
        with_subspace += 1
        for col, val in subspace:
            subspace_columns[col] = subspace_columns.get(col, 0) + 1
        if len(subspace_examples) < 5:
            subspace_examples.append({
                'index': i,
                'title': insight['title'],
                'subspace': subspace
            })
    else:
        without_subspace += 1

if len(final_insights) > 0:
    print(f"Insights with subspace: {with_subspace} ({with_subspace/len(final_insights)*100:.1f}%)")
    print(f"Insights without subspace: {without_subspace} ({without_subspace/len(final_insights)*100:.1f}%)")
else:
    print(f"Insights with subspace: {with_subspace}")
    print(f"Insights without subspace: {without_subspace}")

if subspace_columns:
    print(f"\nSubspace columns distribution:")
    for col, count in subspace_columns.items():
        print(f"  {col}: {count} insights")

if subspace_examples:
    print(f"\nExamples of subspace generation:")
    for ex in subspace_examples:
        print(f"  Insight {ex['index']}: {ex['title'][:50]}...")
        print(f"    Subspace: {ex['subspace']}")
else:
    print(f"\nNo subspace generated")

print(f"\n{'='*70}")
print(f"Test complete. Check {step5_dir}/insights.json for details")
print(f"{'='*70}")
