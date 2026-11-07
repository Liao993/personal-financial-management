import streamlit as st  # type: ignore


def instruction():
    st.markdown(
        "<p style='font-size: 20px;'>"
        "This page records <b style='color:#e74c3c;'>account transfers only</b>. "
        "Incoming money must first be recorded as an earning on the <b style='color:yellow;'>Earning Input</b> page.",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>If interest or another earning arrives in TFSA, record it as an earning deposited into TFSA first. "
        "If you then move it to Chequing, record one transfer from TFSA to Chequing under the same fund category.</p>",
        unsafe_allow_html=True,
    )
    st.write("___")
    st.markdown(
        "<p style='font-size: 20px;'>"
        "If you need to correct a fund balance, record the missing earning first, then transfer it between accounts if needed. "
        "Expense-funded withdrawals are created automatically from the expense record.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>There is no separate Deposit or Withdrawal action here. For an expense amount or fund allocation change, "
        "use <b style='color:yellow;'>Expense Editor (Page 16)</b>; linked fund transactions update automatically.</p>",
        unsafe_allow_html=True,
    )
    st.write("___")
    st.markdown(
        "<p style='font-size: 20px;'>"
        "💡 <b style='color:#5dade2;'>Refunds and edits:</b> "
        "Use the <b>Expense Editor (Page 16)</b> to update or delete expenses. "
        "Linked fund transactions update automatically. "
        "Then use <b>Rerun Calculation (Page 6)</b> if the month's saving totals need refreshing.</p>",
        unsafe_allow_html=True,
    )
