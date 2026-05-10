import streamlit as st # type: ignore
from modules.upload_pdf.component.upload import pdf_upload # type: ignore
from modules.upload_pdf.pipeline.pipeline import pipeline # type: ignore

st.set_page_config(page_title="Upload Expense", page_icon="💸", layout='wide')

def upload_expense():

    st.markdown("<h1 style='color: #e74c3c; text-align: center;'>Upload Your Expenses PDF Here</h1>", unsafe_allow_html=True)
    st.markdown("""
      <style>
      /* Target the text inside st.info and st.warning */
      .stAlert p {
         font-size: 24px !important;
      }
      </style>
      """, unsafe_allow_html=True)
    st.warning("Don't change the name of the file, it will be used to catch the year.")
    st.warning("Please exclude prepaid transactions (wait for people return it and the amount difference just record gift or income) and house-related expenses (pre-filtered by the ETL pipeline).")
    st.info("Expenses is used to record my acutal spending including regular expenses and traveling expense.")

    if 'upload_pdf_state' not in st.session_state:
        st.session_state['upload_pdf_state'] = True
        st.session_state['uploaded_pdf_files_list'] = []
        st.session_state['selected_action'] = None

    

    if st.session_state['upload_pdf_state']:
        action_options = ["RBC", "PC", "Scotia_Red"]
        st.session_state['selected_action'] = st.selectbox("Which Bank for your statements?", action_options)
        uploaded_pdf = pdf_upload()
        if uploaded_pdf: 
            st.session_state['uploaded_pdf_files_list'] = uploaded_pdf
            st.success(f"Uploaded {len(uploaded_pdf)} file(s).")
          

        if st.button("Submit"):
            st.session_state['upload_pdf_state'] = False
            st.rerun()
    else:
        if st.session_state.get('uploaded_pdf_files_list'):
            done = pipeline(st.session_state['selected_action'], st.session_state['uploaded_pdf_files_list'])
            if done:
                #del first
                if 'uploaded_pdf_files_list' in st.session_state:
                    del st.session_state['uploaded_pdf_files_list']
                st.session_state['upload_pdf_state'] = True # Go back to upload state
                st.rerun() # Trigger the re-render to show the upload section again
   
    

if __name__ == "__main__":
    upload_expense()
   
