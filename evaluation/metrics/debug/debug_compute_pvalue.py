"""
Debug compute_p_value directly for failing insights

Run from project root:
  source venv/bin/activate && PYTHONPATH=. python evaluation/metrics/debug/debug_compute_pvalue.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evaluation.metrics.data_loader import load_and_clean_data
from evaluation.configs.debug_config import DATA_PATH
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, ks_2samp

# Load data
csv_path = DATA_PATH
df_raw, df_cleaned = load_and_clean_data(csv_path)

# Test specific failing cases
print("Testing Insight 53: Trend with COUNT(Retailer ID) by Invoice Date")
breakdown = "Invoice Date"
col = "Retailer ID"
print(f"  df[breakdown].dtype: {df_cleaned[breakdown].dtype}")
print(f"  df[col].dtype: {df_cleaned[col].dtype}")
print(f"  breakdown == col: {breakdown == col}")

# Try the Trend logic
print(f"  Checking if breakdown is categorical: {df_cleaned[breakdown].dtype == 'object'}")
print(f"  Checking if breakdown is datetime: {df_cleaned[breakdown].dtype.name.startswith('datetime')}")
if df_cleaned[breakdown].dtype == 'object' or df_cleaned[breakdown].dtype.name.startswith('datetime'):
    print("  Using categorical breakdown aggregation")
    try:
        print("  Attempting groupby...")
        grouped = df_cleaned.groupby(breakdown)[col].count()
        print(f"  Grouped shape: {grouped.shape}")
        x_data = pd.to_numeric(grouped.index, errors='coerce')
        y_data = grouped.values
        print(f"  x_data: {x_data[:5] if len(x_data) > 5 else x_data}")
        print(f"  y_data: {y_data[:5] if len(y_data) > 5 else y_data}")
        mask = x_data.notna() & y_data.notna()
        print(f"  mask.sum(): {mask.sum()}")
        if mask.sum() >= 3:
            x_clean = x_data[mask].values
            y_clean = y_data[mask].values
            print(f"  x_clean: {x_clean[:5]}")
            print(f"  y_clean: {y_clean[:5]}")
            _, _, _, p_value, _ = stats.linregress(x_clean, y_clean)
            print(f"  P-value: {p_value}")
        else:
            print("  Not enough data points")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("  Not using categorical breakdown aggregation")

print("\n" + "="*70)
print("Testing Insight 62: Attribution with COUNT(Invoice Date) by Retailer")
breakdown = "Retailer"
col = "Invoice Date"
print(f"  df[breakdown].dtype: {df_cleaned[breakdown].dtype}")
print(f"  df[col].dtype: {df_cleaned[col].dtype}")

# Try the Attribution logic
if df_cleaned[col].dtype == 'object':
    print("  Using categorical crosstab")
    try:
        contingency_table = pd.crosstab(df_cleaned[breakdown], df_cleaned[col])
        print(f"  Contingency table shape: {contingency_table.shape}")
        print(f"  Contingency table:\n{contingency_table}")
        print(f"  Table sum: {contingency_table.sum().sum()}")
        if contingency_table.size > 0 and contingency_table.sum().sum() > 0:
            _, p_value, _, expected = chi2_contingency(contingency_table)
            print(f"  P-value: {p_value}")
            print(f"  Expected: {expected}")
        else:
            print("  Table is empty")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
