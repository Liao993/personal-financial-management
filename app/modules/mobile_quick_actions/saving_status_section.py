import streamlit as st  # type: ignore
import pandas as pd  # type: ignore

from utils.data import fund_categories
from backend.transaction_backend import (
    fetch_all_transaction_data,
    fetch_expense_withdrawal_transactions,
)


def _combine_expense_withdrawals(
    transaction_data: pd.DataFrame, expense_withdrawals: pd.DataFrame
) -> pd.DataFrame:
    """
    Mirrors the combination step used on the desktop Current Saving Status
    page (Page 10) so totals shown here always match. Kept as a local copy
    since page files aren't easily importable as modules in Streamlit's
    multi-page structure — if Page 10's version changes, update this too,
    or consider moving both to a shared module under app/modules/.
    """
    if expense_withdrawals.empty:
        return transaction_data
    expense_txn_for_sum = expense_withdrawals[
        ["date", "account_name", "amount", "fund_category", "transaction_type"]
    ].copy()
    return pd.concat([transaction_data, expense_txn_for_sum], ignore_index=True)


def render_saving_status_section():
    st.subheader("📊 Saving Status")

    columns_names, all_transaction_data = fetch_all_transaction_data()
    transaction_data = pd.DataFrame(all_transaction_data, columns=columns_names)
    expense_withdrawals = fetch_expense_withdrawal_transactions()
    combined = _combine_expense_withdrawals(transaction_data, expense_withdrawals)

    if combined.empty or "account_name" not in combined.columns:
        st.info("No transaction data yet.")
        return

    def total_for(keyword):
        matched = combined[
            combined["account_name"].str.contains(keyword, case=False, na=False)
        ]
        return matched["amount"].sum()

    def current_year_deposit_for(keyword):
        required_columns = {"account_name", "amount", "date", "transaction_type"}
        if not required_columns.issubset(combined.columns):
            return 0.0

        current_year = pd.Timestamp.today().year
        data = combined.copy()
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
        data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0)

        matched = data[
            data["account_name"].str.contains(keyword, case=False, na=False)
            & (data["date"].dt.year == current_year)
            & data["transaction_type"].isin(["Deposit", "Transfer In"])
        ]
        return matched["amount"].sum()

    chequing_total = total_for("Chequing")
    notice_total = total_for("Notice")
    tfsa_total = total_for("TFSA")
    rrsp_total = total_for("RRSP")
    tfsa_current_year_deposit = current_year_deposit_for("TFSA")
    rrsp_current_year_deposit = current_year_deposit_for("RRSP")

    st.markdown("**By Account**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Chequing", f"${chequing_total:,.2f}")
    with col2:
        st.metric("Notice Savings", f"${notice_total:,.2f}")

    col3, col4 = st.columns(2)
    with col3:
        st.metric("TFSA", f"${tfsa_total:,.2f}")
    with col4:
        st.metric("RRSP", f"${rrsp_total:,.2f}")

    current_year = pd.Timestamp.today().year
    st.markdown(f"**{current_year} Deposits**")
    col5, col6 = st.columns(2)
    with col5:
        st.metric("TFSA Deposit", f"${tfsa_current_year_deposit:,.2f}")
    with col6:
        st.metric("RRSP Deposit", f"${rrsp_current_year_deposit:,.2f}")

    st.divider()
    st.markdown("**By Fund Category**")

    if "fund_category" in combined.columns:
        fund_totals = combined.groupby("fund_category")["amount"].sum()
    else:
        fund_totals = pd.Series(dtype="float64")

    # Walk fund_categories (from utils.data, driven by the FUND_CATEGORIES
    # env var) two at a time, so every configured category always shows —
    # including ones with $0 / no transactions yet — rather than only
    # categories that happen to already have rows.
    for i in range(0, len(fund_categories), 2):
        row_categories = fund_categories[i : i + 2]
        cols = st.columns(len(row_categories))
        for col, category in zip(cols, row_categories):
            with col:
                amount = fund_totals.get(category, 0.0)
                st.metric(category, f"${amount:,.2f}")
