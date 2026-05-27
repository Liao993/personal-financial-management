import streamlit as st  # type: ignore


def instruction():
    st.markdown(
        "<p style='font-size: 20px;'>"
        "If money balance moves <b style='color:#e74c3c;'>BETWEEN DIFFERENT FUNDS</b>, "
        "choose <b style='color:#e74c3c;'>Deposit</b> or <b style='color:#e74c3c;'>Withdrawal</b>.",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>Example: From Medium-term Saving to Traveling Funds — "
        "make <b style='color:orange'>TWO</b> transactions. "
        "<b style='color:#e74c3c;'>Withdrawal</b> from Medium-term, "
        "<b style='color:#e74c3c;'>Deposit</b> to Traveling Funds.</p>",
        unsafe_allow_html=True,
    )
    st.write("___")
    st.markdown(
        "<p style='font-size: 20px;'>"
        "If it is the <b style='color:yellow;'>same fund</b> but in different accounts, "
        "choose <b style='color:yellow;'>Transfer Between Accounts</b>.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 20px;'>Example: Retirement Saving from RBC Chequing to Questrade TFSA — "
        "make <b style='color:orange'>ONE</b> transaction. "
        "Choose <b style='color:yellow;'>Transfer Between Accounts</b>.</p>",
        unsafe_allow_html=True,
    )
    st.write("___")
    st.markdown(
        "<p style='font-size: 20px;'>"
        "If you want to withdraw from TFSA <b style='color:orange'>more</b> than you deposited, "
        "first record a <b style='color:orange'>Deposit</b> to that TFSA account to match the total. "
        "Interest earnings do not need to be recorded as income.</p>",
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
