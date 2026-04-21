"""
Test script for Step 2: Quality Analysis Agent
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from agent import AgenticAutoEDA

data_file = "../../data/Adidas_cleaned.csv"
output_dir = "output_adidas_cleaned"

# Initialize agent
agent = AgenticAutoEDA(data_file)

# Run only Step 2 (requires Step 1 output to exist)
print("=" * 70)
print("🤖 TESTING STEP 2: QUALITY ANALYSIS AGENT")
print("=" * 70)

step2_dir = f"{output_dir}/step2_quality"
os.makedirs(step2_dir, exist_ok=True)

step2_output = agent._run_quality_agent(step2_dir, max_iterations=1)

print("\n✅ Step 2 test complete")
print(f"Output saved to: {step2_dir}/quality_report.json")

# Verify output format
import json
with open(f"{step2_dir}/quality_report.json", 'r') as f:
    report = json.load(f)

print(f"\nQuality Score: {report['summary']['data_quality_score']}")
print(f"Total Issues: {report['summary']['total_issues']}")
print(f"Critical Issues: {report['summary']['critical_issues']}")

# Check if ID columns were excluded from outlier analysis
outliers = report['metrics'].get('outliers', {})
print(f"\nOutlier analysis columns: {list(outliers.keys())}")
