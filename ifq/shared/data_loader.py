#!/usr/bin/env python3
"""
Shared data loader for IFQ (QUGEN and ISGEN).

This module provides a common data loading function with validation
to ensure data is preprocessed before being used by IFQ components.
"""

from __future__ import annotations

import os
import sys

import pandas as pd


def load_data(csv_path: str) -> pd.DataFrame:
    """
    Load data from CSV file with validation.
    
    Data must be preprocessed (numeric columns already converted).
    If data looks numeric but is string type, raises ValueError.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        DataFrame with loaded data
        
    Raises:
        ValueError: If data is not preprocessed (numeric columns are strings)
        FileNotFoundError: If CSV file does not exist
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    
    # Detect separator from first line
    with open(csv_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    
    # Load data
    df = pd.read_csv(csv_path, sep=sep)
    print(f"Loaded data from: {csv_path}")
    print(f"  Shape: {len(df)} rows, {len(df.columns)} columns")
    
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
