"""
visualization.py
----------------
Generates all EDA charts and insight plots.
Saves all figures to outputs/eda/ for GitHub documentation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# Style
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "font.size":        11,
})
sns.set_palette("husl")

# Removed the ../ so it stays inside the project folder
OUTPUT_DIR = "outputs/eda/"

def ensure_output_dir(directory=None):
    if directory is None:
        directory = OUTPUT_DIR
    os.makedirs(directory, exist_ok=True)

def save_fig(filename, dpi=150, output_dir=None):
    # This prevents Python's default argument trap
    if output_dir is None:
        output_dir = OUTPUT_DIR
    
    path = os.path.join(output_dir, filename)
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"  ✅ Saved: {path}")
# ─── Plot 1: Monthly Sales Trend ──────────────────────────────────────────────

def plot_monthly_sales_trend(df):
    """Overall monthly revenue trend — shows seasonality clearly."""
    print("Generating monthly sales trend...")
    monthly = df.copy()
    monthly["year_month"] = monthly["date"].dt.to_period("M")
    monthly_agg = monthly.groupby("year_month")["revenue"].sum().reset_index()
    monthly_agg["year_month"] = monthly_agg["year_month"].astype(str)

    plt.figure(figsize=(16, 5))
    plt.plot(monthly_agg["year_month"], monthly_agg["revenue"],
             marker="o", color="steelblue", linewidth=2, markersize=4)
    plt.fill_between(monthly_agg["year_month"], monthly_agg["revenue"], alpha=0.15, color="steelblue")
    plt.title("Monthly Total Revenue Trend", fontsize=16, fontweight="bold")
    plt.xlabel("Month")
    plt.ylabel("Revenue (₹)")
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    plt.grid(alpha=0.3)
    save_fig("01_monthly_sales_trend.png")


# ─── Plot 2: Category-Wise Sales ──────────────────────────────────────────────

def plot_category_sales(df):
    """Bar chart of total sales by category."""
    print("Generating category-wise sales chart...")
    cat_sales = df.groupby("category")["revenue"].sum().sort_values(ascending=False)

    plt.figure(figsize=(10, 5))
    bars = plt.bar(cat_sales.index, cat_sales.values, color=sns.color_palette("husl", len(cat_sales)))
    plt.title("Total Revenue by Category", fontsize=15, fontweight="bold")
    plt.xlabel("Category")
    plt.ylabel("Revenue (₹)")
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    # Add value labels on bars
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h * 1.01,
                 f"₹{h/1e6:.1f}M", ha="center", va="bottom", fontsize=9)
    plt.grid(axis="y", alpha=0.3)
    save_fig("02_category_sales.png")


# ─── Plot 3: Store-Wise Performance ───────────────────────────────────────────

def plot_store_performance(df):
    """Compare performance across stores."""
    print("Generating store performance chart...")
    store_sales = df.groupby("store")["revenue"].sum().sort_values(ascending=True)

    plt.figure(figsize=(10, 5))
    store_sales.plot(kind="barh", color="coral")
    plt.title("Revenue by Store", fontsize=15, fontweight="bold")
    plt.xlabel("Revenue (₹)")
    plt.gca().xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    plt.grid(axis="x", alpha=0.3)
    save_fig("03_store_performance.png")


# ─── Plot 4: Daily Sales Distribution ─────────────────────────────────────────

def plot_daily_sales_distribution(df):
    """Histogram of daily sales units per product."""
    print("Generating sales distribution chart...")
    plt.figure(figsize=(10, 5))
    sns.histplot(df["sales_units"], bins=50, kde=True, color="mediumseagreen")
    plt.title("Distribution of Daily Sales Units", fontsize=15, fontweight="bold")
    plt.xlabel("Sales Units")
    plt.ylabel("Frequency")
    plt.grid(alpha=0.3)
    save_fig("04_sales_distribution.png")


# ─── Plot 5: Weekday vs Weekend Sales ─────────────────────────────────────────

def plot_weekday_weekend(df):
    """Compare weekday vs weekend sales."""
    print("Generating weekday vs weekend chart...")
    df = df.copy()
    df["day_type"] = df["date"].dt.dayofweek.apply(lambda x: "Weekend" if x >= 5 else "Weekday")
    day_sales = df.groupby("day_type")["sales_units"].mean()

    plt.figure(figsize=(7, 5))
    bars = plt.bar(day_sales.index, day_sales.values,
                   color=["steelblue", "tomato"], edgecolor="white")
    plt.title("Average Daily Sales: Weekday vs Weekend", fontsize=14, fontweight="bold")
    plt.ylabel("Avg Sales Units")
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h * 1.01,
                 f"{h:.1f}", ha="center", va="bottom")
    plt.grid(axis="y", alpha=0.3)
    save_fig("05_weekday_vs_weekend.png")


# ─── Plot 6: Seasonal Monthly Heatmap ─────────────────────────────────────────

def plot_monthly_heatmap(df):
    """Heatmap of average sales by month and category."""
    print("Generating monthly seasonality heatmap...")
    df = df.copy()
    df["month"] = df["date"].dt.month
    pivot = df.pivot_table(
        values="sales_units", index="category", columns="month", aggfunc="mean"
    )
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"][:len(pivot.columns)]

    plt.figure(figsize=(14, 5))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", linewidths=0.5)
    plt.title("Avg Daily Sales by Category and Month (Seasonality Heatmap)",
              fontsize=14, fontweight="bold")
    plt.ylabel("Category")
    plt.xlabel("Month")
    save_fig("06_seasonality_heatmap.png")


# ─── Plot 7: Top 10 Products by Revenue ───────────────────────────────────────

def plot_top_products(df):
    """Bar chart of top 10 products by total revenue."""
    print("Generating top products chart...")
    top_products = df.groupby("product")["revenue"].sum().nlargest(10).sort_values()

    plt.figure(figsize=(10, 6))
    top_products.plot(kind="barh", color="mediumpurple")
    plt.title("Top 10 Products by Total Revenue", fontsize=14, fontweight="bold")
    plt.xlabel("Revenue (₹)")
    plt.gca().xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    plt.grid(axis="x", alpha=0.3)
    save_fig("07_top_products.png")


# ─── Plot 8: Correlation Heatmap ──────────────────────────────────────────────

def plot_correlation_heatmap(df):
    """Correlation between numerical features."""
    print("Generating correlation heatmap...")
    num_cols = ["sales_units", "revenue", "unit_price", "opening_stock",
                "closing_stock", "lead_time_days"]
    corr = df[num_cols].corr()

    plt.figure(figsize=(9, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, square=True, linewidths=0.5)
    plt.title("Correlation Heatmap — Numerical Features", fontsize=14, fontweight="bold")
    save_fig("08_correlation_heatmap.png")


# ─── Plot 9: Stockout Analysis ────────────────────────────────────────────────

def plot_stockout_by_category(df):
    """Stockout rate by category — shows supply chain risk."""
    print("Generating stockout analysis chart...")
    stockout = df.groupby("category")["stockout_flag"].mean() * 100

    plt.figure(figsize=(9, 5))
    bars = plt.bar(stockout.index, stockout.values,
                   color=["red" if v > 5 else "orange" if v > 2 else "green"
                          for v in stockout.values])
    plt.title("Stockout Rate by Category (%)", fontsize=14, fontweight="bold")
    plt.ylabel("Stockout Rate (%)")
    plt.axhline(y=5, color="red", linestyle="--", alpha=0.5, label="5% threshold")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 0.1,
                 f"{h:.1f}%", ha="center", va="bottom")
    save_fig("09_stockout_by_category.png")


# ─── Plot 10: Inventory Status Distribution ───────────────────────────────────

def plot_inventory_status(inv_df):
    """Pie chart of inventory health status."""
    print("Generating inventory status pie chart...")
    status_counts = inv_df["inventory_status"].value_counts()

    colors = {
        "🔴 Critical": "#e74c3c",
        "🟠 Low":      "#f39c12",
        "🟢 Optimal":  "#2ecc71",
        "🔵 Overstock": "#3498db",
    }
    chart_colors = [colors.get(s, "gray") for s in status_counts.index]

    plt.figure(figsize=(8, 6))
    wedges, texts, autotexts = plt.pie(
        status_counts.values,
        labels=status_counts.index,
        autopct="%1.1f%%",
        colors=chart_colors,
        startangle=140,
        wedgeprops=dict(edgecolor="white", linewidth=2),
    )
    plt.title("Inventory Health Status Distribution", fontsize=14, fontweight="bold")
    save_fig("10_inventory_status_pie.png")


# ─── Run All Charts ───────────────────────────────────────────────────────────

def generate_all_eda_charts(df, inv_df=None, output_dir=OUTPUT_DIR):
    """Generate all charts in sequence."""
    global OUTPUT_DIR
    OUTPUT_DIR = output_dir
    ensure_output_dir(output_dir)

    print("\n" + "="*60)
    print("GENERATING ALL EDA & VISUALIZATION CHARTS")
    print("="*60)

    plot_monthly_sales_trend(df)
    plot_category_sales(df)
    plot_store_performance(df)
    plot_daily_sales_distribution(df)
    plot_weekday_weekend(df)
    plot_monthly_heatmap(df)
    plot_top_products(df)
    plot_correlation_heatmap(df)
    plot_stockout_by_category(df)

    if inv_df is not None:
        plot_inventory_status(inv_df)

    print(f"\n✅ All charts saved to: {output_dir}")


if __name__ == "__main__":
    df = pd.read_csv("../data/processed/cleaned_data.csv", parse_dates=["date"])
    inv_df = pd.read_csv("../outputs/inventory/reorder_recommendations.csv")
    generate_all_eda_charts(df, inv_df)