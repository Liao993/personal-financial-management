import streamlit as st # type: ignore
import pdfplumber # type: ignore
import re


#This page is used to extract the text from the PDF file
def scotia_red_extracted(pdf_files):
    all_relevant_lines = {}

    if pdf_files:
        for pdf_file_obj in pdf_files:
            relevant_lines = []
            try:
                with pdfplumber.open(pdf_file_obj) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()

                    
                        if text:
                            for line in text.splitlines():
                                if "STATEMENT" in line.upper() and re.search(r"\b20\d{2}\b", line):
                                    relevant_lines.append(line.strip())
                                    continue
                                #line start with "0"
                                if line.startswith("0"):
                                 
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
