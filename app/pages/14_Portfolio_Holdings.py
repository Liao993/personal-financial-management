import streamlit as st  # type: ignore
import pandas as pd  # type: ignore

from backend.portfolio_backend import (
    insert_holding,
    fetch_all_holdings,
    fetch_holding_by_id,
    update_holding,
    delete_holding,
    fetch_last_price_update,
    fetch_usd_cad_rate,
)
from backend.live_price_fetch import run_manual_price_fetch
from models.portfolio_models import Holding
from pydantic import ValidationError  # type: ignore

from modules.portfolio.components.kpi import display_portfolio_kpis
from modules.portfolio.components.chart_etf_bar import create_etf_bar
from modules.portfolio.components.chart_stock_bar import create_stock_bar
from modules.portfolio.components.chart_stock_vs_etf_bar import create_stock_vs_etf_bar
from modules.portfolio.components.chart_purpose_bar import create_purpose_bar
from modules.portfolio.components.holdings_table import display_holdings_table
from modules.portfolio.components.holding_form import holding_form

st.set_page_config(page_title="Portfolio Holdings", page_icon="📊", layout="wide")

# Wider, bigger-font tabs (Total Portfolio / TFSA / RRSP), PLUS bigger text
# for exactly the three main action buttons (Fetch Live Prices / Dashboard /
# Manage Holdings) without changing their color/type. Each of those buttons
# is preceded by a tiny invisible marker span; the CSS below uses :has() +
# adjacent-sibling (+) to reach only the button that comes right after its
# own marker, leaving every other button (Edit/Delete/Confirm/Cancel, etc.)
# untouched at their normal size.
st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 56px;
        padding: 0px 28px;
        font-size: 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 171, 65, 0.12);
        border-bottom: 4px solid #00ab41;
    }

    div[data-testid="stMarkdown"]:has(#big-btn-fetch) + div[data-testid="stButton"] button,
    div[data-testid="stMarkdown"]:has(#big-btn-dashboard) + div[data-testid="stButton"] button,
    div[data-testid="stMarkdown"]:has(#big-btn-manage) + div[data-testid="stButton"] button {
        font-size: 28px !important;
        font-weight: 700 !important;
        padding: 0.6em 1.2em !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    defaults = {
        "portfolio_mode": "dashboard",
        "holding_edit_mode": True,
        "holding_review_data": {},
        "holding_data_saved": False,
        "holding_edit_id": None,
        "holding_confirm_delete_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_freshness_banner_and_trigger():
    last_update = fetch_last_price_update()
    fx_rate = fetch_usd_cad_rate()
    col1, col2 = st.columns([3, 1])

    with col1:
        if last_update is None:
            st.info(
                "No live price data yet. Holdings below show units only until "
                "you click 'Fetch Live Prices' for the first time."
            )
        else:
            fx_line = (
                f" | 1 USD = {fx_rate:.4f} CAD" if fx_rate else " | USD→CAD rate not fetched yet"
            )
            st.markdown(
                f"<p style='color: gray; font-size: 16px; padding-top: 10px;'>"
                f"Last price update: {last_update}{fx_line}</p>",
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown('<span id="big-btn-fetch"></span>', unsafe_allow_html=True)
        if st.button("🔄 Fetch Live Prices", use_container_width=True):
            with st.spinner("Fetching current prices and USD→CAD rate from Yahoo Finance..."):
                result = run_manual_price_fetch()

            if result["total"] == 0:
                st.warning("No holdings yet — add a holding first, then fetch prices.")
            elif result["success"] == result["total"]:
                msg = f"✅ Updated prices for all {result['success']} ticker(s)."
                if result["fx_fetched"]:
                    msg += f" USD→CAD rate: {result['fx_rate']:.4f}."
                else:
                    msg += " ⚠️ Could not fetch the USD→CAD rate this time."
                st.success(msg)
            elif result["success"] > 0:
                msg = (
                    f"⚠️ Updated {result['success']} of {result['total']} ticker(s). "
                    f"Failed: {', '.join(result['failed'])} "
                    "(check the ticker symbol is correct and try again)."
                )
                if not result["fx_fetched"]:
                    msg += " Also failed to fetch the USD→CAD rate."
                st.warning(msg)
            else:
                st.error(
                    f"❌ Could not fetch any prices. Failed: {', '.join(result['failed'])}. "
                    "Check your tickers are valid exchange symbols."
                )
            st.rerun()


def _filter_by_account(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    Filters holdings by account name keyword. Safe on an empty DataFrame —
    calling .str.contains() on an empty frame's column still works fine in
    pandas, but if the frame is empty AND has no columns at all (e.g. the
    backend returned pd.DataFrame() with zero columns on a connection
    failure), there is no 'account_name' column to filter on. Guard for
    that.
    """
    if df.empty or "account_name" not in df.columns:
        return df
    return df[df["account_name"].str.contains(keyword, case=False, na=False)]


def render_dashboard_mode():
    df = fetch_all_holdings()
    usd_cad_rate = fetch_usd_cad_rate()

    tabs = st.tabs(["🌐  Total Portfolio", "🟢  TFSA", "🔵  RRSP", "🟠 Retirement"])

    tab_configs = [
        ("total", df),
        ("tfsa", _filter_by_account(df, "TFSA")),
        ("rrsp", _filter_by_account(df, "RRSP")),
        ("retirement", _filter_by_account(df, "Retire")),
    ]

    for tab, (tab_key, df_tab) in zip(tabs, tab_configs):
        with tab:
            display_portfolio_kpis(df_tab)
            st.write(" ")
            create_etf_bar(df_tab, tab_key=tab_key, usd_cad_rate=usd_cad_rate)
            st.write(" ")
            create_stock_bar(df_tab, tab_key=tab_key, usd_cad_rate=usd_cad_rate)
            st.write(" ")
            create_stock_vs_etf_bar(df_tab, tab_key=tab_key, usd_cad_rate=usd_cad_rate)
            st.write(" ")
            create_purpose_bar(df_tab, tab_key=tab_key, usd_cad_rate=usd_cad_rate)
            st.divider()
            display_holdings_table(df_tab)


def render_manage_holdings_mode():
    # Tracks the ticker currently being edited (if any), so we can show a
    # pointer note down in the "All Holdings" section after the user clicks
    # Edit, telling them where the editable fields actually are.
    editing_ticker = None

    # ---- Add / Edit form flow ----
    if st.session_state["holding_edit_mode"]:
        prefill = {}
        if st.session_state["holding_edit_id"] is not None:
            prefill = fetch_holding_by_id(st.session_state["holding_edit_id"])
            editing_ticker = prefill.get("ticker")
            st.markdown(f"**Editing holding #{st.session_state['holding_edit_id']}**")
        else:
            st.markdown("**Add New Holding**")

        holding_form("holding_edit_mode", "holding_review_data", prefill=prefill)

    else:
        if not st.session_state["holding_data_saved"]:
            st.subheader("Review Holding")
            review_data = st.session_state["holding_review_data"]
            st.table(review_data)

            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Confirm")
            with col2:
                edit_button = st.button("Edit")

            if confirm_button:
                try:
                    validated = Holding(**review_data)
                    if st.session_state["holding_edit_id"] is not None:
                        success = update_holding(
                            st.session_state["holding_edit_id"], validated.dict()
                        )
                    else:
                        success = insert_holding(validated.dict())

                    if success:
                        st.session_state["holding_data_saved"] = True
                        st.success("Holding saved successfully!")
                        st.rerun()
                except ValidationError as e:
                    for error in e.errors():
                        st.error(f"Error in field '{error['loc'][0]}': {error['msg']}")

            if edit_button:
                st.session_state["holding_edit_mode"] = True
                st.session_state["holding_data_saved"] = False
                st.rerun()
        else:
            st.success("Holding saved! Returning to holdings list.")
            st.session_state["holding_edit_mode"] = True
            st.session_state["holding_data_saved"] = False
            st.session_state["holding_edit_id"] = None
            st.session_state["holding_review_data"] = {}
            st.rerun()

    st.divider()

    # ---- All holdings table with Edit / Delete ----
    st.subheader("All Holdings")

    if editing_ticker:
        st.info(f"✏️ You can update **{editing_ticker}** in the form above now.")

    df = fetch_all_holdings()

    if df.empty:
        st.info("No holdings recorded yet. Use the form above to add your first holding.")
        return

    for _, row in df.iterrows():
        holding_id = int(row["id"])
        category = row["etf_category"] or row["stock_category"]
        price_known = pd.notna(row["current_price"])

        with st.expander(
            f"{row['ticker']} | {row['asset_type']} | {row['account_name']} | "
            f"{row['units']:.4f} units | {category}"
        ):
            col_info, col_actions = st.columns([3, 1])

            with col_info:
                if price_known:
                    st.write(f"**Current Price:** ${row['current_price']:.4f} {row['currency']}")
                    st.write(f"**Market Value (Native):** ${row['market_value']:,.2f} {row['currency']}")
                    if pd.notna(row.get("market_value_cad")):
                        st.write(f"**Market Value (CAD):** ${row['market_value_cad']:,.2f}")
                    else:
                        st.write("**Market Value (CAD):** — (USD→CAD rate not fetched yet)")
                else:
                    st.write("**Current Price:** No live price yet")
                    st.write("**Market Value:** —")
                if row["notes"]:
                    st.write(f"**Notes:** {row['notes']}")

            with col_actions:
                if st.button("✏️ Edit", key=f"edit_{holding_id}"):
                    st.session_state["holding_edit_mode"] = True
                    st.session_state["holding_edit_id"] = holding_id
                    st.rerun()

                if st.session_state["holding_confirm_delete_id"] != holding_id:
                    if st.button("🗑️ Delete", key=f"delete_{holding_id}"):
                        st.session_state["holding_confirm_delete_id"] = holding_id
                        st.rerun()
                else:
                    st.warning("Delete this holding?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Yes", key=f"confirm_yes_{holding_id}"):
                            if delete_holding(holding_id):
                                st.session_state["holding_confirm_delete_id"] = None
                                st.success(f"Holding #{holding_id} deleted.")
                                st.rerun()
                    with col_no:
                        if st.button("❌ Cancel", key=f"confirm_no_{holding_id}"):
                            st.session_state["holding_confirm_delete_id"] = None
                            st.rerun()


def portfolio_holdings_page():
    init_session_state()

    st.markdown(
        "<h1 style='text-align: center; color: #00ab41;'>Portfolio Holdings</h1>",
        unsafe_allow_html=True,
    )

    render_freshness_banner_and_trigger()
    st.write(" ")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span id="big-btn-dashboard"></span>', unsafe_allow_html=True)
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state["portfolio_mode"] = "dashboard"
            st.rerun()
    with col2:
        st.markdown('<span id="big-btn-manage"></span>', unsafe_allow_html=True)
        if st.button("⚙️ Manage Holdings", use_container_width=True):
            st.session_state["portfolio_mode"] = "manage"
            st.rerun()

    st.divider()

    if st.session_state["portfolio_mode"] == "dashboard":
        render_dashboard_mode()
    else:
        render_manage_holdings_mode()


if __name__ == "__main__":
    portfolio_holdings_page()
