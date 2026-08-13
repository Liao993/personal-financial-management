import streamlit as st # type: ignore
from typing import List
from streamlit.runtime.uploaded_file_manager import UploadedFile # type: ignore
from utils.css import drop_down_list

def pdf_upload() -> List[UploadedFile]:
    
    drop_down_list()

    
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader",
    )

    return uploaded_files
