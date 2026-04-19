"""
dashboard.py — Modern Industry-Grade Streamlit Dashboard
=========================================================
Aesthetic: Dark "Command Center" — Bloomberg Terminal meets modern SaaS.
Palette  : Deep navy base · Electric cyan accent · Emerald green positive
           · Amber warning · Crimson alert
Charts   : Fully dark-themed Plotly with vibrant traces
Layout   : Glassmorphism cards · Dense data grid · Clean sidebar

Run:
    streamlit run app/dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG  ── must be the very first Streamlit call
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="RetailIQ · Analytics",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS  ── dark command-center theme
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ── CSS Variables ── */
:root {
    --bg-base:      #070b14;
    --bg-surface:   #0d1526;
    --bg-elevated:  #111d35;
    --bg-card:      rgba(17, 29, 53, 0.85);
    --border:       rgba(0, 212, 255, 0.12);
    --border-hover: rgba(0, 212, 255, 0.35);
    --cyan:         #00d4ff;
    --cyan-dim:     rgba(0, 212, 255, 0.15);
    --cyan-glow:    rgba(0, 212, 255, 0.08);
    --emerald:      #00e5a0;
    --emerald-dim:  rgba(0, 229, 160, 0.12);
    --amber:        #ffb547;
    --amber-dim:    rgba(255, 181, 71, 0.12);
    --crimson:      #ff4d6a;
    --crimson-dim:  rgba(255, 77, 106, 0.12);
    --violet:       #a78bfa;
    --violet-dim:   rgba(167, 139, 250, 0.12);
    --text-primary: #e8f0fe;
    --text-secondary: #7a8bb0;
    --text-muted:   #3d5070;
    --font-display: 'Syne', sans-serif;
    --font-body:    'Inter', sans-serif;
    --font-mono:    'DM Mono', monospace;
    --radius:       12px;
    --radius-lg:    18px;
    --shadow:       0 4px 24px rgba(0,0,0,0.4);
    --shadow-glow:  0 0 30px rgba(0,212,255,0.08);
}

/* ── Base Reset ── */
html, body, [class*="css"] {
    font-family: var(--font-body);
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
}

/* Animated grid background on main area */
.main > div:first-child {
    background:
        linear-gradient(rgba(0,212,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.025) 1px, transparent 1px),
        var(--bg-base);
    background-size: 40px 40px;
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d1a 0%, #0a1220 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] label {
    color: var(--text-secondary) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    font-family: var(--font-mono) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.stDeployButton { display: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-hover); border-radius: 10px; }

/* ── Top nav bar ── */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 8px 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
}
.top-bar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
}
.logo-hex {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--cyan), #0066ff);
    clip-path: polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 800;
    box-shadow: 0 0 20px rgba(0,212,255,0.4);
    animation: pulse-glow 3s ease-in-out infinite;
}
@keyframes pulse-glow {
    0%,100% { box-shadow: 0 0 20px rgba(0,212,255,0.3); }
    50%      { box-shadow: 0 0 35px rgba(0,212,255,0.6); }
}
.logo-text {
    font-family: var(--font-display);
    font-size: 22px; font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, var(--cyan), #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.logo-sub {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.status-pill {
    display: flex; align-items: center; gap: 8px;
    background: var(--emerald-dim);
    border: 1px solid rgba(0,229,160,0.25);
    border-radius: 20px;
    padding: 6px 14px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--emerald);
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--emerald);
    box-shadow: 0 0 8px var(--emerald);
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity: 1; } 50% { opacity: 0.3; }
}

/* ── Section Headers ── */
.section-label {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
    color: var(--cyan);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.section-title {
    font-family: var(--font-display);
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title::before {
    content: '';
    width: 3px; height: 20px;
    background: linear-gradient(180deg, var(--cyan), transparent);
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    transition: border-color 0.25s, transform 0.2s, box-shadow 0.25s;
    cursor: default;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
.kpi-card:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-glow);
}
.kpi-card.cyan::before  { background: linear-gradient(90deg, var(--cyan), transparent); }
.kpi-card.emerald::before { background: linear-gradient(90deg, var(--emerald), transparent); }
.kpi-card.amber::before { background: linear-gradient(90deg, var(--amber), transparent); }
.kpi-card.crimson::before { background: linear-gradient(90deg, var(--crimson), transparent); }
.kpi-card.violet::before { background: linear-gradient(90deg, var(--violet), transparent); }
.kpi-card.blue::before  { background: linear-gradient(90deg, #4d9fff, transparent); }

.kpi-icon {
    font-size: 20px;
    margin-bottom: 12px;
    display: block;
}
.kpi-label {
    font-family: var(--font-mono);
    font-size: 9.5px;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: var(--font-display);
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 8px;
    letter-spacing: -1px;
}
.kpi-card.cyan   .kpi-value { color: var(--cyan); }
.kpi-card.emerald .kpi-value { color: var(--emerald); }
.kpi-card.amber  .kpi-value { color: var(--amber); }
.kpi-card.crimson .kpi-value { color: var(--crimson); }
.kpi-card.violet .kpi-value { color: var(--violet); }
.kpi-card.blue   .kpi-value { color: #4d9fff; }
.kpi-delta {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 4px;
}
.kpi-bg-icon {
    position: absolute;
    right: 16px; bottom: 12px;
    font-size: 48px;
    opacity: 0.05;
    line-height: 1;
}

/* ── Chart containers ── */
.chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 24px;
    backdrop-filter: blur(12px);
    transition: border-color 0.25s;
    margin-bottom: 20px;
}
.chart-card:hover { border-color: var(--border-hover); }

/* ── Table styling ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    background: var(--bg-surface) !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-elevated) !important;
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 12px 14px !important;
}
[data-testid="stDataFrame"] td {
    background: transparent !important;
    color: var(--text-primary) !important;
    font-family: var(--font-mono) !important;
    font-size: 12px !important;
    border-bottom: 1px solid rgba(0,212,255,0.05) !important;
    padding: 10px 14px !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: var(--cyan-glow) !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] > div > div > div {
    background: linear-gradient(90deg, var(--cyan), #0066ff) !important;
}
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    background: var(--bg-elevated) !important;
    color: var(--cyan) !important;
    font-family: var(--font-mono) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--cyan) 0%, #0066ff 100%) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.03em !important;
    padding: 10px 28px !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 0 30px rgba(0,212,255,0.45) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: var(--cyan) !important;
    border: 1px solid var(--border-hover) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: var(--cyan-dim) !important;
    border-color: var(--cyan) !important;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label {
    color: var(--text-secondary) !important;
    font-family: var(--font-mono) !important;
    font-size: 12px !important;
}

/* ── Info / Success / Error alerts ── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border: 1px solid !important;
    font-family: var(--font-mono) !important;
    font-size: 12px !important;
}
div[data-baseweb="notification"][kind="info"] {
    background: var(--cyan-dim) !important;
    border-color: rgba(0,212,255,0.3) !important;
}
div[data-baseweb="notification"][kind="success"] {
    background: var(--emerald-dim) !important;
    border-color: rgba(0,229,160,0.3) !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 28px 0 !important;
}

/* ── Date input ── */
[data-testid="stDateInput"] input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-size: 12px !important;
}

/* ── Simulation result card ── */
.sim-metric {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 12px;
}
.sim-metric-label {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 6px;
}
.sim-metric-value {
    font-family: var(--font-display);
    font-size: 22px;
    font-weight: 800;
    color: var(--cyan);
}

/* ── Tooltip tag ── */
.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.05em;
}
.tag-cyan    { background: var(--cyan-dim);    color: var(--cyan);    border: 1px solid rgba(0,212,255,0.2); }
.tag-emerald { background: var(--emerald-dim); color: var(--emerald); border: 1px solid rgba(0,229,160,0.2); }
.tag-amber   { background: var(--amber-dim);   color: var(--amber);   border: 1px solid rgba(255,181,71,0.2); }
.tag-crimson { background: var(--crimson-dim); color: var(--crimson); border: 1px solid rgba(255,77,106,0.2); }

/* ── Footer ── */
.dash-footer {
    margin-top: 48px;
    padding: 24px 0;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-muted);
}

/* Sidebar section label */
.sidebar-section {
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 16px 0 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PLOTLY DARK TEMPLATE  ── applied to every chart
# ══════════════════════════════════════════════════════════════════════════════

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_family="DM Mono, monospace",
    font_color="#7a8bb0",
    title_font_family="Syne, sans-serif",
    title_font_color="#e8f0fe",
    title_font_size=14,
    colorway=["#00d4ff","#00e5a0","#ffb547","#ff4d6a","#a78bfa","#4d9fff","#ff8c69"],
    legend=dict(
        bgcolor="rgba(17,29,53,0.8)",
        bordercolor="rgba(0,212,255,0.15)",
        borderwidth=1,
        font_size=11,
        font_color="#7a8bb0",
    ),
    xaxis=dict(
        gridcolor="rgba(0,212,255,0.06)",
        zerolinecolor="rgba(0,212,255,0.1)",
        tickfont_size=10,
        linecolor="rgba(0,212,255,0.1)",
    ),
    yaxis=dict(
        gridcolor="rgba(0,212,255,0.06)",
        zerolinecolor="rgba(0,212,255,0.1)",
        tickfont_size=10,
        linecolor="rgba(0,212,255,0.1)",
    ),
    margin=dict(l=0, r=0, t=40, b=0),
    hoverlabel=dict(
        bgcolor="#111d35",
        bordercolor="rgba(0,212,255,0.3)",
        font_family="DM Mono, monospace",
        font_size=12,
        font_color="#e8f0fe",
    ),
    height=340,
)

def apply_template(fig, height=340, title=None):
    """Apply the dark template to any Plotly figure."""
    upd = {**PLOTLY_BASE, "height": height}
    if title:
        upd["title_text"] = title
    fig.update_layout(**upd)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(base, "..")
    paths = {
        "sales":     os.path.join(root, "data","processed","cleaned_data.csv"),
        "forecast":  os.path.join(root, "outputs","forecasts","forecast_results.csv"),
        "inventory": os.path.join(root, "outputs","inventory","reorder_recommendations.csv"),
    }
    for name, path in paths.items():
        if not os.path.exists(path):
            st.error(f"❌ Missing: `{path}` — run `python main.py` first.")
            st.stop()
    df_sales    = pd.read_csv(paths["sales"],    parse_dates=["date"])
    df_forecast = pd.read_csv(paths["forecast"], parse_dates=["date"])
    df_inv      = pd.read_csv(paths["inventory"])
    return df_sales, df_forecast, df_inv

df_sales, df_forecast, df_inventory = load_data()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding: 24px 0 8px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <div class="logo-hex">⬡</div>
            <div>
                <div class="logo-text" style="font-size:18px;">RetailIQ</div>
                <div class="logo-sub">Analytics Platform</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="status-pill"><div class="status-dot"></div>System Live</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Filters</div>', unsafe_allow_html=True)

    store_opts = ["All Stores"] + sorted(df_sales["store"].unique().tolist())
    cat_opts   = ["All Categories"] + sorted(df_sales["category"].unique().tolist())
    prod_opts  = ["All Products"] + sorted(df_sales["product"].unique().tolist())

    sel_store = st.selectbox("Store", store_opts)
    sel_cat   = st.selectbox("Category", cat_opts)
    sel_prod  = st.selectbox("Product", prod_opts)

    st.markdown('<div class="sidebar-section">Date Range</div>', unsafe_allow_html=True)
    min_d, max_d = df_sales["date"].min().date(), df_sales["date"].max().date()
    date_range   = st.date_input("", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    st.markdown('<div class="sidebar-section">Model Info</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:11px;line-height:1.9;
                color:#3d5070;padding:4px 0;">
        <span style="color:#00d4ff;">MODEL</span> XGBoost Regressor<br>
        <span style="color:#00d4ff;">MAPE</span>&nbsp;&nbsp;~8.3%<br>
        <span style="color:#00d4ff;">STORES</span> 5 locations<br>
        <span style="color:#00d4ff;">SKUS</span>&nbsp;&nbsp; 20 products<br>
        <span style="color:#00d4ff;">PERIOD</span> 3 years
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FILTER LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def filter_df(df, inv):
    if len(date_range) == 2:
        s, e = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        df = df[(df["date"] >= s) & (df["date"] <= e)]
    if sel_store != "All Stores":
        df  = df[df["store"]    == sel_store]
        inv = inv[inv["store"]  == sel_store]
    if sel_cat != "All Categories":
        df  = df[df["category"] == sel_cat]
        inv = inv[inv["category"]== sel_cat]
    if sel_prod != "All Products":
        df  = df[df["product"]  == sel_prod]
        inv = inv[inv["product"] == sel_prod]
    return df, inv

df_f, inv_f = filter_df(df_sales.copy(), df_inventory.copy())


# ══════════════════════════════════════════════════════════════════════════════
#  TOP NAV BAR
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="top-bar">
    <div class="top-bar-logo">
        <div class="logo-hex" style="width:36px;height:36px;font-size:16px;">⬡</div>
        <div>
            <div class="logo-text">RetailIQ · Demand Intelligence</div>
            <div class="logo-sub" style="font-size:9px;">
                Forecasting &amp; Inventory Command Center
            </div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:16px;">
        <div class="status-pill">
            <div class="status-dot"></div>
            XGBoost · MAPE 8.3%
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:10px;
                    color:#3d5070;letter-spacing:0.1em;">
            RETAIL ANALYTICS v2.0
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════

total_rev   = df_f["revenue"].sum()
total_units = df_f["sales_units"].sum()
so_rate     = df_f["stockout_flag"].mean() * 100
reorder_ct  = len(inv_f[inv_f["reorder_alert"].str.contains("ORDER NOW", na=False)])
critical_ct = len(inv_f[inv_f["inventory_status"].str.contains("Critical", na=False)])
avg_daily   = df_f["sales_units"].mean()

st.markdown('<div class="section-label">Performance Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Key Metrics</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-grid">

  <div class="kpi-card cyan">
    <span class="kpi-bg-icon">₹</span>
    <span class="kpi-icon">💰</span>
    <div class="kpi-label">Total Revenue</div>
    <div class="kpi-value">₹{total_rev/1e6:.1f}M</div>
    <div class="kpi-delta">▲ Across filtered period</div>
  </div>

  <div class="kpi-card emerald">
    <span class="kpi-bg-icon">📦</span>
    <span class="kpi-icon">📦</span>
    <div class="kpi-label">Units Sold</div>
    <div class="kpi-value">{total_units/1e3:.0f}K</div>
    <div class="kpi-delta">▲ Total volume</div>
  </div>

  <div class="kpi-card blue">
    <span class="kpi-bg-icon">📈</span>
    <span class="kpi-icon">📈</span>
    <div class="kpi-label">Avg Daily Sales</div>
    <div class="kpi-value">{avg_daily:.0f}</div>
    <div class="kpi-delta">units per day</div>
  </div>

  <div class="kpi-card {'crimson' if so_rate > 5 else 'amber'}">
    <span class="kpi-bg-icon">⚠</span>
    <span class="kpi-icon">⚠️</span>
    <div class="kpi-label">Stockout Rate</div>
    <div class="kpi-value">{so_rate:.1f}%</div>
    <div class="kpi-delta">{'▲ Above 5% threshold' if so_rate > 5 else '✓ Within threshold'}</div>
  </div>

  <div class="kpi-card {'crimson' if reorder_ct > 20 else 'amber'}">
    <span class="kpi-bg-icon">🔴</span>
    <span class="kpi-icon">🔴</span>
    <div class="kpi-label">Reorder Alerts</div>
    <div class="kpi-value">{reorder_ct}</div>
    <div class="kpi-delta">products need ordering</div>
  </div>

  <div class="kpi-card violet">
    <span class="kpi-bg-icon">🚨</span>
    <span class="kpi-icon">🚨</span>
    <div class="kpi-label">Critical Items</div>
    <div class="kpi-value">{critical_ct}</div>
    <div class="kpi-delta">below safety stock</div>
  </div>

</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SALES TRENDS  ── area chart + donut
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-label">Revenue Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Sales Trends</div>', unsafe_allow_html=True)

col_l, col_r = st.columns([3, 2])

with col_l:
    monthly = df_f.copy()
    monthly["ym"] = monthly["date"].dt.to_period("M").astype(str)
    m_agg = monthly.groupby("ym")["revenue"].sum().reset_index()

    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=m_agg["ym"], y=m_agg["revenue"],
        mode="lines",
        name="Revenue",
        line=dict(color="#00d4ff", width=2.5),
        fill="tozeroy",
        fillgradient=dict(
            type="vertical",
            colorscale=[[0,"rgba(0,212,255,0.25)"],[1,"rgba(0,212,255,0)"]],
        ),
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    # Add 3-month rolling average
    m_agg["rolling"] = m_agg["revenue"].rolling(3, min_periods=1).mean()
    fig_area.add_trace(go.Scatter(
        x=m_agg["ym"], y=m_agg["rolling"],
        mode="lines",
        name="3M Avg",
        line=dict(color="#a78bfa", width=1.5, dash="dot"),
        hovertemplate="<b>%{x}</b><br>3M Avg ₹%{y:,.0f}<extra></extra>",
    ))
    apply_template(fig_area, height=320, title="Monthly Revenue + 3-Month Rolling Average")
    fig_area.update_layout(
        xaxis_tickangle=-40,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08, x=0.02),
    )
    fig_area.update_xaxes(tickfont_size=9)
    st.plotly_chart(fig_area, use_container_width=True)

with col_r:
    cat_rev = df_f.groupby("category")["revenue"].sum().reset_index()
    fig_donut = go.Figure(go.Pie(
        labels=cat_rev["category"],
        values=cat_rev["revenue"],
        hole=0.55,
        textposition="outside",
        textfont_size=10,
        marker=dict(
            colors=["#00d4ff","#00e5a0","#ffb547","#a78bfa","#ff4d6a"],
            line=dict(color="#0d1526", width=3),
        ),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    apply_template(fig_donut, height=320, title="Revenue by Category")
    fig_donut.update_layout(
        legend=dict(orientation="v", x=0.01, y=0.01),
        annotations=[dict(
            text=f"₹{total_rev/1e6:.1f}M<br><span style='font-size:10px'>Total</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#e8f0fe", family="Syne"),
        )],
    )
    st.plotly_chart(fig_donut, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STORE + WEEKDAY PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════

col_s, col_w = st.columns(2)

with col_s:
    store_rev = df_f.groupby("store")["revenue"].sum().sort_values().reset_index()
    # Shorten store names for display
    store_rev["store_short"] = store_rev["store"].str.replace("Store_","")
    fig_store = go.Figure(go.Bar(
        x=store_rev["revenue"],
        y=store_rev["store_short"],
        orientation="h",
        marker=dict(
            color=store_rev["revenue"],
            colorscale=[[0,"#0d2b52"],[0.5,"#0066ff"],[1,"#00d4ff"]],
            line=dict(width=0),
        ),
        text=[f"₹{v/1e6:.1f}M" for v in store_rev["revenue"]],
        textposition="outside",
        textfont=dict(size=10, color="#7a8bb0"),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    apply_template(fig_store, height=280, title="Revenue by Store")
    fig_store.update_xaxes(tickformat="₹,.0f", showgrid=True)
    st.plotly_chart(fig_store, use_container_width=True)

with col_w:
    df_day = df_f.copy()
    df_day["dow"]  = df_day["date"].dt.dayofweek
    df_day["dname"]= df_day["date"].dt.day_name()
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_agg   = df_day.groupby("dname")["sales_units"].mean().reindex(day_order).reset_index()
    day_agg.columns = ["day","avg_sales"]
    day_agg["is_weekend"] = day_agg["day"].isin(["Saturday","Sunday"])

    fig_dow = go.Figure(go.Bar(
        x=day_agg["day"],
        y=day_agg["avg_sales"],
        marker=dict(
            color=["#ff4d6a" if w else "#00d4ff" for w in day_agg["is_weekend"]],
            opacity=[1 if w else 0.75 for w in day_agg["is_weekend"]],
            line=dict(width=0),
        ),
        text=day_agg["avg_sales"].round(0).astype(int),
        textposition="outside",
        textfont=dict(size=10, color="#7a8bb0"),
        hovertemplate="<b>%{x}</b><br>Avg %{y:.1f} units<extra></extra>",
    ))
    apply_template(fig_dow, height=280, title="Avg Sales by Day of Week")
    fig_dow.update_xaxes(tickfont_size=9)
    st.plotly_chart(fig_dow, use_container_width=True)

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  SEASONALITY HEATMAP
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-label">Pattern Recognition</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Seasonality Heatmap</div>', unsafe_allow_html=True)

df_heat = df_f.copy()
df_heat["month"] = df_heat["date"].dt.month
pivot = df_heat.pivot_table(
    values="sales_units", index="category", columns="month", aggfunc="mean"
)
month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
             7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
pivot.columns = [month_map.get(c,c) for c in pivot.columns]

fig_heat = go.Figure(go.Heatmap(
    z=pivot.values,
    x=pivot.columns.tolist(),
    y=pivot.index.tolist(),
    colorscale=[
        [0.0,  "#070b14"],
        [0.25, "#0d2b52"],
        [0.5,  "#0066ff"],
        [0.75, "#00d4ff"],
        [1.0,  "#00e5a0"],
    ],
    text=np.round(pivot.values, 0).astype(int),
    texttemplate="%{text}",
    textfont=dict(size=11, color="white", family="DM Mono"),
    hovertemplate="<b>%{y} · %{x}</b><br>Avg %{z:.0f} units/day<extra></extra>",
    showscale=True,
    colorbar=dict(
        thickness=10,
        len=0.8,
        tickfont=dict(size=9, color="#7a8bb0", family="DM Mono"),
        outlinewidth=0,
        bgcolor="rgba(0,0,0,0)",
    ),
))
apply_template(fig_heat, height=260, title="Average Daily Sales — Category × Month")
fig_heat.update_layout(
    xaxis=dict(side="top", tickfont_size=10),
    yaxis=dict(tickfont_size=11, autorange="reversed"),
)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  FORECAST vs ACTUAL
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-label">Demand Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Forecast vs Actual</div>', unsafe_allow_html=True)

df_fc = df_forecast.copy()
if sel_store != "All Stores":
    df_fc = df_fc[df_fc["store"]   == sel_store]
if sel_prod  != "All Products":
    df_fc = df_fc[df_fc["product"] == sel_prod]

fc_agg = df_fc.groupby("date")[["sales_units","xgb_predicted"]].sum().reset_index()

c_slider, c_gap = st.columns([3,1])
with c_slider:
    days_show = st.slider(
        "Days to display",
        min_value=30, max_value=max(90, len(fc_agg)),
        value=min(90, len(fc_agg)), step=10,
        key="fc_slider",
    )
fc_plot = fc_agg.tail(days_show)

fig_fc = go.Figure()

# Error band between actual and predicted
fig_fc.add_trace(go.Scatter(
    x=pd.concat([fc_plot["date"], fc_plot["date"].iloc[::-1]]),
    y=pd.concat([fc_plot["xgb_predicted"], fc_plot["sales_units"].iloc[::-1]]),
    fill="toself",
    fillcolor="rgba(0,212,255,0.05)",
    line=dict(width=0),
    showlegend=False,
    hoverinfo="skip",
))
fig_fc.add_trace(go.Scatter(
    x=fc_plot["date"], y=fc_plot["sales_units"],
    name="Actual",
    mode="lines",
    line=dict(color="#00e5a0", width=2),
    hovertemplate="<b>%{x|%b %d}</b><br>Actual: %{y:,}<extra></extra>",
))
fig_fc.add_trace(go.Scatter(
    x=fc_plot["date"], y=fc_plot["xgb_predicted"],
    name="XGBoost Forecast",
    mode="lines",
    line=dict(color="#00d4ff", width=2, dash="dot"),
    hovertemplate="<b>%{x|%b %d}</b><br>Forecast: %{y:,}<extra></extra>",
))
apply_template(fig_fc, height=360, title=f"Actual vs Forecast — Last {days_show} Days")
fig_fc.update_layout(
    hovermode="x unified",
    legend=dict(orientation="h", y=1.08, x=0.0),
)
st.plotly_chart(fig_fc, use_container_width=True)

# Accuracy metrics row
if len(df_fc) > 0:
    actual = df_fc["sales_units"].values
    pred   = df_fc["xgb_predicted"].values
    rmse   = np.sqrt(np.mean((actual - pred) ** 2))
    mae    = np.mean(np.abs(actual - pred))
    mask   = actual != 0
    mape   = np.mean(np.abs((actual[mask] - pred[mask]) / actual[mask])) * 100
    r2     = 1 - np.sum((actual - pred) ** 2) / np.sum((actual - actual.mean()) ** 2)

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;
                margin-top:4px;margin-bottom:8px;">
      <div style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);
                  border-radius:10px;padding:14px 18px;text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;
                    letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;">
          RMSE</div>
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                    color:#00d4ff;">{rmse:.2f}</div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;">
          lower is better</div>
      </div>
      <div style="background:rgba(0,229,160,0.06);border:1px solid rgba(0,229,160,0.15);
                  border-radius:10px;padding:14px 18px;text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;
                    letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;">
          MAE</div>
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                    color:#00e5a0;">{mae:.2f}</div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;">
          mean absolute error</div>
      </div>
      <div style="background:rgba(255,181,71,0.06);border:1px solid rgba(255,181,71,0.15);
                  border-radius:10px;padding:14px 18px;text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;
                    letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;">
          MAPE</div>
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                    color:{'#00e5a0' if mape < 15 else '#ff4d6a'};">{mape:.1f}%</div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;
                    color:{'#00e5a0' if mape < 15 else '#ff4d6a'};">
          {'✓ excellent' if mape < 10 else '✓ good' if mape < 15 else '✗ needs tuning'}</div>
      </div>
      <div style="background:rgba(167,139,250,0.06);border:1px solid rgba(167,139,250,0.15);
                  border-radius:10px;padding:14px 18px;text-align:center;">
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;
                    letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;">
          R² Score</div>
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                    color:#a78bfa;">{max(0,r2):.3f}</div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;">
          {'✓ strong fit' if r2 > 0.85 else '~ moderate fit'}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  INVENTORY OPTIMIZATION
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-label">Supply Chain Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Inventory Optimization</div>', unsafe_allow_html=True)

col_inv1, col_inv2, col_inv3 = st.columns([1, 1, 1])

with col_inv1:
    # Donut — inventory health
    sc = inv_f["inventory_status"].value_counts().reset_index()
    sc.columns = ["Status","Count"]
    color_map = {
        "🔴 Critical":"#ff4d6a","🟠 Low":"#ffb547",
        "🟢 Optimal":"#00e5a0","🔵 Overstock":"#00d4ff",
    }
    fig_health = go.Figure(go.Pie(
        labels=sc["Status"], values=sc["Count"], hole=0.6,
        textposition="outside", textfont_size=9,
        marker=dict(
            colors=[color_map.get(s,"#7a8bb0") for s in sc["Status"]],
            line=dict(color="#0d1526", width=4),
        ),
        hovertemplate="<b>%{label}</b><br>%{value} products<extra></extra>",
    ))
    apply_template(fig_health, height=280, title="Inventory Health")
    fig_health.update_layout(
        legend=dict(orientation="v", x=0, y=0),
        annotations=[dict(
            text=f"<b>{len(inv_f)}</b><br><span style='font-size:9px'>products</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=15, color="#e8f0fe", family="Syne"),
        )],
    )
    st.plotly_chart(fig_health, use_container_width=True)

with col_inv2:
    # Top stockout products
    top_so = inv_f.nlargest(8,"stockout_rate_pct")[["product","stockout_rate_pct"]].copy()
    top_so["product_short"] = top_so["product"].str[:18]
    fig_so = go.Figure(go.Bar(
        x=top_so["stockout_rate_pct"],
        y=top_so["product_short"],
        orientation="h",
        marker=dict(
            color=top_so["stockout_rate_pct"],
            colorscale=[[0,"#2d0a12"],[0.5,"#993049"],[1,"#ff4d6a"]],
            line=dict(width=0),
        ),
        text=[f"{v:.1f}%" for v in top_so["stockout_rate_pct"]],
        textposition="outside",
        textfont=dict(size=9, color="#7a8bb0"),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% stockout<extra></extra>",
    ))
    apply_template(fig_so, height=280, title="Top 8 Stockout Risk")
    fig_so.update_xaxes(ticksuffix="%")
    st.plotly_chart(fig_so, use_container_width=True)

with col_inv3:
    # EOQ distribution
    fig_eoq = go.Figure(go.Histogram(
        x=inv_f["eoq"].clip(upper=inv_f["eoq"].quantile(0.95)),
        nbinsx=30,
        marker=dict(
            color="#a78bfa",
            opacity=0.85,
            line=dict(width=0),
        ),
        hovertemplate="EOQ: %{x:.0f}<br>Products: %{y}<extra></extra>",
    ))
    apply_template(fig_eoq, height=280, title="EOQ Distribution")
    fig_eoq.update_traces(
        marker=dict(
            color=None,
            colorscale=[[0,"#2d1b6b"],[1,"#a78bfa"]],
            coloraxis="coloraxis",
        ),
    )
    fig_eoq.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_eoq, use_container_width=True)


# ─── Reorder Table ────────────────────────────────────────────────────────────

st.markdown('<div class="section-label" style="margin-top:8px;">Procurement Alerts</div>',
            unsafe_allow_html=True)

col_tbl_ctrl, col_tbl_dl = st.columns([3, 1])
with col_tbl_ctrl:
    show_all = st.checkbox("Show all products (default: reorder alerts only)", value=False)
with col_tbl_dl:
    pass

table_df = inv_f if show_all else inv_f[
    inv_f["reorder_alert"].str.contains("ORDER NOW", na=False)
]

if len(table_df) == 0:
    st.markdown("""
    <div style="background:rgba(0,229,160,0.08);border:1px solid rgba(0,229,160,0.2);
                border-radius:10px;padding:16px 20px;font-family:'DM Mono',monospace;
                font-size:12px;color:#00e5a0;">
        ✓ No immediate reorders needed for current selection.
    </div>
    """, unsafe_allow_html=True)
else:
    display_cols = [c for c in [
        "store","category","product","avg_daily_demand",
        "safety_stock","reorder_point","avg_closing_stock",
        "eoq","recommended_order_qty","stockout_rate_pct",
        "inventory_status","reorder_alert",
    ] if c in table_df.columns]

    st.dataframe(
        table_df[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=320,
    )
    c_dl1, c_dl2, _ = st.columns([2, 2, 4])
    with c_dl1:
        st.download_button(
            "⬇ Download Alerts CSV",
            data=table_df[display_cols].to_csv(index=False),
            file_name="reorder_alerts.csv", mime="text/csv",
        )

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCT PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-label">Product Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Product Performance</div>', unsafe_allow_html=True)

col_p1, col_p2 = st.columns(2)

with col_p1:
    top_rev = (df_f.groupby("product")["revenue"]
               .sum().nlargest(10).sort_values().reset_index())
    fig_pr = go.Figure(go.Bar(
        x=top_rev["revenue"], y=top_rev["product"],
        orientation="h",
        marker=dict(
            color=top_rev["revenue"],
            colorscale=[[0,"#0a2a1a"],[0.5,"#006644"],[1,"#00e5a0"]],
            line=dict(width=0),
        ),
        text=[f"₹{v/1e6:.2f}M" for v in top_rev["revenue"]],
        textposition="outside",
        textfont=dict(size=9, color="#7a8bb0"),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
    ))
    apply_template(fig_pr, height=320, title="Top 10 by Revenue")
    fig_pr.update_xaxes(tickformat="₹,.0f", showgrid=True)
    st.plotly_chart(fig_pr, use_container_width=True)

with col_p2:
    top_units = (df_f.groupby("product")["sales_units"]
                 .sum().nlargest(10).sort_values().reset_index())
    fig_pu = go.Figure(go.Bar(
        x=top_units["sales_units"], y=top_units["product"],
        orientation="h",
        marker=dict(
            color=top_units["sales_units"],
            colorscale=[[0,"#1a0d3d"],[0.5,"#5b31b5"],[1,"#a78bfa"]],
            line=dict(width=0),
        ),
        text=[f"{v:,}" for v in top_units["sales_units"]],
        textposition="outside",
        textfont=dict(size=9, color="#7a8bb0"),
        hovertemplate="<b>%{y}</b><br>%{x:,} units<extra></extra>",
    ))
    apply_template(fig_pu, height=320, title="Top 10 by Units Sold")
    st.plotly_chart(fig_pu, use_container_width=True)


# ─── Sales Distribution ───────────────────────────────────────────────────────

col_d1, col_d2 = st.columns(2)
with col_d1:
    fig_hist = go.Figure(go.Histogram(
        x=df_f["sales_units"], nbinsx=60,
        marker=dict(color="#00d4ff", opacity=0.7, line=dict(width=0)),
        hovertemplate="Sales: %{x}<br>Count: %{y}<extra></extra>",
    ))
    apply_template(fig_hist, height=280, title="Daily Sales Distribution")
    fig_hist.update_layout(bargap=0.05)
    st.plotly_chart(fig_hist, use_container_width=True)

with col_d2:
    fig_box = go.Figure()
    cats = df_f["category"].unique()
    cat_colors = ["#00d4ff","#00e5a0","#ffb547","#a78bfa","#ff4d6a"]
    for i, cat in enumerate(cats):
        sub = df_f[df_f["category"] == cat]
        fig_box.add_trace(go.Box(
            y=sub["sales_units"], name=cat,
            marker_color=cat_colors[i % len(cat_colors)],
            line_width=1.5,
            boxmean="sd",
            hovertemplate=f"<b>{cat}</b><br>%{{y}} units<extra></extra>",
        ))
    apply_template(fig_box, height=280, title="Sales Range by Category")
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  WHAT-IF SCENARIO SIMULATION
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="section-label">Scenario Modelling</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">What-If Simulation</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.1);
            border-radius:12px;padding:14px 20px;margin-bottom:20px;
            font-family:'DM Mono',monospace;font-size:11px;color:#7a8bb0;">
    ↳ Adjust supplier lead time and service level to model the impact on safety stock
    and reorder points across your entire product catalogue.
</div>
""", unsafe_allow_html=True)

sim_col1, sim_col2 = st.columns([1, 2])

with sim_col1:
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#3d5070;
                letter-spacing:0.15em;text-transform:uppercase;margin-bottom:6px;">
        PARAMETERS</div>
    """, unsafe_allow_html=True)

    sim_lt = st.slider("Supplier Lead Time (days)", 1, 30, 5, key="sim_lt")
    sim_sl = st.slider("Service Level (%)", 80, 99, 95, key="sim_sl")

    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#3d5070;
                letter-spacing:0.1em;margin:16px 0 8px;">
        SCENARIO CONTEXT
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#7a8bb0;
                line-height:2;">
        Current baseline: 5 days · 95%<br>
        Z-score applied: per service level<br>
        Formula: Z × σ × √(lead_time)
    </div>
    """, unsafe_allow_html=True)

    run_sim = st.button("▶ Run Simulation", type="primary", use_container_width=True)

with sim_col2:
    if run_sim:
        from scipy.stats import norm
        z = norm.ppf(sim_sl / 100)

        rows = []
        for _, r in inv_f.iterrows():
            new_ss  = round(z * r["std_daily_demand"] * np.sqrt(sim_lt), 0)
            new_rop = round((r["avg_daily_demand"] * sim_lt) + new_ss, 0)
            rows.append({
                "product":   r["product"],
                "store":     r["store"],
                "orig_ss":   int(r["safety_stock"]),
                "new_ss":    int(new_ss),
                "orig_rop":  int(r["reorder_point"]),
                "new_rop":   int(new_rop),
                "Δ_rop":     int(new_rop - r["reorder_point"]),
                "Δ_ss":      int(new_ss  - r["safety_stock"]),
            })
        sim_df = pd.DataFrame(rows)

        avg_rop_d = sim_df["Δ_rop"].mean()
        avg_ss_d  = sim_df["Δ_ss"].mean()
        increased = (sim_df["Δ_rop"] > 0).sum()
        decreased = (sim_df["Δ_rop"] < 0).sum()

        sign = "▲" if avg_rop_d >= 0 else "▼"
        col_rop = "#ff4d6a" if avg_rop_d > 0 else "#00e5a0"

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;
                    margin-bottom:16px;">
          <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
                      border-radius:10px;padding:14px;text-align:center;">
            <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;
                        text-transform:uppercase;letter-spacing:0.12em;margin-bottom:4px;">
                Avg ROP Change</div>
            <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
                        color:{col_rop};">{sign}{abs(avg_rop_d):.1f}</div>
          </div>
          <div style="background:rgba(0,229,160,0.05);border:1px solid rgba(0,229,160,0.15);
                      border-radius:10px;padding:14px;text-align:center;">
            <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;
                        text-transform:uppercase;letter-spacing:0.12em;margin-bottom:4px;">
                Avg SS Change</div>
            <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
                        color:#00e5a0;">{avg_ss_d:+.1f}</div>
          </div>
          <div style="background:rgba(255,181,71,0.05);border:1px solid rgba(255,181,71,0.15);
                      border-radius:10px;padding:14px;text-align:center;">
            <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;
                        text-transform:uppercase;letter-spacing:0.12em;margin-bottom:4px;">
                ROP Increased</div>
            <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
                        color:#ffb547;">{increased}</div>
          </div>
          <div style="background:rgba(167,139,250,0.05);border:1px solid rgba(167,139,250,0.15);
                      border-radius:10px;padding:14px;text-align:center;">
            <div style="font-family:'DM Mono',monospace;font-size:9px;color:#3d5070;
                        text-transform:uppercase;letter-spacing:0.12em;margin-bottom:4px;">
                ROP Decreased</div>
            <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
                        color:#a78bfa;">{decreased}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Waterfall-style delta chart
        top_changes = sim_df.nlargest(12, "Δ_rop")[["product","Δ_rop","Δ_ss"]].copy()
        top_changes["product_s"] = top_changes["product"].str[:18]

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Bar(
            name="Δ Reorder Point",
            x=top_changes["Δ_rop"],
            y=top_changes["product_s"],
            orientation="h",
            marker=dict(
                color=["#ff4d6a" if v > 0 else "#00e5a0" for v in top_changes["Δ_rop"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>ROP change: %{x:+.0f}<extra></extra>",
        ))
        fig_sim.add_trace(go.Bar(
            name="Δ Safety Stock",
            x=top_changes["Δ_ss"],
            y=top_changes["product_s"],
            orientation="h",
            marker=dict(color="#ffb547", opacity=0.6, line=dict(width=0)),
            hovertemplate="<b>%{y}</b><br>SS change: %{x:+.0f}<extra></extra>",
        ))
        apply_template(fig_sim, height=340,
                       title=f"Top Impacted Products · LT={sim_lt}d · SL={sim_sl}%")
        fig_sim.update_layout(barmode="group", hovermode="y unified")
        fig_sim.update_xaxes(ticksuffix=" units", zeroline=True,
                             zerolinecolor="rgba(0,212,255,0.2)")
        st.plotly_chart(fig_sim, use_container_width=True)

        dl1, dl2, _ = st.columns([2,2,4])
        with dl1:
            st.download_button(
                "⬇ Download Simulation",
                data=sim_df.to_csv(index=False),
                file_name=f"sim_lt{sim_lt}_sl{sim_sl}.csv",
                mime="text/csv",
            )
    else:
        st.markdown("""
        <div style="height:260px;display:flex;flex-direction:column;align-items:center;
                    justify-content:center;background:rgba(0,212,255,0.03);
                    border:1px dashed rgba(0,212,255,0.15);border-radius:12px;gap:12px;">
            <div style="font-size:36px;opacity:0.3;">⚗</div>
            <div style="font-family:'DM Mono',monospace;font-size:12px;color:#3d5070;
                        text-align:center;line-height:1.8;">
                Adjust parameters on the left<br>
                and click <span style="color:#00d4ff;">▶ Run Simulation</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="dash-footer">
    <div>
        <span style="color:#00d4ff;font-weight:600;">RetailIQ</span>
        · Retail Sales Forecasting &amp; Inventory Optimization
    </div>
    <div style="display:flex;gap:24px;">
        <span>Python · XGBoost · Pandas</span>
        <span style="color:#3d5070;">|</span>
        <span>Streamlit · Plotly</span>
        <span style="color:#3d5070;">|</span>
        <span style="color:#00e5a0;">Portfolio Project</span>
    </div>
</div>
""", unsafe_allow_html=True)