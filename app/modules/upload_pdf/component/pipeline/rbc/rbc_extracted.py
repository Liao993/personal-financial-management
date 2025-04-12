import streamlit as st # type: ignore
import pdfplumber # type: ignore
import re

def rbc_extracted(pdf_files):
    all_relevant_lines = {}
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    if pdf_files:
        for pdf_file_obj in pdf_files:
            st.write(f"Processing file: {pdf_file_obj.name}")
            relevant_lines = []
            try:
                with pdfplumber.open(pdf_file_obj) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            for line in text.splitlines():
                                if '$' in line and any(month in line for month in months):
                                    relevant_lines.append(line.strip())
                    if relevant_lines:
                        all_relevant_lines[pdf_file_obj.name] = relevant_lines
                    else:
                        all_relevant_lines[pdf_file_obj.name] = "No relevant lines found."
            except Exception as e:
                st.error(f"Error reading PDF {pdf_file_obj.name}: {e}")
                all_relevant_lines[pdf_file_obj.name] = f"Error: {e}"
    else:
        st.warning("No PDF files were uploaded.")
    return all_relevant_lines
