#!/usr/bin/env python3
"""
Preprocess employee_attrition.csv data by converting Yes/No to boolean,
trimming whitespace, and ensuring proper data types.

Column processing (based on actual data analysis):
- Attrition: Convert Yes/No to boolean
- Over18: Convert Y to boolean (all values are Y)
- OverTime: Convert Yes/No to boolean
- Trim whitespace from all string columns
- Ensure numeric columns have correct data types
"""

import warnings
import pandas as pd
import sys
import os

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)


def clean_dataframe(df: pd.DataFrame, sep: str) -> pd.DataFrame:
    """
    Clean dataframe by converting Yes/No to boolean, trimming whitespace,
    and ensuring proper data types.
    
    Args:
        df: DataFrame to clean
        sep: Separator used in CSV
    
    Returns:
        Cleaned DataFrame
    """
    print("\nColumn processing:")
    
    # Columns to convert from Yes/No to boolean
    yes_no_columns = ["Attrition", "OverTime"]
    
    # Column to convert from Y to boolean
    y_column = ["Over18"]
    
    # Trim whitespace from all string columns
    for col in df.columns:
        if df[col].dtype == object or 'str' in str(df[col].dtype).lower():
            df[col] = df[col].astype(str).str.strip()
    
    # Convert Yes/No columns to boolean
    for col in yes_no_columns:
        if col in df.columns:
            print(f"  {col}: Converting Yes/No to boolean")
            df[col] = df[col].map({'Yes': True, 'No': False}).astype('boolean')
    
    # Convert Y column to boolean
    for col in y_column:
        if col in df.columns:
            print(f"  {col}: Converting Y to boolean")
            df[col] = df[col].map({'Y': True}).astype('boolean')
    
    # Ensure numeric columns are properly typed
    numeric_columns = [
        "Age", "DailyRate", "DistanceFromHome", "Education", "EmployeeCount",
        "EmployeeNumber", "EnvironmentSatisfaction", "HourlyRate", "JobInvolvement",
        "JobLevel", "JobSatisfaction", "MonthlyIncome", "MonthlyRate",
        "NumCompaniesWorked", "PercentSalaryHike", "PerformanceRating",
        "RelationshipSatisfaction", "StandardHours", "StockOptionLevel",
        "TotalWorkingYears", "TrainingTimesLastYear", "WorkLifeBalance",
        "YearsAtCompany", "YearsInCurrentRole", "YearsSinceLastPromotion",
        "YearsWithCurrManager"
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            if df[col].dtype == object:
                print(f"  {col}: Converting to numeric")
                df[col] = pd.to_numeric(df[col], errors="coerce")
            # Check if all values are whole numbers
            if df[col].dtype in ['float64', 'float32']:
                if (df[col].dropna() % 1 == 0).all():
                    print(f"  {col}: Converting to integer (all values are whole numbers)")
                    df[col] = df[col].astype('Int64')
    
    return df


def main():
    input_path = "data/raw/employee_attrition.csv"
    output_path = "data/employee_attrition_cleaned.csv"
    
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
    df_cleaned.to_csv(output_path, index=False, sep=';')
    print("Done!")
    
    # Show sample of cleaned data
    print("\nSample of cleaned data:")
    print(df_cleaned.head())


if __name__ == "__main__":
    main()
