#!/usr/bin/env python3
"""
Preprocess Adidas.csv data by cleaning currency, percentage, and European number formatting.
Run this script once to create a cleaned version of the data.

Column processing (based on actual data analysis):
- Invoice Date: Parse as datetime (handles both M/D/YY and D/M/YY formats)
- Price per Unit: Remove $, convert EU format (comma=decimal), convert to int (all values are whole numbers like 50, 40, 45)
- Units Sold: Already numeric, remains float64 (has decimal values like 1.20, 1.25, 1.22)
- Total Sales: Remove $, convert EU format (dot=thousands), convert to int (all values are whole numbers like 600000, 382500)
- Operating Profit: Remove $, convert EU format (dot=thousands), convert to int (all values are whole numbers like 300000, 133875)
- Operating Margin: Remove %, convert to int (all values are whole numbers like 50, 30, 35)
- Retailer ID: Already int64, convert to Int64 for consistency
"""

import warnings
import pandas as pd
import sys
import os

# Suppress date parsing warning
warnings.filterwarnings('ignore', category=UserWarning)


def clean_dataframe(df: pd.DataFrame, sep: str) -> pd.DataFrame:
    """
    Clean dataframe by removing currency symbols, percentage signs, converting European number format,
    parsing dates, and converting whole numbers to integers.
    
    Args:
        df: DataFrame to clean
        sep: Separator used in CSV (determines number format)
    
    Returns:
        Cleaned DataFrame
    """
    print("\nColumn processing:")
    
    # Process Invoice Date: Parse as datetime (handle both M/D/YY and D/M/YY formats)
    if "Invoice Date" in df.columns:
        print("  Invoice Date: Parsing as datetime (handling M/D/YY and D/M/YY formats)")
        df["Invoice Date"] = pd.to_datetime(df["Invoice Date"], dayfirst=True, errors="coerce")
    
    # Process numeric columns with currency/percentage symbols
    for col in df.columns:
        if col == "Invoice Date":
            continue
        
        # Check for object or string dtype (QUIS only checks object, but that doesn't work with this data)
        dtype_str = str(df[col].dtype)
        if df[col].dtype == object or 'str' in dtype_str.lower() or 'string' in dtype_str.lower():
            sample = df[col].dropna().head(20).astype(str).str.strip()
            # Detect columns that look numeric: contain $ or % with digits
            has_currency_or_percent = sample.str.contains(r"[$%]")
            has_digits = sample.str.contains(r"[\d.,]")
            numeric_like = has_currency_or_percent & has_digits
            if numeric_like.sum() >= len(sample) * 0.8:
                print(f"  {col}: Removing $/% symbols, converting number format")
                cleaned = df[col].astype(str).str.replace(r"[$%]", "", regex=True).str.strip()
                if sep == ";":
                    # EU format: dot=thousands, comma=decimal
                    cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
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
    input_path = "Adidas.csv"
    output_path = "Adidas_cleaned.csv"
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Detect separator from first line
    with open(input_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    print(f"Detected separator: '{sep}'")
    
    # Load raw data (without decimal parameter - QUIS's approach doesn't work with this data)
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
