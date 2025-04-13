import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, UpdateMode, GridUpdateMode

def display_editable_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_columns(['Category'], editable=True)
    gb.configure_columns(['Amount'], editable=True)
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group column")
    gridOptions = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=False,
        height=350,
        width='100%',
        reload_data=True
    )

    updated_df = pd.DataFrame(grid_response['data'])
    selected_rows = grid_response['selected_rows']

    if selected_rows:
        st.subheader("Selected Rows for Deletion")
        selected_df = pd.DataFrame(selected_rows)
        st.table(selected_df)

        if st.button("Delete Selected Rows"):
            indices_to_drop = [item['_index'] for item in selected_rows]
            updated_df = updated_df.drop(indices_to_drop).reset_index(drop=True)
            st.success("Selected rows deleted.")
            st.rerun()  # Refresh the app to show the updated table

    return updated_df
