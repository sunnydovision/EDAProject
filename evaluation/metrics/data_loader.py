"""
Data loading module for evaluation.

Loads preprocessed data directly without cleaning.
"""

import os
import pandas as pd
from typing import Tuple


def load_data(csv_path: str) -> pd.DataFrame:
    """
    Load data from CSV file.
    
    Data is assumed to be preprocessed/cleaned already.
    If data looks numeric but is string type, raises error.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        DataFrame with loaded data
        
    Raises:
        ValueError: If data looks numeric but is string type (not preprocessed)
    """
    # Detect separator from first line
    with open(csv_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    
    # Load data
    df = pd.read_csv(csv_path, sep=sep)
    print(f"Loaded data from: {csv_path}")
    print(f"  Shape: {len(df)} rows, {len(df.columns)} columns")
    
    # Parse date columns automatically (same as QUIS data loader)
    date_columns = []
    for col in df.columns:
        col_lower = col.lower()
        # Check for common date column names
        if any(date_keyword in col_lower for date_keyword in ['date', 'ngày', 'ngay', 'time']):
            if df[col].dtype == object or 'str' in str(df[col].dtype).lower():
                try:
                    # Try parsing with dayfirst=True for European format
                    df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                    if df[col].notna().sum() > 0:
                        date_columns.append(col)
                        print(f"  Parsed {col} as datetime")
                except Exception:
                    pass
    
    # Validate that data is preprocessed (no string columns that look numeric)
    string_numeric_cols = []
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        if df[col].dtype == object or 'str' in dtype_str.lower():
            sample = df[col].dropna().head(20).astype(str)
            # Check if column looks like numeric data (European format or regular numbers)
            # Match patterns like: "123,45", "1234,5678", "1234567"
            numeric_like = sample.str.match(r'^[\d,.]+$')
            if numeric_like.sum() >= len(sample) * 0.8:
                string_numeric_cols.append(col)
    
    if string_numeric_cols:
        raise ValueError(
            f"Data is not preprocessed. The following columns look numeric but are string type: {string_numeric_cols}\n"
            f"Please run preprocessing script first to convert European number format to numeric.\n"
            f"Example: python data/transactions_data_preprocess.py"
        )
    
    return df


def load_and_clean_data(csv_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load data from CSV and return both raw and cleaned versions.
    
    Data is assumed to be preprocessed/cleaned already.
    Both raw and cleaned will be the same dataframe.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Tuple of (raw_df, cleaned_df)
        - raw_df: Original dataframe
        - cleaned_df: Same dataframe (data is preprocessed)
    """
    df = load_data(csv_path)
    return df, df
