import streamlit as st  # type: ignore
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from utils.data import account_name_list, fund_categories
from modules.transaction.transaction_review import record_saving_transaction


def build_fund_transfer_transactions(
    transaction_date,
    account_name: str,
    fund_moving_out: str,
    fund_moving_in: str,
    amount: float | Decimal,
    source_notes: str | None = None,
) -> list[dict]:
    """Build the two schema-compatible rows for one fund transfer."""
    if fund_moving_out == fund_moving_in:
        raise ValueError("Fund Moving Out and Fund Moving In must be different.")
    amount_decimal = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if amount_decimal <= Decimal("0.00"):
        raise ValueError("Fund transfer amount must be greater than zero.")

    note_suffix = f" {source_notes.strip()}" if source_notes and source_notes.strip() else ""
    return [
        {
            "transaction_date": transaction_date,
            "account_name": account_name,
            "transaction_type": "Withdrawal",
            "amount": -amount_decimal,
            "fund_category": fund_moving_out,
            "source_notes": f"Fund transfer to {fund_moving_in}.{note_suffix}",
        },
        {
            "transaction_date": transaction_date,
            "account_name": account_name,
            "transaction_type": "Deposit",
            "amount": amount_decimal,
            "fund_category": fund_moving_in,
            "source_notes": f"Fund transfer from {fund_moving_out}.{note_suffix}",
        },
    ]


def fund_transfer_form():
    """Record a movement between two funds while keeping the account fixed."""
    form_version = st.session_state.get("transaction_form_version", 0)

    st.subheader(
        "Record Fund Transfer: move money between funds within one account."
    )
    st.caption(
        "The account stays the same. The source fund is recorded as a Withdrawal "
        "and the destination fund as a Deposit."
    )

    if len(account_name_list) == 0:
        st.error("No accounts are configured. Add an account before recording a fund transfer.")
        return
    if len(fund_categories) < 2:
        st.error("At least two fund categories are required for a fund transfer.")
        return

    transaction_date = st.date_input(
        "Transaction Date",
        datetime.now().date(),
        key=f"fund_transfer_date_{form_version}",
    )
    account_name = st.selectbox(
        "Account",
        account_name_list,
        key=f"fund_transfer_account_{form_version}",
    )
    fund_moving_out = st.selectbox(
        "Fund Moving Out",
        fund_categories,
        key=f"fund_transfer_out_{form_version}",
    )
    fund_moving_in = st.selectbox(
        "Fund Moving In",
        fund_categories,
        index=1,
        key=f"fund_transfer_in_{form_version}",
    )
    amount = st.number_input(
        "Amount",
        min_value=0.0,
        step=0.01,
        format="%.2f",
        key=f"fund_transfer_amount_{form_version}",
    )
    source_notes = st.text_input(
        "Notes (Optional)",
        key=f"fund_transfer_notes_{form_version}",
    )

    if st.button("Record Fund Transfer"):
        try:
            transactions = build_fund_transfer_transactions(
                transaction_date,
                account_name,
                fund_moving_out,
                fund_moving_in,
                amount,
                source_notes,
            )
        except ValueError as exc:
            st.error(str(exc))
            return

        for transaction in transactions:
            record_saving_transaction(
                transaction["transaction_date"],
                transaction["account_name"],
                transaction["transaction_type"],
                transaction["amount"],
                transaction["fund_category"],
                source_notes=transaction["source_notes"],
            )
        st.session_state["show_the_form"] = False
        st.rerun()
