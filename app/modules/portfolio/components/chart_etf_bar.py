import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from modules.portfolio.components.bar_chart_helpers import render_horizontal_bar


ETF_CATEGORY_COLORS = {
    "Global": "#1a5276",
    "US": "#e74c3c",
    "Europe": "#3498db",
    "Asia": "#f39c12",
    "Bond": "#00ab41",
    "Dividend": "#a569bd",
    "Industry": "#d35400",
}


def create_etf_bar(df: pd.DataFrame, tab_key: str, usd_cad_rate):
    etf_df = df[(df["asset_type"] == "ETF") & df["market_value_cad"].notna()].copy()

    if etf_df.empty:
        if not df[df["asset_type"] == "ETF"].empty:
            st.info("ETF holdings exist but have no CAD market value yet — click 'Fetch Live Prices' above.")
        else:
            st.info("No ETF holdings in this account.")
        return

    grouped = etf_df.groupby("etf_category")["market_value_cad"].sum().reset_index()

    render_horizontal_bar(
        grouped=grouped,
        label_col="etf_category",
        value_col="market_value_cad",
        usd_cad_rate=usd_cad_rate,
        title="ETF Allocation by Category",
        color_map=ETF_CATEGORY_COLORS,
        chart_key=f"etf_bar_{tab_key}",
    )