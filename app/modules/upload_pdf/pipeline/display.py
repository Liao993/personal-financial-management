import streamlit as st
import pandas as pd


def display_editable_dataframe(df: pd.DataFrame) -> pd.DataFrame:
  edited_df = df.copy()
  rows_to_delete = set()

  st.subheader("Editable Data")

  for index, row in df.iterrows():
      col1, col2, col3, col4, col5 = st.columns(5)  # Adjust number of columns based on your DataFrame

      # Display original values (can be replaced with editable inputs)
      with col1:
          st.text_area("Description", row['Description'], key=f"description_{index}")
          edited_df.loc[index, 'Description'] = st.session_state[f"description_{index}"]
      with col2:
          edited_amount = st.number_input("Amount", value=row['Amount'], key=f"amount_{index}")
          edited_df.loc[index, 'Amount'] = edited_amount
      with col3:
          edited_category = st.text_input("Category", row['Category'], key=f"category_{index}")
          edited_df.loc[index, 'Category'] = edited_category
      # Add more columns as needed based on your DataFrame structure

      with col5:
          if st.checkbox("Delete", key=f"delete_{index}"):
              rows_to_delete.add(index)

      st.markdown("---")

  if rows_to_delete:
      st.subheader("Rows to be Deleted")
      st.dataframe(df.loc[list(rows_to_delete)])

      if st.button("Confirm Delete"):
          edited_df = edited_df.drop(list(rows_to_delete)).reset_index(drop=True)
          st.success("Selected rows deleted.")
          st.rerun()

  return edited_df
