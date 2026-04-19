"""
data_preprocessing.py
---------------------
Cleans and prepares the raw retail dataset for analysis and modeling.
Handles: missing values, data types, duplicates, outlier capping.
"""

import pandas as pd
import numpy as np
import os

def load_data(filepath):
    """Load raw CSV data."""
    print(f"Loading data from: {filepath}")
    df = pd.read_csv(filepath, parse_dates=["date"])
    print(f"✅ Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    return df


def inspect_data(df):
    """Print a full inspection report of the dataframe."""
    print("\n" + "="*60)
    print("DATA INSPECTION REPORT")
    print("="*60)
    print(f"\nShape: {df.shape}")
    print(f"\nData Types:\n{df.dtypes}")
    print(f"\nMissing Values:\n{df.isnull().sum()}")
    print(f"\nDuplicate rows: {df.duplicated().sum()}")
    print(f"\nBasic Statistics:\n{df[['sales_units','revenue','opening_stock']].describe()}")
    print("="*60)


def handle_missing_values(df):
    """
    Strategy:
    - Numerical columns → fill with median (robust to outliers)
    - Categorical columns → fill with mode (most common value)
    - Date column → drop rows with missing dates
    """
    print("\nHandling missing values...")

    # Drop rows where date is missing (critical column)
    before = len(df)
    df = df.dropna(subset=["date"])
    print(f"  Rows dropped due to missing date: {before - len(df)}")

    # Fill numerical missing values with median
    num_cols = ["sales_units", "revenue", "unit_price", "opening_stock",
                "closing_stock", "lead_time_days"]
    for col in num_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  {col}: filled {df[col].isnull().sum()} NaN with median={median_val:.2f}")

    # Fill categorical missing values with mode
    cat_cols = ["store", "category", "product"]
    for col in cat_cols:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)
            print(f"  {col}: filled NaN with mode='{mode_val}'")

    print(f"✅ Missing values handled. Remaining NaN: {df.isnull().sum().sum()}")
    return df


def remove_duplicates(df):
    """Remove duplicate rows."""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    print(f"\n✅ Duplicates removed: {removed} rows")
    return df


def fix_data_types(df):
    """Ensure columns have correct data types."""
    print("\nFixing data types...")
    df["date"]          = pd.to_datetime(df["date"])
    df["sales_units"]   = df["sales_units"].astype(int)
    df["opening_stock"] = df["opening_stock"].astype(int)
    df["closing_stock"] = df["closing_stock"].astype(int)
    df["stockout_flag"] = df["stockout_flag"].astype(int)
    df["lead_time_days"]= df["lead_time_days"].astype(int)
    df["revenue"]       = df["revenue"].astype(float)
    df["unit_price"]    = df["unit_price"].astype(float)
    print("✅ Data types fixed")
    return df


def cap_outliers(df, column, lower_pct=0.01, upper_pct=0.99):
    """
    Cap outliers using percentile method.
    Values below 1st percentile → set to 1st percentile value
    Values above 99th percentile → set to 99th percentile value
    (Better than removing rows — preserves data volume)
    """
    lower = df[column].quantile(lower_pct)
    upper = df[column].quantile(upper_pct)
    before_min, before_max = df[column].min(), df[column].max()
    df[column] = df[column].clip(lower=lower, upper=upper)
    print(f"  {column}: [{before_min:.1f}, {before_max:.1f}] → [{lower:.1f}, {upper:.1f}]")
    return df


def preprocess_pipeline(raw_filepath, processed_filepath):
    """
    Full preprocessing pipeline.
    Runs all steps in order and saves cleaned data.
    """
    print("\n" + "="*60)
    print("STARTING DATA PREPROCESSING PIPELINE")
    print("="*60)

    # Step 1: Load
    df = load_data(raw_filepath)

    # Step 2: Inspect
    inspect_data(df)

    # Step 3: Handle missing values
    df = handle_missing_values(df)

    # Step 4: Remove duplicates
    df = remove_duplicates(df)

    # Step 5: Fix data types
    df = fix_data_types(df)

    # Step 6: Cap outliers
    print("\nCapping outliers...")
    df = cap_outliers(df, "sales_units")
    df = cap_outliers(df, "revenue")

    # Step 7: Sort by date
    df = df.sort_values(["store", "product", "date"]).reset_index(drop=True)
    print("\n✅ Data sorted by store, product, date")

    # Step 8: Save
    os.makedirs(os.path.dirname(processed_filepath), exist_ok=True)
    df.to_csv(processed_filepath, index=False)
    print(f"\n✅ Cleaned data saved to: {processed_filepath}")
    print(f"Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")

    return df


if __name__ == "__main__":
    df = preprocess_pipeline(
        raw_filepath="../data/raw/retail_sales_data.csv",
        processed_filepath="../data/processed/cleaned_data.csv"
    )