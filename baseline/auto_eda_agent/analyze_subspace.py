"""
Analyze subspace generation from new baseline output
"""
import json

insights_path = "output_adidas_cleaned_new/quis_format/insights_summary.json"

with open(insights_path, 'r', encoding='utf-8') as f:
    insights = json.load(f)

print(f"Total insights: {len(insights)}")

with_subspace = 0
without_subspace = 0
subspace_columns = {}
subspace_examples = []

for insight in insights:
    subspace = insight['insight']['subspace']
    if subspace and len(subspace) > 0:
        with_subspace += 1
        for col, val in subspace:
            subspace_columns[col] = subspace_columns.get(col, 0) + 1
        if len(subspace_examples) < 10:
            subspace_examples.append({
                'question': insight['question'],
                'subspace': subspace
            })
    else:
        without_subspace += 1

print(f"\nInsights with subspace: {with_subspace} ({with_subspace/len(insights)*100:.1f}%)")
print(f"Insights without subspace: {without_subspace} ({without_subspace/len(insights)*100:.1f}%)")

if subspace_columns:
    print(f"\nSubspace columns distribution:")
    for col, count in sorted(subspace_columns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col}: {count} insights")

if subspace_examples:
    print(f"\nExamples of subspace generation:")
    for ex in subspace_examples:
        print(f"  Question: {ex['question'][:60]}...")
        print(f"    Subspace: {ex['subspace']}")
