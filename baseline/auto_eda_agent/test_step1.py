"""
Test script for Step 1: Data Profiling Agent
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from agent import AgenticAutoEDA

data_file = "../../data/Adidas_cleaned.csv"
output_dir = "output_adidas_cleaned"

# Initialize agent
agent = AgenticAutoEDA(data_file)

# Run only Step 1
print("=" * 70)
print("🤖 TESTING STEP 1: DATA PROFILING AGENT")
print("=" * 70)

step1_dir = f"{output_dir}/step1_profiling"
os.makedirs(step1_dir, exist_ok=True)

step1_output = agent._run_profiling_agent(step1_dir, max_iterations=1)

print("\n✅ Step 1 test complete")
print(f"Output saved to: {step1_dir}/profile.json")

# Verify output format
import json
with open(f"{step1_dir}/profile.json", 'r') as f:
    profile = json.load(f)

# Check first column
first_col = list(profile['columns'].keys())[0]
print(f"\nSample column '{first_col}':")
print(f"  semantic_meaning: {profile['columns'][first_col].get('semantic_meaning', 'MISSING')}")
print(f"  data_type_class: {profile['columns'][first_col].get('data_type_class', 'MISSING')}")
print(f"  importance: {profile['columns'][first_col].get('importance', 'MISSING')}")
print(f"  potential_issues: {profile['columns'][first_col].get('potential_issues', 'MISSING')}")

# Check all columns have required fields
required_fields = ['semantic_meaning', 'data_type_class', 'importance', 'potential_issues']
print(f"\nChecking required fields in all columns...")
all_ok = True
for col_name, col_data in profile['columns'].items():
    for field in required_fields:
        if field not in col_data:
            print(f"  ❌ Column '{col_name}' missing field: {field}")
            all_ok = False

if all_ok:
    print(f"  ✅ All columns have required fields: {required_fields}")
