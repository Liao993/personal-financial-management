import streamlit as st # type: ignore
from modules.upload_pdf.component.upload import pdf_upload # type: ignore
from modules.upload_pdf.pipeline import pipeline # type: ignore

st.set_page_config(page_title="Upload Expense", page_icon="💸", layout='wide')

def upload_expense():
    st.title("Upload Your Expenses PDF Here")

    if 'upload_pdf_state' not in st.session_state:
        st.session_state['upload_pdf_state'] = True
        st.session_state['uploaded_pdf'] = []
        st.session_state['selected_action'] = None
   

    if st.session_state['upload_pdf_state']:
        action_options = ["RBC", "TD", "WISE", "CIBC"]
        st.session_state['selected_action'] = st.selectbox("Which Bank for your statements?", action_options)
        uploaded_pdf = pdf_upload()
        if uploaded_pdf: 
            st.session_state['uploaded_pdf'] = uploaded_pdf
          

        if st.button("Submit"):
            st.session_state['upload_pdf_state'] = False
            st.rerun()
    else:
        pipeline(st.session_state['selected_action'], st.session_state['uploaded_pdf'])
        # remove cached data
        if 'uploaded_pdf' in st.session_state:
            del st.session_state['uploaded_pdf']

   
    

if __name__ == "__main__":
    upload_expense()
   
