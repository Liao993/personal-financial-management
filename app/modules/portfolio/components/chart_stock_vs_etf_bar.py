import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from modules.portfolio.components.bar_chart_helpers import render_horizontal_bar


SEGMENT_COLORS = {
    "Single Stock": "#e74c3c",
    "Global": "#1a5276",
    "US": "#3498db",
    "Europe": "#5dade2",
    "Asia": "#f39c12",
    "Bond": "#00ab41",
    "Dividend": "#a569bd",
    "Industry": "#d35400",
}


def create_stock_vs_etf_bar(df: pd.DataFrame, tab_key: str, usd_cad_rate):
    """
    Shows the split between all individual stock holdings (collapsed into
    one 'Single Stock' bar) versus each ETF category. Example: NVDA 2000 +
    GOOG 2000 + VOO(US) 4000 + VT(Global) 2000 -> Single Stock 40%, US 40%,
    Global 20%.

    "Single Stock" is always pinned to the top row regardless of its
    value — the ETF categories underneath still sort by value (largest
    ETF category sits just below Single Stock, smallest at the bottom).
    """
    priced_df = df[df["market_value_cad"].notna()].copy()

    if priced_df.empty:
        st.info("No holdings with a CAD market value yet — click 'Fetch Live Prices' above.")
        return

    priced_df["segment"] = priced_df.apply(
        lambda row: "Single Stock" if row["asset_type"] == "Stock" else row["etf_category"],
        axis=1,
    )
    grouped = priced_df.groupby("segment")["market_value_cad"].sum().reset_index()

    single_stock_row = grouped[grouped["segment"] == "Single Stock"]
    other_rows = grouped[grouped["segment"] != "Single Stock"].sort_values(
        "market_value_cad", ascending=True
    )
    # other_rows first (ascending), Single Stock last -> Plotly draws the
    # last row at the top of a horizontal bar chart.
    ordered = pd.concat([other_rows, single_stock_row], ignore_index=True)

    render_horizontal_bar(
        grouped=ordered,
        label_col="segment",
        value_col="market_value_cad",
        usd_cad_rate=usd_cad_rate,
        title="Single Stock vs ETF Category",
        color_map=SEGMENT_COLORS,
        chart_key=f"stock_vs_etf_bar_{tab_key}",
        preserve_order=True,
    )
