#!/usr/bin/env python3
"""
Preprocess Adidas.csv data by cleaning currency, percentage, and European number formatting.
Run this script once to create a cleaned version of the data.

Column processing (based on actual data analysis):
- Invoice Date: Parse as datetime (handles both M/D/YY and D/M/YY formats)
- Price per Unit: Remove $, convert EU format (comma=decimal), convert to int (all values are whole numbers like 50, 40, 45)
- Units Sold: Convert EU format (dot=decimal), remains float (has decimal values like 1.2, 1.0, 850.0)
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
    
    # Process each column with specific rules
    column_rules = {
        "Price per Unit": {"remove_symbols": "$", "dot_thousands": False, "comma_decimal": True, "to_int": True},
        "Units Sold": {"remove_symbols": "", "dot_thousands": False, "comma_decimal": True, "to_int": False},
        "Total Sales": {"remove_symbols": "$", "dot_thousands": True, "comma_decimal": False, "to_int": True},
        "Operating Profit": {"remove_symbols": "$", "dot_thousands": True, "comma_decimal": False, "to_int": True},
        "Operating Margin": {"remove_symbols": "%", "dot_thousands": False, "comma_decimal": False, "to_int": True},
        "Retailer ID": {"remove_symbols": "", "dot_thousands": False, "comma_decimal": False, "to_int": True},
    }
    
    for col in df.columns:
        if col == "Invoice Date":
            continue
        
        # Get column-specific rules or use default
        rules = column_rules.get(col, {"remove_symbols": "", "dot_thousands": False, "comma_decimal": False, "to_int": False})
        
        # Check if column needs cleaning (object/string type)
        dtype_str = str(df[col].dtype)
        if df[col].dtype == object or 'str' in dtype_str.lower() or 'string' in dtype_str.lower():
            sample = df[col].dropna().head(20).astype(str).str.strip()
            
            # Detect if column looks numeric
            has_symbols = False
            if rules["remove_symbols"]:
                has_symbols = sample.str.contains(r"[$%]").any()
            
            has_digits = sample.str.contains(r"[\d.,]").any()
            numeric_like = has_symbols or has_digits
            
            if numeric_like and sample.str.contains(r"[\d]").sum() >= len(sample) * 0.5:
                print(f"  {col}: Cleaning with specific rules")
                cleaned = df[col].astype(str).str.strip()
                
                # Remove currency/percentage symbols
                if rules["remove_symbols"]:
                    cleaned = cleaned.str.replace(f"[{rules['remove_symbols']}]", "", regex=True)
                
                # Handle European number format
                if rules["dot_thousands"]:
                    # EU format: dot is thousands separator (e.g., "1.200" = 1200)
                    cleaned = cleaned.str.replace(".", "", regex=False)
                if rules["comma_decimal"]:
                    # EU format: comma is decimal (e.g., "50,00" = 50.0)
                    cleaned = cleaned.str.replace(",", ".", regex=False)
                
                # Convert to numeric
                converted = pd.to_numeric(cleaned, errors="coerce")
                if converted.notna().sum() >= len(df) * 0.5:
                    df[col] = converted
    
    # Convert to integers for columns that should be integers
    for col in df.columns:
        if col in column_rules and column_rules[col]["to_int"]:
            if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                print(f"  {col}: Converting to integer")
                df[col] = df[col].astype('Int64')  # Use Int64 to handle NA values
    
    return df


def main():
    input_path = "data/raw/adidas.csv"
    output_path = "data/Adidas_cleaned.csv"
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Detect separator from first line
    with open(input_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    print(f"Detected separator: '{sep}'")
    
    # Load raw data - read Units Sold as string to handle European format
    print(f"Loading data from: {input_path}")
    df = pd.read_csv(input_path, sep=sep, dtype={"Units Sold": str})
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
