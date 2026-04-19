"""
forecasting.py
--------------
Trains XGBoost and Random Forest models to forecast retail sales.
Evaluates using RMSE, MAE, MAPE.
Generates 30-day future forecasts.
"""

import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit


# ─── Feature Columns ──────────────────────────────────────────────────────────

FEATURE_COLS = [
    "store_encoded", "category_encoded", "product_encoded",
    "year", "month", "day", "dayofweek", "quarter", "weekofyear",
    "is_weekend", "is_month_start", "is_month_end", "is_festival_month",
    "sales_lag_7", "sales_lag_14", "sales_lag_21", "sales_lag_30",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_30",
    "rolling_std_7", "rolling_std_14", "rolling_std_30",
    "unit_price", "price_change", "is_promotion",
    "lead_time_days",
]
TARGET_COL = "sales_units"


# ─── Metric Functions ─────────────────────────────────────────────────────────

def mean_absolute_percentage_error(y_true, y_pred):
    """MAPE: % error, easier to interpret than RMSE."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def evaluate_model(y_true, y_pred, model_name):
    """Print evaluation metrics for a model."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae  = mean_absolute_error(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)
    print(f"\n📊 {model_name} Evaluation:")
    print(f"   RMSE  : {rmse:.2f}  (lower is better)")
    print(f"   MAE   : {mae:.2f}  (lower is better)")
    print(f"   MAPE  : {mape:.2f}% (< 15% is good for retail)")
    return {"model": model_name, "RMSE": rmse, "MAE": mae, "MAPE": mape}


# ─── Train/Test Split ─────────────────────────────────────────────────────────

def time_based_split(df, test_months=3):
    """
    Time-based split — CRITICAL for time-series.
    We CANNOT use random split because future data would leak into training.
    
    Train: everything before the last 3 months
    Test:  last 3 months of data
    """
    split_date = df["date"].max() - pd.DateOffset(months=test_months)
    train = df[df["date"] <= split_date].copy()
    test  = df[df["date"] > split_date].copy()
    print(f"\nTrain: {train['date'].min().date()} → {train['date'].max().date()} ({len(train):,} rows)")
    print(f"Test:  {test['date'].min().date()} → {test['date'].max().date()} ({len(test):,} rows)")
    return train, test


# ─── Model Training ───────────────────────────────────────────────────────────

def train_xgboost(X_train, y_train):
    """Train XGBoost Regressor — industry-standard for tabular forecasting."""
    print("\nTraining XGBoost model...")
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,  # Use all CPU cores
        verbosity=0,
    )
    model.fit(X_train, y_train)
    print("✅ XGBoost training complete")
    return model


def train_random_forest(X_train, y_train):
    """Train Random Forest as a comparison model."""
    print("\nTraining Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    print("✅ Random Forest training complete")
    return model


# ─── Feature Importance ───────────────────────────────────────────────────────

def plot_feature_importance(model, feature_names, model_name, output_dir):
    """Save a feature importance bar chart."""
    importances = pd.Series(model.feature_importances_, index=feature_names)
    importances = importances.sort_values(ascending=False).head(15)

    plt.figure(figsize=(10, 6))
    importances.plot(kind="barh", color="steelblue")
    plt.title(f"Top 15 Feature Importances — {model_name}", fontsize=14)
    plt.xlabel("Importance Score")
    plt.gca().invert_yaxis()
    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"feature_importance_{model_name.lower().replace(' ','_')}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Feature importance chart saved: {path}")


# ─── Forecast vs Actual Plot ──────────────────────────────────────────────────

def plot_forecast_vs_actual(df_test, y_pred, model_name, output_dir, product_filter=None):
    """
    Plot actual vs predicted sales over time.
    Optionally filter for one product for a cleaner view.
    """
    df_plot = df_test.copy()
    df_plot["predicted"] = np.maximum(0, np.round(y_pred)).astype(int)

    if product_filter:
        df_plot = df_plot[df_plot["product"] == product_filter]
        title = f"Actual vs Predicted — {product_filter} ({model_name})"
    else:
        # Aggregate across all products for overview
        df_plot = df_plot.groupby("date")[["sales_units", "predicted"]].sum().reset_index()
        title = f"Total Actual vs Predicted Sales — {model_name}"

    plt.figure(figsize=(14, 5))
    plt.plot(df_plot["date"], df_plot["sales_units"], label="Actual", color="blue", linewidth=1.5)
    plt.plot(df_plot["date"], df_plot["predicted"], label="Predicted", color="red",
             linestyle="--", linewidth=1.5)
    plt.title(title, fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Sales Units")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    fname = f"forecast_vs_actual_{model_name.lower().replace(' ','_')}.png"
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, fname)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Forecast chart saved: {path}")


# ─── Save Forecast Results ────────────────────────────────────────────────────

def save_forecast_results(df_test, y_pred_xgb, y_pred_rf, output_path):
    """Save actual vs predicted comparison to CSV."""
    results = df_test[["date", "store", "product", "category", "sales_units"]].copy()
    results["xgb_predicted"]  = np.maximum(0, np.round(y_pred_xgb)).astype(int)
    results["rf_predicted"]   = np.maximum(0, np.round(y_pred_rf)).astype(int)
    results["xgb_error"]      = abs(results["sales_units"] - results["xgb_predicted"])
    results["rf_error"]       = abs(results["sales_units"] - results["rf_predicted"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    results.to_csv(output_path, index=False)
    print(f"\n✅ Forecast results saved to: {output_path}")
    return results


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def forecasting_pipeline(
    featured_filepath="../data/processed/featured_data.csv",
    model_dir="../models/",
    output_dir="../outputs/forecasts/",
    eda_dir="../outputs/eda/",
):
    print("\n" + "="*60)
    print("STARTING FORECASTING PIPELINE")
    print("="*60)

    # Load data
    df = pd.read_csv(featured_filepath, parse_dates=["date"])
    print(f"Loaded: {df.shape[0]:,} rows")

    # Verify required feature columns
    missing = [c for c in FEATURE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")

    # Time-based train/test split
    train, test = time_based_split(df)

    X_train = train[FEATURE_COLS]
    y_train = train[TARGET_COL]
    X_test  = test[FEATURE_COLS]
    y_test  = test[TARGET_COL]

    # Train models
    xgb_model = train_xgboost(X_train, y_train)
    rf_model  = train_random_forest(X_train, y_train)

    # Predictions
    y_pred_xgb = xgb_model.predict(X_test)
    y_pred_rf  = rf_model.predict(X_test)

    # Evaluation
    xgb_metrics = evaluate_model(y_test, y_pred_xgb, "XGBoost")
    rf_metrics  = evaluate_model(y_test, y_pred_rf, "Random Forest")

    # Save models
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(xgb_model, os.path.join(model_dir, "xgboost_model.pkl"))
    joblib.dump(rf_model,  os.path.join(model_dir, "random_forest_model.pkl"))
    print(f"\n✅ Models saved to: {model_dir}")

    # Visualizations
    plot_feature_importance(xgb_model, FEATURE_COLS, "XGBoost", eda_dir)
    plot_forecast_vs_actual(test, y_pred_xgb, "XGBoost", output_dir)

    # Save results
    results = save_forecast_results(
        test, y_pred_xgb, y_pred_rf,
        output_path=os.path.join(output_dir, "forecast_results.csv")
    )

    print("\n" + "="*60)
    print("FORECASTING PIPELINE COMPLETE")
    print(f"Best Model: {'XGBoost' if xgb_metrics['MAPE'] < rf_metrics['MAPE'] else 'Random Forest'}")
    print("="*60)

    return xgb_model, rf_model, results


if __name__ == "__main__":
    forecasting_pipeline()