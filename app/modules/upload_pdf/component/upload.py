import streamlit as st # type: ignore
from typing import List
from streamlit.runtime.uploaded_file_manager import UploadedFile # type: ignore

def pdf_upload() -> List[UploadedFile]:
    
    st.subheader("Upload PDF Documents (Max 5)")

    action_options = ["View File Names", "Process with Script A", "Process with Script B", "Process with Script C"]
    selected_action = st.selectbox("Select an action for the uploaded PDFs:", action_options)
    
    
    uploaded_files = st.file_uploader(
        "Upload up to 5 PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader",
    )
  
    if uploaded_files:
        if len(uploaded_files) > 5:
            st.warning(f"You uploaded {len(uploaded_files)} files. Only the first 5 will be considered.")
            uploaded_files = uploaded_files[:5]

    if st.button("Submit"):
        st.write("---")
        st.info(f"Selected Action: {selected_action}")
        st.subheader("Uploaded Files:")
        for file in uploaded_files:
            st.write(f"- {file.name}")
   

    return uploaded_files