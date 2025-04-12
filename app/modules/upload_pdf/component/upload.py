import streamlit as st # type: ignore
from typing import List
from streamlit.runtime.uploaded_file_manager import UploadedFile # type: ignore
from utils.css import drop_down_list

def pdf_upload() -> List[UploadedFile]:
    
    drop_down_list()

    
    st.write("")
    
    uploaded_files = st.file_uploader(
        "Upload up to 3 PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader",
    )
  
    if uploaded_files:
        if len(uploaded_files) > 6:
            st.warning(f"You uploaded {len(uploaded_files)} files. Only the newest 6 will be considered.")
            uploaded_files = uploaded_files[:3]

    return uploaded_files