import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from modules.portfolio.components.bar_chart_helpers import render_horizontal_bar


PURPOSE_COLORS = {
    "Growth": "#16a085",
    "Dividend": "#8e44ad",
    "Bond": "#2980b9",
}


def create_purpose_bar(df: pd.DataFrame, tab_key: str, usd_cad_rate):
    """
    Single horizontal bar chart showing CAD market value by Purpose
    (Growth / Dividend / Bond) across both ETFs and Stocks combined. No
    account split — the Total/TFSA/RRSP tabs already provide that.
    """
    priced_df = df[df["market_value_cad"].notna()].copy()

    if priced_df.empty:
        st.info("No holdings with a CAD market value yet — click 'Fetch Live Prices' above.")
        return

    grouped = priced_df.groupby("purpose")["market_value_cad"].sum().reset_index()

    render_horizontal_bar(
        grouped=grouped,
        label_col="purpose",
        value_col="market_value_cad",
        usd_cad_rate=usd_cad_rate,
        title="Holdings by Purpose",
        color_map=PURPOSE_COLORS,
        chart_key=f"purpose_bar_{tab_key}",
    )