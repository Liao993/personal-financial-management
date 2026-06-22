import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from modules.portfolio.components.bar_chart_helpers import render_horizontal_bar


STOCK_CATEGORY_COLORS = {
    "Tech": "#3498db",
    "Finance": "#00ab41",
    "Consumer": "#f39c12",
    "Healthcare": "#e74c3c",
    "Energy": "#1a5276",
    "Dividend": "#a569bd",
}


def create_stock_bar(df: pd.DataFrame, tab_key: str, usd_cad_rate):
    stock_df = df[(df["asset_type"] == "Stock") & df["market_value_cad"].notna()].copy()

    if stock_df.empty:
        if not df[df["asset_type"] == "Stock"].empty:
            st.info("Stock holdings exist but have no CAD market value yet — click 'Fetch Live Prices' above.")
        else:
            st.info("No stock holdings in this account.")
        return

    grouped = stock_df.groupby("stock_category")["market_value_cad"].sum().reset_index()

    render_horizontal_bar(
        grouped=grouped,
        label_col="stock_category",
        value_col="market_value_cad",
        usd_cad_rate=usd_cad_rate,
        title="Stock Allocation by Category",
        color_map=STOCK_CATEGORY_COLORS,
        chart_key=f"stock_bar_{tab_key}",
    )