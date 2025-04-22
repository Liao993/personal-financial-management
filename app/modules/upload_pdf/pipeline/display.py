import streamlit as st # type: ignore
import pandas as pd
from modules.upload_pdf.pipeline.load import load_expense_data
import time

def display_editable_dataframe(dataframe):
    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = True
    if 'review_mode' not in st.session_state:
        st.session_state['review_mode'] = False
    if 'edited_df' not in st.session_state:
        st.session_state['edited_df'] = dataframe.copy()

    if st.session_state['edit_mode']:
        st.success("Your data is being processed")
        edited_df = st.data_editor(st.session_state['edited_df'], key="data_editor")
        st.session_state['edited_df'] = edited_df # Update session state immediately on edit

        if st.button("Confirm your changes"):
            st.session_state['edit_mode'] = False
            st.session_state['review_mode'] = True
            st.rerun()
        return None

    if st.session_state['review_mode']:
        st.info("View your information again before saving.")
        st.table(st.session_state['edited_df'])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save"):
               
                done_status = load_expense_data(st.session_state['edited_df'])
                if done_status:
                    st.session_state['edit_mode'] = False
                    st.session_state['review_mode'] = False
                    st.info("Saving your data...")
                    time.sleep(10)
                    return done_status
        with col2:
            if st.button("Edit again"):
                st.session_state['edit_mode'] = True
                st.session_state['review_mode'] = False
            
                st.rerun()
        return None

