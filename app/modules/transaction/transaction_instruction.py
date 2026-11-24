import streamlit as st  # type: ignore


def account_transfer_instruction():
    st.markdown(
        "<p style='font-size: 20px;'>"
        "<b style='color:#e74c3c;'>Account Transfer</b> moves money between two accounts "
        "while keeping the same fund category. The account changes; the fund stays the same."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>If income or interest arrives in an account, record it first on "
        "<b style='color:yellow;'>Earning Input</b>. If you then need to move that money to another account, "
        "use Account Transfer under the same fund category.</p>",
        unsafe_allow_html=True,
    )
    st.info(
        "Account Transfer is only for moving existing money between accounts. "
        "For a standalone earning, use Earning Input; for a standalone expense, use Expense Input."
    )


def fund_transfer_instruction():
    st.markdown(
        "<p style='font-size: 20px;'>"
        "<b style='color:#e74c3c;'>Fund Transfer</b> moves money between two fund categories "
        "while keeping the same account. The account stays fixed; the funds change."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>One Fund Transfer creates two direction records: a negative "
        "<b>Withdrawal</b> from the source fund and a positive <b>Deposit</b> into the destination fund."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>To correct a fund balance, record any missing income first on "
        "<b style='color:yellow;'>Earning Input</b>, then use Fund Transfer to move the money between funds. "
        "Expense-funded withdrawals are created automatically from the expense record.</p>",
        unsafe_allow_html=True,
    )
    st.info(
        "Fund Transfer is not for a standalone deposit or withdrawal. Use Earning Input for income and "
        "Expense Input for a single expense. For an expense amount, refund, deletion, or fund-allocation "
        "correction, use Expense Editor; linked fund transactions update automatically."
    )
