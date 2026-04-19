"""
main.py
-------
Entry point for the Retail Sales Forecasting & Inventory Optimization System.
Runs the complete pipeline in sequence.

Usage:
    python main.py
"""

import os
import sys
import time

print("="*70)
print("  RETAIL SALES FORECASTING & INVENTORY OPTIMIZATION SYSTEM")
print("  By: CH S K CHAITANYA | Python + XGBoost + Taipy")
print("="*70)

# ─── Ensure src is in path ────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_generator        import generate_dataset
from data_preprocessing    import preprocess_pipeline
from feature_engineering   import feature_engineering_pipeline
from forecasting           import forecasting_pipeline
from inventory_optimization import inventory_pipeline
from visualization         import generate_all_eda_charts
import pandas as pd


def main():
    start_time = time.time()

    # ── Step 1: Generate Synthetic Dataset ────────────────────────────────────
    print("\n[STEP 1/6] Generating synthetic retail dataset...")
    raw_path = "data/raw/retail_sales_data.csv"
    if not os.path.exists(raw_path):
        os.makedirs("data/raw", exist_ok=True)
        df_raw = generate_dataset(start_date="2021-01-01", end_date="2024-01-01")
        df_raw.to_csv(raw_path, index=False)
        print(f"  Dataset saved: {raw_path}")
    else:
        print(f"  Dataset already exists: {raw_path} (skipping generation)")

    # ── Step 2: Preprocessing ─────────────────────────────────────────────────
    print("\n[STEP 2/6] Running data preprocessing...")
    df_clean = preprocess_pipeline(
        raw_filepath=raw_path,
        processed_filepath="data/processed/cleaned_data.csv"
    )

    # ── Step 3: Feature Engineering ───────────────────────────────────────────
    print("\n[STEP 3/6] Engineering features...")
    df_featured = feature_engineering_pipeline(
        cleaned_filepath="data/processed/cleaned_data.csv",
        featured_filepath="data/processed/featured_data.csv"
    )

    # ── Step 4: Forecasting ───────────────────────────────────────────────────
    print("\n[STEP 4/6] Training forecasting models...")
    xgb_model, rf_model, forecast_results = forecasting_pipeline(
        featured_filepath="data/processed/featured_data.csv",
        model_dir="models/",
        output_dir="outputs/forecasts/",
        eda_dir="outputs/eda/",
    )

    # ── Step 5: Inventory Optimization ────────────────────────────────────────
    print("\n[STEP 5/6] Computing inventory optimization...")
    inv_df = inventory_pipeline(
        cleaned_filepath="data/processed/cleaned_data.csv",
        output_dir="outputs/inventory/"
    )

    # ── Step 6: Visualizations ────────────────────────────────────────────────
    print("\n[STEP 6/6] Generating all charts and visualizations...")
    df_clean = pd.read_csv("data/processed/cleaned_data.csv", parse_dates=["date"])
    generate_all_eda_charts(df_clean, inv_df, output_dir="outputs/eda/")

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    print("\n" + "="*70)
    print("✅  PIPELINE COMPLETE!")
    print(f"   Total time: {elapsed:.1f} seconds")
    print("\n   Output files:")
    print("   → data/processed/cleaned_data.csv")
    print("   → data/processed/featured_data.csv")
    print("   → models/xgboost_model.pkl")
    print("   → outputs/forecasts/forecast_results.csv")
    print("   → outputs/inventory/reorder_recommendations.csv")
    print("   → outputs/eda/  (10 charts)")
    print("\n   Next: Run the Taipy dashboard:")
    print("   → python app/dashboard.py")
    print("="*70)


if __name__ == "__main__":
    main()