import streamlit as st # type: ignore
from modules.upload_pdf.component.upload import pdf_upload # type: ignore
from modules.upload_pdf.pipeline.pipeline import pipeline # type: ignore

st.set_page_config(page_title="Upload Expense", page_icon="💸", layout='wide')

def upload_expense():

    st.markdown("<h1 style='color: #e74c3c; text-align: center;'>Upload Your Expenses PDF Here</h1>", unsafe_allow_html=True)

    with st.expander("📋 Quick Reference Notes (click to expand)", expanded=False):
        st.markdown("""
        | Topic | Note |
        |---|---|
        | 📁 **File Name** | Don't rename the PDF — the filename is used to extract the statement year. |
        | 🏠 **House Expenses** | Exclude house-related items (pre-filtered by the ETL pipeline). |
        | ✈️ **Traveling Rows** | Set the Trip and Traveling Category in the data editor for traveling rows. |
        | 💰 **Fund Withdrawal** | Set a Primary Target Fund in the editor to auto-create a withdrawal from RBC Chequing. |
        | 🔄 **Is Prepaid** | If someone owes you money, exclude it here — record as Gift for amount difference or no record it. |
        """)

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
   
