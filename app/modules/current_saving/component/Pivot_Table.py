import streamlit as st # type: ignore
import pandas as pd # type: ignore
from utils.data import fund_categories, account_name_list
from utils.css import apply_pivot_table_style


# These are presentation labels only. Transaction and portfolio records keep
# their canonical account names so account filtering and reconciliation remain
# unchanged.
ACCOUNT_DISPLAY_NAMES = {
    "EQ 10D Notice": "EQ 10D",
    "EQ 30D Notice": "EQ 30D",
    "Questrade TFSA (Travel)": "Quest TFSA (Travel)",
    "Questrade TFSA (Retire)": "Quest TFSA (Retire)",
    "Questrade TFSA (Medium)": "Quest TFSA (Medium)",
    "Questrade RRSP (Medium)": "Quest RRSP (Medium)",
    "Moomoo RRSP (Retire)": "Moo RRSP (Retire)",
}

# EQ TFSA remains a valid source account, but is intentionally omitted from
# this compact matrix to keep the current-savings view readable.
HIDDEN_PIVOT_ACCOUNTS = {"EQ TFSA", "Questrade RRSP (Retire)"}
QUESTRADE_ACCOUNT_ORDER = {
    "Questrade TFSA (Travel)": 0,
    "Questrade TFSA (Medium)": 1,
    "Questrade TFSA (Retire)": 2,
    "Questrade RRSP (Medium)": 3,
}


def _order_pivot_accounts(accounts: list[str]) -> list[str]:
    """Keep provider groups together while preserving configured order."""
    first_questrade = next(
        (index for index, account in enumerate(accounts) if "Questrade" in account),
        None,
    )
    if first_questrade is None:
        return accounts

    before = [
        account
        for account in accounts[:first_questrade]
        if "Questrade" not in account
    ]
    questrade = sorted(
        (account for account in accounts if "Questrade" in account),
        key=lambda account: QUESTRADE_ACCOUNT_ORDER.get(account, 99),
    )
    after = [
        account
        for account in accounts[first_questrade:]
        if "Questrade" not in account
    ]
    return before + questrade + after


def build_pivot_table(data: pd.DataFrame) -> pd.DataFrame:
    """Build the current-savings matrix without changing source account names."""
    pivot_df = pd.pivot_table(
        data,
        values="amount",
        index="fund_category",
        columns="account_name",
        aggfunc="sum",
        fill_value=0,
    )

    display_accounts = [
        account
        for account in account_name_list
        if account not in HIDDEN_PIVOT_ACCOUNTS
    ]
    display_accounts = _order_pivot_accounts(display_accounts)
    pivot_df = pivot_df.reindex(fund_categories, fill_value=0)
    pivot_df = pivot_df.reindex(columns=display_accounts, fill_value=0)
    pivot_df = pivot_df.rename(columns=ACCOUNT_DISPLAY_NAMES)

    pivot_df["Total"] = pivot_df.sum(axis=1)
    pivot_df.loc["Total"] = pivot_df.sum(axis=0)
    return pivot_df.reset_index()


def Pivot_Table(data):
    pivot_df = build_pivot_table(data)

    # --- Apply Styling for Total Row and Column ---
    styled_df = apply_pivot_table_style(pivot_df)

    st.caption("Account labels are shortened for display only; source account names are unchanged.")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
