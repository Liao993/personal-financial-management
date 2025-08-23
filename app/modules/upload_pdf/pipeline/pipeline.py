import streamlit as st # type: ignore
from modules.upload_pdf.pipeline.rbc.rbc_extracted import rbc_extracted
from modules.upload_pdf.pipeline.rbc.rbc_transformed import rbc_transformed
from modules.upload_pdf.pipeline.display import display_editable_dataframe


def pipeline(bank, pdf_file):



  if bank == "RBC":
    extracted_data = rbc_extracted(pdf_file)
    transformed_data = rbc_transformed(extracted_data)
    finished = display_editable_dataframe(transformed_data)
    return finished
  elif bank == "PC":
    extracted_data = rbc_extracted(pdf_file)
    transformed_data = rbc_transformed(extracted_data)
    finished = display_editable_dataframe(transformed_data)



 