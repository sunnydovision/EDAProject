"""
Test script for Step 3: Statistical Analysis Agent
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from agent import AgenticAutoEDA

data_file = "../../data/Adidas_cleaned.csv"
output_dir = "output_adidas_cleaned"

# Initialize agent
agent = AgenticAutoEDA(data_file)

# Run only Step 3 (requires Step 1 and Step 2 outputs to exist)
print("=" * 70)
print("🤖 TESTING STEP 3: STATISTICAL ANALYSIS AGENT")
print("=" * 70)

step3_dir = f"{output_dir}/step3_statistics"
os.makedirs(step3_dir, exist_ok=True)

step3_output = agent._run_statistics_agent(step3_dir, max_iterations=1)

print("\n✅ Step 3 test complete")
print(f"Output saved to: {step3_dir}/statistics.json")

# Verify output format
import json
with open(f"{step3_dir}/statistics.json", 'r') as f:
    report = json.load(f)

print(f"\nNumerical columns: {report['summary']['numerical_columns']}")
print(f"Categorical columns: {report['summary']['categorical_columns']}")
print(f"Strong correlations: {report['summary']['strong_correlations']}")
print(f"Key findings: {len(report['interpretation'].get('key_findings', []))}")
