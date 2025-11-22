import streamlit as st # type: ignore



def instruction():
    st.markdown(f"<p style='font-size: 20px;'>"
                "If money  <b style='color:#e74c3c;'>Coming In (Income)</b>, "
                "choose <b style='color:#e74c3c;'>deposit</b> and the account name should be <b style='color:#e74c3c;'>RBC chequing</b>. This one should be autoamtically recorded with income input.", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>"
                "If money  <b style='color:#e74c3c;'>Going Out (Expense)</b> (both credit card statement or manual expense input), "
                "choose <b style='color:#e74c3c;'>withdraw</b> and the account money should be <b style='color:#e74c3c;'>the account used for payment</b>.", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>For example, I can pay my credit card with EQ saving account. I may need to make a transfer from EQ to RBC, but I <b style='color:#e74c3c;'>don't need to record it.</b>", unsafe_allow_html=True)
    

    st.markdown(f"<p style='font-size: 20px;'>"
                "If money  <b style='color:#e74c3c;'>Move to saving before bookkeeping</b>, choose <b style='color:#e74c3c;'>transfer between accounts</b>.", unsafe_allow_html=True)
    st.write("___")
    