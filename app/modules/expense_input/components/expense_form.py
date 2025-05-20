import pandas as pd
import streamlit as st # type: ignore
from datetime import date
from utils.css import drop_down_list
from utils.data import expense_category_options, common_store_list, traveling_category_options
from modules.expense_input.middle_layer.common_items_check import common_items_check

def expense_form(edit_mode_form, data_saved_key, expense_data_key):

   review_button = False

   with st.form("expense_form"):
      drop_down_list()
      expense_date = st.date_input("Date", value=date.today())
      expense_common_items = st.selectbox("Items", common_store_list, key="common_item_select")
      expense_items = st.text_input("Items (if not in common store list)", key="custom_item_input")
      expense_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=100.00)
      expense_category = st.selectbox("Category", expense_category_options, index=1)
      traveling = st.selectbox("Traveling Category", [None] + traveling_category_options)
      trip_input = st.text_input("Trip-Year-Month (e.g., Vancouver-Jan25)")
      trip = trip_input if trip_input else None

      #expense items handling
      expense_common_items = st.session_state.get("common_item_select")
      expense_items = st.session_state.get("custom_item_input")
  
      final_expense_items = common_items_check(expense_common_items, expense_items)

    
      review_button = st.form_submit_button("Review")

      if review_button:
         st.session_state[expense_data_key] = {
            "date" : expense_date,
            "amount":  expense_amount,
            "category": expense_category,
            "items": final_expense_items,
            "traveling_category": traveling,
            "trip" : trip
         }
         st.session_state[edit_mode_form] = False
         st.session_state[data_saved_key] = False
         st.rerun()  
   return review_button