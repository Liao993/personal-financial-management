import streamlit as st  # type: ignore


def instruction():
    st.markdown(
        "<p style='font-size: 20px;'>"
        "Use <b style='color:#e74c3c;'>Account Transfer</b> to move money between accounts "
        "while keeping the same fund category. Use <b style='color:#e74c3c;'>Fund Transfer</b> "
        "to move money between fund categories while keeping the same account.",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>If interest or another earning arrives in TFSA, record it as an earning deposited into TFSA first. "
        "If you then move it to Chequing, use <b>Account Transfer</b> from TFSA to Chequing "
        "under the same fund category.</p>",
        unsafe_allow_html=True,
    )
    st.write("___")
    st.markdown(
        "<p style='font-size: 20px;'>"
        "To correct a fund balance, first record any missing income on <b style='color:yellow;'>Earning Input</b>. "
        "Then use <b>Account Transfer</b> if the money needs to move between accounts, or <b>Fund Transfer</b> "
        "if it needs to move between funds. Expense-funded withdrawals are created automatically from the expense record.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>This page does not record a standalone deposit or withdrawal. "
        "For a normal earning or a single expense, use <b style='color:yellow;'>Earning Input</b> or "
        "<b style='color:yellow;'>Expense Input</b>. A Fund Transfer creates a paired Withdrawal from one fund "
        "and Deposit into another fund.</p>",
        unsafe_allow_html=True,
    )
    st.write("___")
    st.markdown(
        "<p style='font-size: 20px;'>"
        "💡 <b style='color:#5dade2;'>Expense corrections:</b> "
        "For an expense amount, refund, deletion, or fund-allocation change, use the <b>Expense Editor</b>. "
        "Linked fund transactions update automatically. "
        "Use <b>Monthly Saving Calculation</b> to refresh monthly totals when needed.</p>",
        unsafe_allow_html=True,
    )
