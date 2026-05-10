import streamlit as st # type: ignore
from PIL import Image # type: ignore




def instruction():
    st.markdown(f"<p style='font-size: 20px;'>"
                "If money balance BETWEEN <b style='color:#e74c3c;'>DIFFERENT FUNDS</b>, "
                "choose <b style='color:#e74c3c;'>deposit</b>  or  <b style='color:#e74c3c;'>withdraw</b>,", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>Example: From Medium-term Saving to Traveling Funds, please make <b style='color:orange'>'TWO'</b> transactions. "
                " Choose <b style='color:#e74c3c;'>Withdrawal</b> for Medium-term and <b style='color:#e74c3c;'>Deposit</b> for Traveling Funds</p>", unsafe_allow_html=True)
    st.write("___")
    st.markdown(f"<p style='font-size: 20px;'>"
               "if it is the <b style='color:yellow;'>same funds</b> but in different accounts, "
                "choose <b style='color:yellow;'>transfer between accounts.</b></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>Example: Retirement Saving From RBC Chequing  to Questrade TFSA (Retire), please make <b style='color:orange'>'ONE'</b> transaction."
                " Choose <b style='color:yellow;'>Transfer Between Accounts</b> for Retirement Saving</p>", unsafe_allow_html=True)
    st.write("___")
    st.markdown(f"<p style='font-size: 20px;'>If I want to withdraw money from TFSA <b style='color:orange'>more than</b> the amount I deposited, please make a <b style='color:orange'>deposit</b> to that TFSA account for matching the total amount. Interest earning don't need to record as earning.</p>", unsafe_allow_html=True)
 
    st.write("___")
    st.markdown(f"<p style='font-size: 20px;'>If I help other to prepaid spending in traveling, please make a <b style='color:orange'>deposit</b>  and a <b style='color:orange'>withdraw</b> transactions with <b style='color:orange'>prepaid click</b></p>", unsafe_allow_html=True)
