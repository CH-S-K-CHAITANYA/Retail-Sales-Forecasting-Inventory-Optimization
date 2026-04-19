"""
feature_engineering.py
-----------------------
Creates ML-ready features from cleaned retail data.

Key features created:
1. Time features (month, day, weekday, quarter)
2. Lag features (past sales values — tells model what happened before)
3. Rolling averages (smoothed demand signal)
4. Seasonal and holiday flags
5. Price change indicator
"""

import pandas as pd
import numpy as np
import os


def add_time_features(df):
    """Extract date-based features useful for capturing seasonality."""
    print("Adding time features...")
    df["year"]       = df["date"].dt.year
    df["month"]      = df["date"].dt.month
    df["day"]        = df["date"].dt.day
    df["dayofweek"]  = df["date"].dt.dayofweek       # 0=Monday, 6=Sunday
    df["quarter"]    = df["date"].dt.quarter
    df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)  # 1 if Sat/Sun

    # Is it start of month? (grocery shopping spike)
    df["is_month_start"] = (df["day"] <= 5).astype(int)

    # Is it month end?
    df["is_month_end"] = (df["day"] >= 25).astype(int)

    print("  ✅ Year, Month, Day, DayOfWeek, Quarter, WeekOfYear, Is_Weekend added")
    return df


def add_festival_flags(df):
    """
    Add Indian festival/holiday flags that drive retail spikes.
    (Approximate dates for simulation — adjust for actual years)
    """
    print("Adding festival flags...")

    festival_months = {
        10: "Navratri",
        11: "Diwali",
        12: "Christmas",
        1:  "New_Year",
        8:  "Independence_Day",
        3:  "Holi",
    }

    # Simple flag: is this a festival month?
    df["is_festival_month"] = df["month"].apply(
        lambda m: 1 if m in festival_months.keys() else 0
    )
    print("  ✅ Festival month flag added (Oct=Navratri, Nov=Diwali, etc.)")
    return df


def add_lag_features(df, lag_days=[7, 14, 21, 30]):
    """
    Lag features: sales from N days ago.
    
    Why? The model needs to 'see' past values to predict future ones.
    For example: 'What was sales 7 days ago? 30 days ago?'
    
    IMPORTANT: Must group by store + product to avoid data leakage
    between different product-store combinations.
    """
    print(f"Adding lag features for {lag_days} days...")
    df = df.sort_values(["store", "product", "date"])

    for lag in lag_days:
        col_name = f"sales_lag_{lag}"
        df[col_name] = df.groupby(["store", "product"])["sales_units"].shift(lag)
        print(f"  ✅ {col_name} created")

    return df


def add_rolling_features(df, windows=[7, 14, 30]):
    """
    Rolling mean and std of sales.
    
    Rolling mean: average sales over past N days → smoothed trend signal
    Rolling std:  variability of sales → captures demand volatility
    """
    print(f"Adding rolling window features for {windows} days...")
    df = df.sort_values(["store", "product", "date"])

    for window in windows:
        mean_col = f"rolling_mean_{window}"
        std_col  = f"rolling_std_{window}"
        df[mean_col] = df.groupby(["store", "product"])["sales_units"].transform(
            lambda x: x.shift(1).rolling(window=window, min_periods=1).mean()
        )
        df[std_col] = df.groupby(["store", "product"])["sales_units"].transform(
            lambda x: x.shift(1).rolling(window=window, min_periods=1).std().fillna(0)
        )
        print(f"  ✅ {mean_col}, {std_col} created")

    return df


def add_price_features(df):
    """
    Price-based features.
    
    Demand is often affected by price changes (price elasticity).
    If price drops → demand typically increases.
    """
    print("Adding price features...")

    # Price change from previous day
    df["price_change"] = df.groupby(["store", "product"])["unit_price"].diff().fillna(0)

    # Flag for promotion/discount day (price drop > 5%)
    df["is_promotion"] = (df["price_change"] < -df["unit_price"] * 0.05).astype(int)

    print("  ✅ Price change and promotion flag added")
    return df


def encode_categoricals(df):
    """
    Convert categorical text columns to numeric codes.
    ML models need numbers, not text.
    """
    print("Encoding categorical columns...")
    df["store_encoded"]    = df["store"].astype("category").cat.codes
    df["category_encoded"] = df["category"].astype("category").cat.codes
    df["product_encoded"]  = df["product"].astype("category").cat.codes
    print("  ✅ Store, Category, Product encoded as integer codes")
    return df


def feature_engineering_pipeline(cleaned_filepath, featured_filepath):
    """
    Full feature engineering pipeline.
    """
    print("\n" + "="*60)
    print("STARTING FEATURE ENGINEERING PIPELINE")
    print("="*60)

    df = pd.read_csv(cleaned_filepath, parse_dates=["date"])
    print(f"Loaded: {df.shape[0]:,} rows")

    df = add_time_features(df)
    df = add_festival_flags(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_price_features(df)
    df = encode_categoricals(df)

    # Drop rows with NaN (created by lag features for initial days)
    before = len(df)
    df = df.dropna()
    print(f"\nRows dropped due to NaN from lag features: {before - len(df):,}")
    print(f"Final feature dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

    os.makedirs(os.path.dirname(featured_filepath), exist_ok=True)
    df.to_csv(featured_filepath, index=False)
    print(f"\n✅ Featured data saved to: {featured_filepath}")

    return df


if __name__ == "__main__":
    df = feature_engineering_pipeline(
        cleaned_filepath="../data/processed/cleaned_data.csv",
        featured_filepath="../data/processed/featured_data.csv"
    )
    print("\nFeature columns created:")
    print([c for c in df.columns if c not in ["date","store","category","product"]])