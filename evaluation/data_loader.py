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
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        DataFrame with loaded data
    """
    # Detect separator from first line
    with open(csv_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    sep = ";" if first_line.count(";") > first_line.count(",") else ","
    
    # Load data
    df = pd.read_csv(csv_path, sep=sep)
    print(f"Loaded data from: {csv_path}")
    print(f"  Shape: {len(df)} rows, {len(df.columns)} columns")
    
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
