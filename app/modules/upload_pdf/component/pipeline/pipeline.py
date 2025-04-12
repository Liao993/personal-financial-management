import streamlit as st
from modules.upload_pdf.component.pipeline.rbc.rbc_extracted import rbc_extracted
from modules.upload_pdf.component.pipeline.rbc.rbc_transformed import rbc_transformed

def pipeline(bank, pdf_file):

  st.success("Your data is being processed")

  if bank == "RBC":
      extracted_data = rbc_extracted(pdf_file)
      transformed_data = rbc_transformed(extracted_data)
      st.table(transformed_data)
  elif bank == "TD":
      st.write("TD pipeline")

 