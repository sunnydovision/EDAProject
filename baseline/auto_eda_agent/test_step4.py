"""
Test script for Step 4: Pattern Discovery Agent
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from agent import AgenticAutoEDA

data_file = "../../data/adidas_cleaned.csv"
output_dir = "output_adidas_cleaned"

# Initialize agent
agent = AgenticAutoEDA(data_file)

# Run only Step 4 (requires Step 1, 2, 3 outputs to exist)
print("=" * 70)
print("🤖 TESTING STEP 4: PATTERN DISCOVERY AGENT")
print("=" * 70)

step4_dir = f"{output_dir}/step4_patterns"
os.makedirs(step4_dir, exist_ok=True)

step4_output = agent._run_pattern_agent(step4_dir, max_iterations=1)

print("\n✅ Step 4 test complete")
print(f"Output saved to: {step4_dir}/patterns.json")

# Verify output format
import json
with open(f"{step4_dir}/patterns.json", 'r') as f:
    report = json.load(f)

print(f"\nTotal patterns: {report['total_patterns']}")
print(f"Pattern categories: {report['pattern_categories']}")
for category, patterns in report['patterns_by_category'].items():
    print(f"  {category}: {len(patterns)} patterns")
