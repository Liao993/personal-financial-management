import streamlit as st # type: ignore
import pdfplumber # type: ignore


def rbc_extracted(pdf_files):
    all_relevant_lines = {}  # Dictionary to store relevant lines per filename
    months = ["NOV", "DEC"]
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
                                if '$' in line:
                                    dollar_index = line.find('$')
                                    if dollar_index > -1:  # Ensure '$' is found
                                        prefix = line[:dollar_index].strip().split()
                                        for word in prefix:
                                            if any(month in word for month in months):
                                                relevant_lines.append(line.strip())
                                                break  # Move to the next line once a match is found in the prefix
                                        else:  # Only check after '$' if no month found before
                                            if dollar_index + 1 < len(line):
                                                following_string = line[dollar_index + 1:].strip()
                                                for month in months:
                                                    if following_string.startswith(month):
                                                        relevant_lines.append(line.strip())
                                                        break
                    if relevant_lines:
                        all_relevant_lines[pdf_file_obj.name] = relevant_lines
                    else:
                        all_relevant_lines[pdf_file_obj.name] = "No lines with '$' and 'NOV' or 'DEC' found."
            except Exception as e:
                st.error(f"Error reading PDF {pdf_file_obj.name}: {e}")
                all_relevant_lines[pdf_file_obj.name] = f"Error: {e}"
    else:
        st.warning("No PDF files were uploaded.")
    return all_relevant_lines


