import streamlit as st
from modules.upload_pdf.component.pipeline.rbc.rbc_extracted import rbc_extracted


def pipeline(bank, pdf_file):
  st.success("Your data is being processed")
  for file in pdf_file:
    st.info(f"Processing file before extracted: {file.name}")
  if bank == "RBC":
    extracted_data = rbc_extracted(pdf_file)
    if extracted_data:
        for filename, text in extracted_data.items():
            st.subheader(f"Content of {filename}:")
            st.text_area("PDF Text", text, height=300)
    #transfromed_data = rbc_transformed(extracted_data)
    #displayed_data = rbc_display(transfromed_data)
    #loaded_data = rbc_load(displayed_data)

  elif bank == "TD":
    st.write("TD pipeline")