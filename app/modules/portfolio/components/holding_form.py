import streamlit as st  # type: ignore
from utils.data import account_name_list

ETF_CATEGORIES = ["Global", "US", "Europe", "Asia", "Bond", "Dividend", "Industry"]
STOCK_CATEGORIES = ["Tech", "Finance", "Consumer", "Healthcare", "Energy", "Dividend"]
PURPOSE_OPTIONS = ["Growth", "Dividend", "Bond"]


def holding_form(edit_mode_key: str, review_data_key: str, prefill: dict = None):
    prefill = prefill or {}

    # BUG FIX (carried from previous session): st.radio with a fixed `key`
    # persists its value in session_state and ignores `index` after the
    # first render. We track which holding the form is bound to, and only
    # reset the radio's stored value when switching to a DIFFERENT holding
    # (or to "new") — normal manual clicks on the radio mid-form still work.
    form_target = prefill.get("id", "new")
    if st.session_state.get("holding_form_bound_to") != form_target:
        st.session_state["holding_form_bound_to"] = form_target
        st.session_state["holding_asset_type_radio"] = prefill.get("asset_type", "ETF")
        prefill_purpose = prefill.get("purpose", "Growth")
        # Both radios get reset on every holding switch — only the one
        # matching the current asset_type is actually shown/used below, the
        # other just sits inert in session_state.
        st.session_state["holding_etf_purpose_radio"] = prefill_purpose
        st.session_state["holding_stock_purpose_radio"] = prefill_purpose

    # Asset Type AND Purpose both live OUTSIDE st.form(), because forms only
    # rerun on submit — but the Dividend-locks-Category behavior needs to
    # update the page live as the user clicks, before they submit. This is
    # now consistent for both ETF and Stock (previously Stock used a plain
    # selectbox inside the form — removed in favor of this radio pattern).
    asset_type = st.radio(
        "Asset Type",
        ["ETF", "Stock"],
        horizontal=True,
        key="holding_asset_type_radio",
    )

    if asset_type == "ETF":
        purpose_outside_form = st.radio(
            "Purpose",
            PURPOSE_OPTIONS,
            horizontal=True,
            key="holding_etf_purpose_radio",
            help="Choosing 'Dividend' will lock ETF Category to Dividend below.",
        )
    else:  # Stock
        purpose_outside_form = st.radio(
            "Purpose",
            PURPOSE_OPTIONS,
            horizontal=True,
            key="holding_stock_purpose_radio",
            help="Choosing 'Dividend' will lock Stock Category to Dividend below.",
        )

    with st.form("holding_form"):
        ticker = st.text_input(
            "Ticker (exchange symbol, e.g. VOO, VT, TSLL, XEQT)",
            value=prefill.get("ticker", ""),
        ).strip().upper()

        account_name = st.selectbox(
            "Account",
            account_name_list,
            index=account_name_list.index(prefill["account_name"])
            if prefill.get("account_name") in account_name_list
            else 0,
        )

        units = st.number_input(
            "Units",
            min_value=0.0001,
            value=float(prefill.get("units", 1.0)),
            format="%.4f",
        )

        currency = st.selectbox(
            "Currency",
            ["CAD", "USD"],
            index=["CAD", "USD"].index(prefill.get("currency", "CAD")),
        )

        etf_category = None
        stock_category = None
        purpose = purpose_outside_form

        if asset_type == "ETF":
            if purpose == "Dividend":
                # Auto-sync: Dividend purpose forces Dividend category.
                # Bond and Growth do NOT force a category — picked freely.
                etf_category = "Dividend"
                st.selectbox(
                    "ETF Category",
                    ["Dividend"],
                    index=0,
                    disabled=True,
                    help="Locked to 'Dividend' because Purpose is set to Dividend.",
                )
            else:
                default_category = (
                    prefill.get("etf_category")
                    if prefill.get("etf_category") in ETF_CATEGORIES
                    else "Global"
                )
                etf_category = st.selectbox(
                    "ETF Category",
                    ETF_CATEGORIES,
                    index=ETF_CATEGORIES.index(default_category),
                    help="Use 'Industry' for leveraged/thematic ETFs that aren't region-based (e.g. TSLL, SOXL).",
                )
        else:  # Stock
            if purpose == "Dividend":
                # Same auto-sync as ETF, mirrored exactly: Dividend purpose
                # forces Stock Category to Dividend too.
                stock_category = "Dividend"
                st.selectbox(
                    "Stock Category",
                    ["Dividend"],
                    index=0,
                    disabled=True,
                    help="Locked to 'Dividend' because Purpose is set to Dividend.",
                )
            else:
                default_category = (
                    prefill.get("stock_category")
                    if prefill.get("stock_category") in STOCK_CATEGORIES
                    else "Tech"
                )
                stock_category = st.selectbox(
                    "Stock Category",
                    STOCK_CATEGORIES,
                    index=STOCK_CATEGORIES.index(default_category),
                )

        notes_input = st.text_input("Notes (Optional)", value=prefill.get("notes") or "")
        notes = notes_input if notes_input else None

        review_button = st.form_submit_button("Review")

        if review_button:
            st.session_state[review_data_key] = {
                "ticker": ticker,
                "asset_type": asset_type,
                "account_name": account_name,
                "units": units,
                "currency": currency,
                "etf_category": etf_category,
                "stock_category": stock_category,
                "purpose": purpose,
                "notes": notes,
            }
            st.session_state[edit_mode_key] = False
            st.rerun()

    return review_button