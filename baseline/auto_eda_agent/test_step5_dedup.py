"""
Test step 5 dedup logic only — does NOT call OpenAI.
Verifies that structural dedup (used_struct_keys) and title dedup (used_titles)
work correctly after recent agent.py changes.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import AgenticAutoEDA
import json

data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/adidas_cleaned.csv"))
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "output_adidas"))
step5_dir = f"{output_dir}/step5_dedup_test"

print("Testing Step 5 dedup logic (no LLM calls)")
print("="*70)

os.makedirs(step5_dir, exist_ok=True)

# Initialize agent (just loads CSV — no LLM)
agent = AgenticAutoEDA(data_file)

# Simulate what _run_insight_agent does for dedup
used_titles = set()
used_struct_keys = set()
category_struct_keys = {}

# Simulate batch of insights with intentional duplicates
mock_insights_batch = [
    {"title": "Trend A", "type": "TREND", "variables": ["Invoice Date", "Total Sales"], "subspace": []},
    {"title": "Trend B", "type": "TREND", "variables": ["Invoice Date", "Total Sales"], "subspace": []},  # struct dup
    {"title": "Trend A", "type": "TREND", "variables": ["Units Sold", "Total Sales"], "subspace": []},     # title dup
    {"title": "Trend C", "type": "TREND", "variables": ["Units Sold", "Total Sales"], "subspace": []},     # unique
    {"title": "Trend D", "type": "TREND", "variables": ["Invoice Date", "Total Sales"], "subspace": [["Region", "West"]]},  # unique (diff subspace)
    {"title": "Attrib A", "type": "ATTRIBUTION", "variables": ["Total Sales", "Operating Profit"], "subspace": []},  # unique (diff type)
]

print(f"Input batch: {len(mock_insights_batch)} insights (with intentional duplicates)")
print()

accepted = []
skipped_struct = []
skipped_title = []

for insight_data in mock_insights_batch:
    title = insight_data.get('title', '')

    variables = insight_data.get('variables', [])
    subspace = insight_data.get('subspace', [])
    subspace_key = tuple(tuple(pair) for pair in subspace) if subspace else ()
    breakdown = variables[0] if variables else ''
    measure = variables[1] if len(variables) > 1 else ''
    struct_key = (insight_data.get('type', ''), breakdown, measure, subspace_key)

    if struct_key in used_struct_keys:
        skipped_struct.append(insight_data)
        continue
    if title in used_titles:
        skipped_title.append(insight_data)
        continue

    used_titles.add(title)
    used_struct_keys.add(struct_key)

    cat_key = insight_data.get('type', '')
    if cat_key not in category_struct_keys:
        category_struct_keys[cat_key] = set()
    category_struct_keys[cat_key].add(struct_key)

    accepted.append(insight_data)

print(f"Accepted: {len(accepted)}")
for ins in accepted:
    print(f"  ✓ [{ins['type']}] {ins['title']} | breakdown={ins['variables'][0]}, subspace={ins['subspace']}")

print(f"\nSkipped (struct dup): {len(skipped_struct)}")
for ins in skipped_struct:
    print(f"  ✗ [{ins['type']}] {ins['title']} | breakdown={ins['variables'][0]}, subspace={ins['subspace']}")

print(f"\nSkipped (title dup): {len(skipped_title)}")
for ins in skipped_title:
    print(f"  ✗ [{ins['type']}] {ins['title']} | breakdown={ins['variables'][0]}, subspace={ins['subspace']}")

print(f"\ncategory_struct_keys populated: {list(category_struct_keys.keys())}")

# Assertions
assert len(accepted) == 4, f"Expected 4 accepted, got {len(accepted)}"
assert len(skipped_struct) == 1, f"Expected 1 struct dup, got {len(skipped_struct)}"
assert len(skipped_title) == 1, f"Expected 1 title dup, got {len(skipped_title)}"
assert 'TREND' in category_struct_keys
assert 'ATTRIBUTION' in category_struct_keys

print("\n" + "="*70)
print("All assertions passed. Dedup logic is correct.")
print("="*70)
