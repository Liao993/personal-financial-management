import streamlit as st  # type: ignore
import pandas as pd  # type: ignore


def display_portfolio_kpis(df: pd.DataFrame, total_deposit: float=0.0):
    if df.empty:
        st.info("No holdings to summarize yet.")
        return

    missing_price_count = df["current_price"].isna().sum()
    missing_cad_count = (
        df["market_value_cad"].isna().sum() if "market_value_cad" in df.columns else 0
    )

    total_cad = df["market_value_cad"].sum() if "market_value_cad" in df.columns else 0.0
    native_cad_value = df.loc[df["currency"] == "CAD", "market_value"].sum()
    native_usd_value = df.loc[df["currency"] == "USD", "market_value"].sum()
    total_holdings = len(df)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"<p style='font-size: 22px; color: #00ab41;'><b>Total Value (CAD)</b></p>"
            f"<p style='font-size: 26px;'><b>${total_cad:,.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<p style='font-size: 22px; color: #f39c12;'><b>Native CAD Holdings</b></p>"
            f"<p style='font-size: 26px;'><b>${native_cad_value:,.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"<p style='font-size: 22px; color: #5dade2;'><b>Native USD Holdings</b></p>"
            f"<p style='font-size: 26px;'><b>${native_usd_value:,.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"<p style='font-size: 22px; color: #8e44ad;'><b>Total Holdings</b></p>"
            f"<p style='font-size: 26px;'><b>{total_holdings}</b></p>",
            unsafe_allow_html=True,
        )
    
    with col5:
        st.markdown(
            f"<p style='font-size: 22px; color: #e74c3c;'><b>Total Deposit</b></p>"
            f"<p style='font-size: 26px;'><b>${total_deposit:,.2f}</b></p>",
            unsafe_allow_html=True,
        )

    if missing_price_count > 0:
        st.caption(
            f"⚠️ {missing_price_count} holding(s) have no live price yet — click 'Fetch Live Prices' above."
        )
    if missing_cad_count > 0 and missing_cad_count != missing_price_count:
        st.caption(
            f"⚠️ {missing_cad_count} holding(s) are missing a CAD-equivalent value "
            "(likely USD holdings priced before the FX rate was fetched)."
        )