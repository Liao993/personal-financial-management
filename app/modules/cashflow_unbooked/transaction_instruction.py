import streamlit as st # type: ignore
from PIL import Image # type: ignore

instruction_text = "This page is used for tracking the unbooked cashflows, so I will know how much I have in RBC chequing or EQ saving accounts while bookkeeping every month."



def instruction():
    st.markdown(f"<p style='font-size: 20px;'>"
                "If money  <b style='color:#e74c3c;'>Coming In (Income)</b>, "
                "choose <b style='color:#e74c3c;'>deposit</b> and the account name should be <b style='color:#e74c3c;'>RBC chequing</b>.", unsafe_allow_html=True)
    st.write("___")
    st.markdown(f"<p style='font-size: 20px;'>"
                "If money  <b style='color:#e74c3c;'>Going Out (Expense)</b> (both credit card statement or manual expense input), "
                "choose <b style='color:#e74c3c;'>withdraw</b> and the account money should be <b style='color:#e74c3c;'>the account used for payment</b>.", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>For example, I can pay my credit card with EQ saving account.", unsafe_allow_html=True)
    
    st.write("___")
    st.markdown(f"<p style='font-size: 20px;'>"
                "If money  <b style='color:#e74c3c;'>Not IN or OUT</b> (move money to saving account <b style='color:#e74c3c;'>before</b> bookkeeping), "
                "choose <b style='color:#e74c3c;'>transfer between accounts</b>.", unsafe_allow_html=True)
    st.write("___")
    