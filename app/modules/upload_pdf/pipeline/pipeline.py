import streamlit as st # type: ignore
from modules.upload_pdf.pipeline.rbc.rbc_extracted import rbc_extracted
from modules.upload_pdf.pipeline.rbc.rbc_transformed import rbc_transformed
from modules.upload_pdf.pipeline.display import display_editable_dataframe
from modules.upload_pdf.pipeline.load import load_expense_data


def pipeline(bank, pdf_file):

  st.success("Your data is being processed")

  if bank == "RBC":
    extracted_data = rbc_extracted(pdf_file)
    transformed_data = rbc_transformed(extracted_data)
    st.table(transformed_data)
    #edited_df = display_editable_dataframe(transformed_data)
    #load_expense_data(edited_df)
    
  elif bank == "TD":
      st.write("TD pipeline")

 