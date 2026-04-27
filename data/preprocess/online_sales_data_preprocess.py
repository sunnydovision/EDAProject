#!/usr/bin/env python3
"""
Preprocess online_sales.csv data by converting separator to semicolon,
parsing dates, and ensuring proper data types.

Column processing (based on actual data analysis):
- Date: Parse as datetime (format: YYYY-MM-DD)
- Transaction ID: Convert to integer
- Units Sold: Convert to integer
- Unit Price: Convert to float
- Total Revenue: Convert to float
- Trim whitespace from all string columns
- Output with ; separator for consistency with other datasets
"""

import warnings
import pandas as pd
import sys
import os

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean dataframe by parsing dates, converting numeric columns,
    trimming whitespace, and ensuring proper data types.
    
    Args:
        df: DataFrame to clean
    
    Returns:
        Cleaned DataFrame
    """
    print("\nColumn processing:")
    
    # Trim whitespace from all string columns
    for col in df.columns:
        if df[col].dtype == object or 'str' in str(df[col].dtype).lower():
            df[col] = df[col].astype(str).str.strip()
    
    # Process Date: Parse as datetime (format: YYYY-MM-DD)
    if "Date" in df.columns:
        print("  Date: Parsing as datetime (format: YYYY-MM-DD)")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    
    # Convert numeric columns
    numeric_columns = {
        "Transaction ID": "int",
        "Units Sold": "int",
        "Unit Price": "float",
        "Total Revenue": "float",
    }
    
    for col, expected_type in numeric_columns.items():
        if col in df.columns:
            if df[col].dtype == object:
                print(f"  {col}: Converting to {expected_type}")
                if expected_type == "int":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype('Int64')
                else:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            # Check if integer column should be Int64
            if expected_type == "int" and df[col].dtype in ['float64', 'float32']:
                if (df[col].dropna() % 1 == 0).all():
                    print(f"  {col}: Converting to integer (all values are whole numbers)")
                    df[col] = df[col].astype('Int64')
    
    return df


def main():
    input_path = "data/raw/online_sales.csv"
    output_path = "data/online_sales_cleaned.csv"
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Load raw data
    print(f"Loading data from: {input_path}")
    df = pd.read_csv(input_path, sep=',')
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Original dtypes:\n{df.dtypes}")
    
    # Clean data
    print("\nCleaning data...")
    df_cleaned = clean_dataframe(df.copy())
    
    # Show which columns were converted
    print(f"\nFinal dtypes:\n{df_cleaned.dtypes}")
    
    # Save cleaned data with ; separator for consistency
    print(f"\nSaving cleaned data to: {output_path}")
    df_cleaned.to_csv(output_path, index=False, sep=';')
    print("Done!")
    
    # Show sample of cleaned data
    print("\nSample of cleaned data:")
    print(df_cleaned.head())


if __name__ == "__main__":
    main()
