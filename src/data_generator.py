"""
data_generator.py
-----------------
Generates a synthetic retail sales dataset that mimics real-world
retail data from stores like D-Mart, Reliance Retail, or Walmart.

This gives us a realistic dataset without needing access to real company data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# ─── Configuration ────────────────────────────────────────────────────────────

np.random.seed(42)  # For reproducibility

STORES = ["Store_Mumbai", "Store_Delhi", "Store_Bangalore", "Store_Chennai", "Store_Hyderabad"]
CATEGORIES = ["Groceries", "Beverages", "Personal Care", "Dairy", "Snacks"]
PRODUCTS = {
    "Groceries":      ["Rice 5kg",    "Wheat Flour 5kg", "Toor Dal 1kg",   "Cooking Oil 1L"],
    "Beverages":      ["Coca Cola 2L","Mineral Water 1L","Orange Juice 1L","Green Tea 50pcs"],
    "Personal Care":  ["Shampoo 200ml","Toothpaste 100g","Soap Bar 100g",  "Face Wash 100ml"],
    "Dairy":          ["Milk 1L",     "Curd 500g",       "Butter 100g",    "Paneer 200g"],
    "Snacks":         ["Chips 100g",  "Biscuits 200g",   "Namkeen 250g",   "Popcorn 150g"],
}

# Base price per product
PRICES = {
    "Rice 5kg": 280, "Wheat Flour 5kg": 210, "Toor Dal 1kg": 120, "Cooking Oil 1L": 160,
    "Coca Cola 2L": 90, "Mineral Water 1L": 20, "Orange Juice 1L": 110, "Green Tea 50pcs": 130,
    "Shampoo 200ml": 180, "Toothpaste 100g": 70, "Soap Bar 100g": 35, "Face Wash 100ml": 120,
    "Milk 1L": 55, "Curd 500g": 40, "Butter 100g": 52, "Paneer 200g": 90,
    "Chips 100g": 20, "Biscuits 200g": 30, "Namkeen 250g": 45, "Popcorn 150g": 35,
}

# ─── Helper Functions ──────────────────────────────────────────────────────────

def apply_seasonality(date, category):
    """
    Adds realistic seasonal multipliers.
    - Beverages spike in summer (Apr-Jun)
    - Snacks spike during festivals (Oct-Nov = Diwali season)
    - Dairy is relatively stable
    - Groceries spike in festive months
    """
    month = date.month
    multipliers = {
        "Beverages":     {4: 1.5, 5: 1.7, 6: 1.6, 11: 1.2, 12: 1.1},
        "Snacks":        {10: 1.5, 11: 1.8, 12: 1.6, 1: 1.3},
        "Groceries":     {10: 1.3, 11: 1.4, 1: 1.2},
        "Personal Care": {7: 1.2, 8: 1.2},
        "Dairy":         {},
    }
    return multipliers.get(category, {}).get(month, 1.0)


def apply_weekend_effect(date):
    """Weekend sales are typically 20-35% higher."""
    return 1.3 if date.weekday() >= 5 else 1.0


def generate_dataset(start_date="2021-01-01", end_date="2024-01-01"):
    records = []
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    # Dictionary to track current stock for each (store, product)
    # Start with a full shelf (e.g., 500 units)
    current_inventory = {(s, p): 500 for s in STORES for cat in PRODUCTS for p in PRODUCTS[cat]}
    
    # Dictionary to track orders that are "in transit" (date_due: [(store, product, qty)])
    orders_in_transit = {}

    for date in date_range:
        # Check if any orders arrived today
        if date in orders_in_transit:
            for store, product, qty in orders_in_transit[date]:
                current_inventory[(store, product)] += qty

        for store in STORES:
            for category, products in PRODUCTS.items():
                for product in products:
                    base_price = PRICES[product]
                    season_mult = apply_seasonality(date, category)
                    weekend_mult = apply_weekend_effect(date)
                    store_mult = np.random.uniform(0.8, 1.3)

                    # Determine Demand
                    base_sales = np.random.randint(10, 80)
                    demand = int(base_sales * season_mult * weekend_mult * store_mult + np.random.normal(0, 5))
                    demand = max(0, demand)

                    # Inventory Logic
                    opening_stock = current_inventory[(store, product)]
                    sales_units = min(opening_stock, demand) # Can't sell more than you have
                    closing_stock = opening_stock - sales_units
                    current_inventory[(store, product)] = closing_stock
                    
                    stockout_flag = 1 if (demand > opening_stock) else 0
                    lead_time = int(np.random.choice([3, 5, 7]))

                    # TRIGGER REORDER: If stock is low and no order is already in transit
                    # (Simplified: ROP approx 400 for these items)
                    if closing_stock < 400:
                        arrival_date = date + timedelta(days=lead_time)
                        if arrival_date not in orders_in_transit:
                            orders_in_transit[arrival_date] = []
                        # Simulate ordering a batch (EOQ approx 1300)
                        orders_in_transit[arrival_date].append((store, product, 1300))

                    records.append({
                        "date": date,
                        "store": store,
                        "category": category,
                        "product": product,
                        "sales_units": sales_units,
                        "revenue": round(sales_units * base_price, 2),
                        "unit_price": base_price,
                        "opening_stock": opening_stock,
                        "closing_stock": closing_stock,
                        "stockout_flag": stockout_flag,
                        "lead_time_days": lead_time,
                    })

    df = pd.DataFrame(records)
    return df

# ─── Main Execution ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs("../data/raw", exist_ok=True)
    df = generate_dataset()
    output_path = "../data/raw/retail_sales_data.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✅ Saved to: {output_path}")
    print(df.head())
    print(f"\nDate range: {df['date'].min()} → {df['date'].max()}")
    print(f"Stores: {df['store'].unique()}")
    print(f"Products: {df['product'].nunique()}")