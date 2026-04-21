"""
Test script for data_loader.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_loader import load_and_clean_data

# Test data loader
print("Testing data_loader.py...")
print("="*70)

csv_path = "../data/Adidas.csv"
print(f"Loading data from: {csv_path}")

try:
    df_raw, df_cleaned = load_and_clean_data(csv_path)
    
    print(f"Raw dataframe:")
    print(f"  - Rows: {len(df_raw)}")
    print(f"  - Columns: {list(df_raw.columns)}")
    print(f"  - Dtypes: {df_raw.dtypes.to_dict()}")
    
    print(f"\nCleaned dataframe:")
    print(f"  - Rows: {len(df_cleaned)}")
    print(f"  - Columns: {list(df_cleaned.columns)}")
    print(f"  - Dtypes: {df_cleaned.dtypes.to_dict()}")
    
    print(f"\nSample raw data (first 3 rows):")
    print(df_raw.head(3))
    
    print(f"\nSample cleaned data (first 3 rows):")
    print(df_cleaned.head(3))
    
    print("\n" + "="*70)
    print("Test PASSED!")
    
except Exception as e:
    print(f"\nTest FAILED: {e}")
    import traceback
    traceback.print_exc()
