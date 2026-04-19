"""
inventory_optimization.py
--------------------------
Computes inventory KPIs using Operations Research formulas.

Formulas used:
1. Safety Stock  = Z × σ_demand × √(lead_time)
   - Z = service level factor (1.65 for 95% service level)
   - σ_demand = standard deviation of daily demand
   - lead_time = supplier delivery time in days

2. Reorder Point = (avg_daily_demand × lead_time) + safety_stock
   "Place an order when stock falls to this level"

3. EOQ (Economic Order Quantity) = √(2 × D × S / H)
   - D = annual demand
   - S = ordering cost per order
   - H = holding cost per unit per year
   "The optimal order quantity that minimizes total inventory cost"
"""

import pandas as pd
import numpy as np
import os


# ─── Constants ────────────────────────────────────────────────────────────────

# Service level factor (Z-score)
# 90% → 1.28 | 95% → 1.645 | 99% → 2.326
SERVICE_LEVEL_Z = 1.645  # 95% service level

# Cost assumptions (in INR, for simulation)
ORDERING_COST_PER_ORDER = 500     # Fixed cost to place one order (₹500)
HOLDING_COST_PER_UNIT_YEAR = 12   # Cost to hold one unit for one year (₹12)

# Stockout threshold: if current stock < reorder_point → alert
STOCKOUT_RISK_THRESHOLD = 0.8  # Flag when stock < 80% of reorder point


# ─── Core Formulas ────────────────────────────────────────────────────────────

def calculate_safety_stock(std_demand, lead_time, z=SERVICE_LEVEL_Z):
    """
    Safety Stock = Z × σ_demand × √(lead_time)
    
    Protects against demand variability during lead time.
    Higher std → more safety stock needed.
    Longer lead time → more safety stock needed.
    """
    return round(z * std_demand * np.sqrt(lead_time), 0)


def calculate_reorder_point(avg_daily_demand, lead_time, safety_stock):
    """
    Reorder Point = (avg_daily_demand × lead_time) + safety_stock
    
    This is the stock level at which you should place a new order,
    so it arrives before you run out of safety stock.
    """
    return round((avg_daily_demand * lead_time) + safety_stock, 0)


def calculate_eoq(annual_demand, ordering_cost=ORDERING_COST_PER_ORDER,
                  holding_cost=HOLDING_COST_PER_UNIT_YEAR):
    """
    Economic Order Quantity = √(2DS / H)
    
    The optimal quantity to order each time to minimize total cost.
    """
    if annual_demand <= 0 or holding_cost <= 0:
        return 0
    return round(np.sqrt((2 * annual_demand * ordering_cost) / holding_cost), 0)


def calculate_days_of_stock(current_stock, avg_daily_demand):
    """How many days will current stock last?"""
    if avg_daily_demand <= 0:
        return 999  # Infinite if no demand
    return round(current_stock / avg_daily_demand, 1)


# ─── Product-Level Inventory Table ────────────────────────────────────────────

def compute_inventory_metrics(df):
    """
    Aggregate sales data by product + store and compute all inventory KPIs.
    Updated to compare ROP against the LATEST stock instead of 3-year averages.
    """
    print("\nComputing inventory metrics per product-store...")

    # 1. Group by store + product and calculate demand statistics
    inventory_df = df.groupby(["store", "category", "product"]).agg(
        avg_daily_demand   = ("sales_units", "mean"),
        std_daily_demand   = ("sales_units", "std"),
        total_units_sold   = ("sales_units", "sum"),
        avg_closing_stock  = ("closing_stock", "mean"), # Still useful for historical context
        avg_lead_time      = ("lead_time_days", "mean"),
        stockout_days      = ("stockout_flag", "sum"),
        total_days_tracked = ("sales_units", "count"),
        avg_unit_price     = ("unit_price", "mean"),
        total_revenue      = ("revenue", "sum"),
    ).reset_index()

    # Fill NaN std and round demand
    inventory_df["std_daily_demand"] = inventory_df["std_daily_demand"].fillna(0)
    inventory_df["avg_daily_demand"] = inventory_df["avg_daily_demand"].round(1)
    inventory_df["avg_lead_time"]    = inventory_df["avg_lead_time"].round(0).astype(int)

    # 2. Calculate Base KPIs
    inventory_df["safety_stock"] = inventory_df.apply(
        lambda r: calculate_safety_stock(r["std_daily_demand"], r["avg_lead_time"]),
        axis=1
    )
    inventory_df["reorder_point"] = inventory_df.apply(
        lambda r: calculate_reorder_point(r["avg_daily_demand"], r["avg_lead_time"], r["safety_stock"]),
        axis=1
    )

    inventory_df["annual_demand"] = (inventory_df["avg_daily_demand"] * 365).round(0)
    inventory_df["eoq"] = inventory_df["annual_demand"].apply(calculate_eoq)

    # 3. GET CURRENT REALITY (The Fix)
    # Find the most recent date in the entire dataset
    latest_date = df['date'].max()
    
    # Filter for only the latest day's stock levels
    current_stock_snap = df[df['date'] == latest_date][['store', 'product', 'closing_stock']]
    current_stock_snap.columns = ['store', 'product', 'current_actual_stock']

    # Merge this 'current' snapshot into our main metrics table
    inventory_df = inventory_df.merge(current_stock_snap, on=['store', 'product'], how='left')

    # 4. Calculate Days of Stock using Current Stock, not Average
    inventory_df["days_of_stock_remaining"] = inventory_df.apply(
        lambda r: calculate_days_of_stock(r["current_actual_stock"], r["avg_daily_demand"]),
        axis=1
    )

    # Stockout rate remains based on history
    inventory_df["stockout_rate_pct"] = (
        inventory_df["stockout_days"] / inventory_df["total_days_tracked"] * 100
    ).round(2)

    # 5. Inventory status (Logic now looks at 'current_actual_stock')
    inventory_df["inventory_status"] = inventory_df.apply(
        lambda r: classify_inventory_status_logic(r["current_actual_stock"], r["reorder_point"], r["safety_stock"]), 
        axis=1
    )

    # 6. Reorder alert (Logic now looks at 'current_actual_stock')
    inventory_df["reorder_alert"] = (
        inventory_df["current_actual_stock"] <= inventory_df["reorder_point"]
    ).map({True: "🔴 ORDER NOW", False: "✅ STABLE"})

    # 7. Recommended order quantity
    inventory_df["recommended_order_qty"] = inventory_df.apply(
        lambda r: int(r["eoq"]) if r["reorder_alert"] == "🔴 ORDER NOW" else 0,
        axis=1
    )

    print(f"✅ Computed metrics for {len(inventory_df):,} product-store combinations")
    return inventory_df

def classify_inventory_status_logic(stock, reorder, safety):
    """Refined classification based on current stock levels."""
    if stock <= safety:
        return "🔴 Critical"
    elif stock <= reorder:
        return "🟠 Low"
    elif stock <= reorder * 1.5:
        return "🟢 Healthy"
    else:
        return "🔵 Overstock"

# ─── Summary Statistics ───────────────────────────────────────────────────────

def print_inventory_summary(inv_df):
    """Print a high-level business summary."""
    print("\n" + "="*60)
    print("INVENTORY OPTIMIZATION SUMMARY")
    print("="*60)

    status_counts = inv_df["inventory_status"].value_counts()
    print("\nInventory Status Distribution:")
    for status, count in status_counts.items():
        print(f"  {status}: {count} products")

    alerts = inv_df[inv_df["reorder_alert"] == "🔴 ORDER NOW"]
    print(f"\n⚠️  Products needing immediate reorder: {len(alerts)}")
    print(f"   Total recommended order value (₹): "
          f"{(alerts['recommended_order_qty'] * alerts['avg_unit_price']).sum():,.0f}")

    print(f"\nTop 5 products by stockout rate:")
    top_stockout = inv_df.nlargest(5, "stockout_rate_pct")[
        ["product", "store", "stockout_rate_pct", "inventory_status"]
    ]
    print(top_stockout.to_string(index=False))

    print(f"\nTop 5 products by revenue:")
    top_revenue = inv_df.nlargest(5, "total_revenue")[
        ["product", "store", "total_revenue", "avg_daily_demand"]
    ]
    print(top_revenue.to_string(index=False))


# ─── Pipeline ─────────────────────────────────────────────────────────────────

def inventory_pipeline(
    cleaned_filepath="../data/processed/cleaned_data.csv",
    output_dir="../outputs/inventory/",
):
    print("\n" + "="*60)
    print("STARTING INVENTORY OPTIMIZATION PIPELINE")
    print("="*60)

    df = pd.read_csv(cleaned_filepath, parse_dates=["date"])
    print(f"Loaded: {df.shape[0]:,} rows")

    inv_df = compute_inventory_metrics(df)
    print_inventory_summary(inv_df)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "reorder_recommendations.csv")
    inv_df.to_csv(output_path, index=False)
    print(f"\n✅ Reorder recommendations saved to: {output_path}")

    return inv_df


if __name__ == "__main__":
    inv_df = inventory_pipeline()
    print("\nSample output:")
    print(inv_df[["store","product","avg_daily_demand","safety_stock",
                   "reorder_point","eoq","inventory_status","reorder_alert"]].head(10))