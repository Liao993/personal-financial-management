import streamlit as st # type: ignore
import pandas as pd
import time
import numpy as np
from utils.data import expense_category_options as category_list, traveling_category_options
from modules.upload_pdf.pipeline.load import load_expense_data

edit_mode_form = 'edit_mode_expense'
data_saved_key = 'data_saved_expense'
review_data = 'review_expense_data'



def display_editable_dataframe(dataframe):
   
    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    # data saved or not
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False
    # catch review data
    if review_data not in st.session_state:
        st.session_state[review_data] = dataframe
    
     # Add "Not Categorized" option
    if "Not Categorized" not in category_list:
        category_list.append("Not Categorized")

 

     # if it is in edit mode, show the form
    if st.session_state[edit_mode_form]:
        st.success("Your data is being processed")
        st.write("Please input your trip below!")
        single_trip = st.checkbox("Single Trip", value=True)
        trip_input = st.text_input("Trip-Year-Month (e.g., Vancouver-24-01)")
        st.warning("Please exclude house related expenses!")
        edited_df = st.data_editor(
            st.session_state[review_data],
            column_config={
                 "date": st.column_config.DateColumn(  # Use DateColumn for display
                    "Date",
                    format="YYYY-MM-DD",  # Set the display format
                    required=True
                ),
                 "category": st.column_config.SelectboxColumn(
                    "category",
                    options=category_list if category_list else dataframe["category"].unique(),
                    required=True,
                ),
                "traveling_category": st.column_config.SelectboxColumn(  # Add traveling_category
                "Traveling Category",  # Label for the column
                options=[None] + traveling_category_options,  # Use your options, include None
                required=False,  # traveling_category is not required
                ),
            } if category_list else None,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
           
        )

        
        if st.button("Confirm your changes"):
            if single_trip:
                # 4.  Use .loc to correctly assign the 'trip' value based on the 'category'.
                edited_df.loc[edited_df['category'] == 'Traveling', 'trip'] = trip_input
                # 5.  For other categories,  it is better to assign a value, such as 'None'
                edited_df.loc[edited_df['category'] != 'Traveling', 'trip'] = None
            else:
                edited_df

            st.info("Loading your information...")
            st.session_state[review_data] = edited_df
            st.session_state[edit_mode_form] = False
            st.session_state[data_saved_key] = False
            st.rerun()

    # The rest of your review mode logic remains the same
    else:
        if not st.session_state.get(data_saved_key, False):
            st.info("View your information again before saving.")
            reviewed_data = st.session_state[review_data]
            st.table(reviewed_data)  # Use st.session_state['edited_df'] here
            #Confirm and Edit buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                confirm_button = st.button("Save your information")
            with col2:
                edit_button = st.button("Edit your information")
            
            #Validate Data and Save Data after clicking confirm button
            if confirm_button:
                data_to_saved = reviewed_data
                st.info("Saving your information...")
                if load_expense_data(data_to_saved):
                    st.session_state[data_saved_key] = True
                    st.rerun()
                else:
                    pass
            # Back to form to edit information
            if edit_button:
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        elif st.session_state.get(data_saved_key, True):
            st.success("Expense data from your statement successfully saved! Moving back to upload page.")
            time.sleep(6)
            return True


