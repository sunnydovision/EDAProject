"""
Simple test for updated data_loader
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from data_loader import load_data, load_and_clean_data

# Test load_data
print("=" * 70)
print("Testing load_data()")
print("=" * 70)
df = load_data("../data/Adidas_cleaned.csv")
print(f"✓ load_data() successful")
print(f"  Shape: {df.shape}")
print(f"  Columns: {list(df.columns)}")

# Test load_and_clean_data
print("\n" + "=" * 70)
print("Testing load_and_clean_data()")
print("=" * 70)
df_raw, df_cleaned = load_and_clean_data("../data/Adidas_cleaned.csv")
print(f"✓ load_and_clean_data() successful")
print(f"  Raw shape: {df_raw.shape}")
print(f"  Cleaned shape: {df_cleaned.shape}")
print(f"  Are they the same? {df_raw.equals(df_cleaned)}")

print("\n✅ All data_loader tests passed!")
