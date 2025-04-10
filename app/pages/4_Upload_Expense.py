import streamlit as st
from modules.upload_pdf.component.upload import pdf_upload

def upload_expense():
    st.title("Upload Expense PDF Here")
    pdf_upload()
 

if __name__ == "__main__":
    upload_expense()
   
