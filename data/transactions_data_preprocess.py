#!/usr/bin/env python3
"""
Preprocess transactions.csv data by cleaning European number formatting and parsing dates.
Run this script once to create a cleaned version of the data.

Column processing (based on actual data analysis):
- Ngày bán: Parse as datetime (format: D/M/YY)
- Numeric columns with EU format (comma as decimal): Convert to float
- Boolean columns (Cuối_tuần, Cờ_giao_hàng_trễ, Cờ_khiếu_nại_lặp_lại, Cờ_giao_dịch_bất_thường): Convert TRUE/FALSE to boolean
- Convert whole numbers to integers to avoid ".0" in output
"""

import warnings
import pandas as pd
import sys
import os

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)


def clean_dataframe(df: pd.DataFrame, sep: str) -> pd.DataFrame:
    """
    Clean dataframe by converting European number format, parsing dates,
    converting booleans, and converting whole numbers to integers.
    
    Args:
        df: DataFrame to clean
        sep: Separator used in CSV (determines number format)
    
    Returns:
        Cleaned DataFrame
    """
    print("\nColumn processing:")
    
    # Process Ngày bán: Parse as datetime (format: D/M/YY)
    if "Ngày bán" in df.columns:
        print("  Ngày bán: Parsing as datetime (format: D/M/YY)")
        df["Ngày bán"] = pd.to_datetime(df["Ngày bán"], dayfirst=True, errors="coerce")
    
    # Trim whitespace from all string columns
    for col in df.columns:
        if df[col].dtype == object or 'str' in str(df[col].dtype).lower():
            print(f"  {col}: Trimming whitespace")
            df[col] = df[col].astype(str).str.strip()
    
    # Process numeric columns with EU format (comma as decimal) and boolean columns
    for col in df.columns:
        if col == "Ngày bán":
            continue
        
        # Check for object or string dtype
        dtype_str = str(df[col].dtype)
        if df[col].dtype == object or 'str' in dtype_str.lower() or 'string' in dtype_str.lower():
            sample = df[col].dropna().head(20).astype(str).str.strip()
            
            # Check for boolean values (TRUE/FALSE)
            if sample.str.upper().isin(['TRUE', 'FALSE']).all():
                print(f"  {col}: Converting to boolean")
                df[col] = df[col].astype(str).str.upper().map({'TRUE': True, 'FALSE': False})
                continue
            
            # Check for numeric values with EU format (comma as decimal) OR plain integers
            has_comma_decimal = sample.str.contains(r',\d')
            has_digits = sample.str.contains(r'[\d.,]')
            # Check if it's a plain integer (no comma, only digits and possibly dots as thousand separators)
            is_plain_integer = sample.str.match(r'^[\d\.]+$')
            numeric_like = (has_comma_decimal & has_digits) | is_plain_integer
            if numeric_like.sum() >= len(sample) * 0.8:
                print(f"  {col}: Converting to numeric")
                # For EU format: remove dots (thousand separators), replace comma with dot (decimal)
                # For plain integers: just convert directly
                if has_comma_decimal.sum() >= len(sample) * 0.5:
                    # Has comma decimal, treat as European format
                    cleaned = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                else:
                    # Plain integer, just convert
                    cleaned = df[col].astype(str)
                converted = pd.to_numeric(cleaned, errors="coerce")
                if converted.notna().sum() >= len(df) * 0.5:
                    df[col] = converted
    
    # Convert whole numbers to integers for numeric columns
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
            # Check if all values are whole numbers (no decimal part)
            if (df[col].dropna() % 1 == 0).all():
                print(f"  {col}: Converting to integer (all values are whole numbers)")
                df[col] = df[col].astype('Int64')  # Use Int64 to handle NA values
    
    return df


def main():
    input_path = "transactions.csv"
    output_path = "transactions_cleaned.csv"
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Detect separator from first line
    with open(input_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    print(f"Detected separator: '{sep}'")
    
    # Load raw data
    print(f"Loading data from: {input_path}")
    df = pd.read_csv(input_path, sep=sep)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Original dtypes:\n{df.dtypes}")
    
    # Clean data
    print("\nCleaning data...")
    df_cleaned = clean_dataframe(df.copy(), sep)
    
    # Show which columns were converted
    print(f"\nFinal dtypes:\n{df_cleaned.dtypes}")
    
    # Save cleaned data
    print(f"\nSaving cleaned data to: {output_path}")
    df_cleaned.to_csv(output_path, index=False, sep=sep)
    print("Done!")
    
    # Show sample of cleaned data
    print("\nSample of cleaned data:")
    print(df_cleaned.head())


if __name__ == "__main__":
    main()
