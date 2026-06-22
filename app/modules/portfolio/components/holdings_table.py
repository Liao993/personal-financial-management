import streamlit as st  # type: ignore
import pandas as pd  # type: ignore


def display_holdings_table(df: pd.DataFrame):
    if df.empty:
        st.info("No holdings to display.")
        return

    display_df = df.copy()
    display_df["category"] = display_df["etf_category"].fillna(display_df["stock_category"])

    show_cols = [
        "ticker",
        "asset_type",
        "account_name",
        "units",
        "currency",
        "current_price",
        "market_value",
        "market_value_cad",
        "category",
        "purpose",
    ]
    show_df = display_df[show_cols].copy()

    show_df["current_price"] = show_df["current_price"].apply(
        lambda x: f"${x:,.4f}" if pd.notna(x) else "No price yet"
    )
    show_df["market_value"] = show_df["market_value"].apply(
        lambda x: f"${x:,.2f}" if pd.notna(x) else "—"
    )
    show_df["market_value_cad"] = show_df["market_value_cad"].apply(
        lambda x: f"${x:,.2f}" if pd.notna(x) else "—"
    )

    show_df = show_df.rename(
        columns={
            "market_value": "Market Value (Native)",
            "market_value_cad": "Market Value (CAD)",
        }
    )

    st.dataframe(show_df, hide_index=True, use_container_width=True)