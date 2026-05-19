import streamlit as st # type: ignore
import pandas as pd
import time
import numpy as np
from utils.data import expense_category_options as category_list, traveling_category_options, fund_categories
from modules.upload_pdf.pipeline.load import load_expense_data
from modules.upload_pdf.component.monthly_summary import monthly_summary
from backend.trip_backend import fetch_all_trips


edit_mode_form = 'edit_mode_expense'
data_saved_key = 'data_saved_expense'
review_data = 'review_expense_data'



def display_editable_dataframe(dataframe, bank):
    
   
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
        st.markdown("""
        <style>
        .stAlert p {
           font-size: 20px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:22px; color: #ff9900; padding: 6px; border-radius: 5px;">📍 Traveling Section</div>', unsafe_allow_html=True)
        st.write("Please input your trip below!")
        single_trip = st.checkbox("Single Trip", value=True)
        
        existing_trips = fetch_all_trips()
        
        trip_options = existing_trips + ["Add New Trip"]
        selected_trip = st.selectbox("Select Trip", options=trip_options)
        
        if selected_trip == "Add New Trip":
            trip_input = st.text_input("Trip-MonthYear (e.g., Vancouver-012025)")
        else:
            trip_input = selected_trip
            
        st.markdown('<div style="font-size:28px; color: #ff9900; padding: 10px; border-radius: 5px;">📊 PDF Data Editor</div>', unsafe_allow_html=True)
        st.warning("⚠️ Please exclude House-related expenses!")
        
        # Initialize boolean columns if they don't exist
        if 'exclude_from_monthly' not in st.session_state[review_data].columns:
            st.session_state[review_data]['exclude_from_monthly'] = False
        if 'is_prepaid' not in st.session_state[review_data].columns:
            st.session_state[review_data]['is_prepaid'] = False
        if 'target_fund_category' not in st.session_state[review_data].columns:
            st.session_state[review_data]['target_fund_category'] = None
        if 'split_fund_category_1' not in st.session_state[review_data].columns:
            st.session_state[review_data]['split_fund_category_1'] = None
        if 'split_amount_1' not in st.session_state[review_data].columns:
            st.session_state[review_data]['split_amount_1'] = 0.0
        if 'split_fund_category_2' not in st.session_state[review_data].columns:
            st.session_state[review_data]['split_fund_category_2'] = None
        if 'split_amount_2' not in st.session_state[review_data].columns:
            st.session_state[review_data]['split_amount_2'] = 0.0

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
                "exclude_from_monthly": st.column_config.CheckboxColumn(
                    "Fund Withdrawal Required",
                    help="Fund Withdrawal Required (this amount will be excluded from monthly expense). Auto-checked if you set a Target Fund.",
                    default=False,
                ),
                "is_prepaid": st.column_config.CheckboxColumn(
                    "Is Prepaid",
                    help="Is Prepaid: check this box if I need to withdraw from the fund category first and get this money back after the bookkeeping. Record Deposit in the transaction page after getting money back.",
                    default=False,
                ),
                "target_fund_category": st.column_config.SelectboxColumn(
                    "Primary Target Fund",
                    help="Primary Target Fund Category — set this to auto-create a withdrawal transaction. Leave blank for regular monthly spending (no transaction created).",
                    options=[None] + fund_categories,
                    default=None,
                ),
                "split_fund_category_1": st.column_config.SelectboxColumn(
                    "Secondary Target Fund",
                    help="Secondary Target Fund (Split Allocation) — optional. The remainder after split goes to the Primary Target Fund.",
                    options=[None] + fund_categories,
                    default=None,
                ),
                "split_amount_1": st.column_config.NumberColumn(
                    "Amount (Secondary)",
                    help="Amount to allocate to Secondary Target Fund. The rest (total - secondary - tertiary) goes to Primary.",
                    default=0.0,
                    format="%.2f",
                ),
                "split_fund_category_2": st.column_config.SelectboxColumn(
                    "Tertiary Target Fund",
                    help="Tertiary Target Fund (Split Allocation) — optional third bucket.",
                    options=[None] + fund_categories,
                    default=None,
                ),
                "split_amount_2": st.column_config.NumberColumn(
                    "Amount (Tertiary)",
                    help="Amount to allocate to Tertiary Target Fund.",
                    default=0.0,
                    format="%.2f",
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
            reviewed_data_dict = st.session_state[review_data]
            
            st.table(reviewed_data_dict)  
            
            monthly_summary(reviewed_data_dict)
           
         
            #Confirm and Edit buttons
            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Save your information")
            with col2:
                edit_button = st.button("Edit your information")
            #Validate Data and Save Data after clicking confirm button
            if confirm_button:
                data_to_saved = reviewed_data_dict
                st.info("Saving your information...")
                if load_expense_data(data_to_saved, bank):
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


