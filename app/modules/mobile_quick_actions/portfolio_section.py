import streamlit as st  # type: ignore

from backend.portfolio_backend import (
    fetch_all_holdings,
    fetch_usd_cad_rate,
    fetch_last_price_update,
)


def render_portfolio_section():
    st.subheader("📈 Portfolio")

    last_update = fetch_last_price_update()
    if last_update is None:
        st.info(
            "No live price data yet — fetch prices from the full "
            "Portfolio Holdings page first."
        )
        return

    df = fetch_all_holdings()
    if df.empty:
        st.info("No holdings recorded yet.")
        return

    usd_cad_rate = fetch_usd_cad_rate()
    total_cad = df["market_value_cad"].sum() if "market_value_cad" in df.columns else 0.0
    native_cad = df.loc[df["currency"] == "CAD", "market_value"].sum()
    native_usd = df.loc[df["currency"] == "USD", "market_value"].sum()

    st.caption(f"Last price update: {last_update}")
    if usd_cad_rate:
        st.caption(f"1 USD = {usd_cad_rate:.4f} CAD")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Value (CAD)", f"${total_cad:,.2f}")
    with col2:
        st.metric("Total Holdings", f"{len(df)}")

    col3, col4 = st.columns(2)
    with col3:
        st.metric("Native CAD Holdings", f"${native_cad:,.2f}")
    with col4:
        st.metric("Native USD Holdings", f"${native_usd:,.2f}")