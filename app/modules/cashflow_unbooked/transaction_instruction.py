import streamlit as st # type: ignore
from PIL import Image # type: ignore

instruction_text = "After completing the monthly bookkeeping, the funds should be moved from RBC chequing to various accounts. \
        However, the actual transfer needs to be moved first based on the amounts in the 10-day account first."



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
 
    st.markdown(f"<p style='font-size: 20px;'>Monthly Transaction Instructions:</p>", unsafe_allow_html=True)
    instruction_image = Image.open("utils/images/instructions.png")
    st.image(instruction_image, caption='Monthly Transaction Instructions.', use_container_width=True)
    st.write("___")

    st.markdown(f"<p style='font-size: 20px;'>Other Transaction Instructions: </p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>When All Traveling Amounts are bookkept, please move the amount out from 10 days or 30 days to Chequing. Otherwise, the amount in RBC chequing will not be enough.</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>All Credit Card Payments should be transfered out from RBC Chequing or TD account (for house payment). Therefore, No transaction bookingkeeping involved.</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>If I over-deposit the money into notice account, just need to move the extra deposit in that month, NOT the amount the credit card statements. No transaction bookingkeeping involved.</p>", unsafe_allow_html=True)
    st.write("___")