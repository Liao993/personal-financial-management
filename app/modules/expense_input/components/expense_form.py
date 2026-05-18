import pandas as pd # type: ignore
import streamlit as st # type: ignore
from datetime import date
from utils.css import drop_down_list
from utils.data import expense_category_options, common_store_list, traveling_category_options, payment_method
from modules.expense_input.middle_layer.common_items_combined import common_items_combined
from backend.trip_backend import fetch_all_trips

def expense_form(edit_mode_form, data_saved_key, expense_data_key):

   review_button = False

   with st.form("expense_form"):
      drop_down_list()
      st.markdown("""
      <style>
      /* Target the text inside st.info and st.warning */
      .stAlert p {
         font-size: 22px !important;
      }
      </style>
      """, unsafe_allow_html=True)


      st.warning("If the transaction is not traveling, please exclude those prepaid transactions (wait for people return it) and the amount difference just record gift or income).")
      st.warning("Please exlcude house-related expenses (pre-filtered by the ETL pipeline).")
      st.info("Expenses is used to record my acutal spending including regular expenses and traveling expense.")
      expense_date = st.date_input("Date", value=date.today())
      expense_common_items = st.selectbox("Items", common_store_list, key="common_item_select")
      expense_items = st.text_input("Items (if not in common store list), such as GREAT ENLIGHTENMENT BU MURRAY RIVER PE", key="custom_item_input")
      expense_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=100.00)
      expense_category = st.selectbox("Category", expense_category_options, index=1)
      how_paid = st.selectbox("Payment Method", payment_method, index=1)
      source_notes = st.text_input("Notes (Optional)")
      traveling = st.selectbox("Traveling Category", [None] + traveling_category_options)
     
      existing_trips = fetch_all_trips()
      trip_options = existing_trips + ["Add New Trip"]
      selected_trip = st.selectbox("Select Trip", options=trip_options)
      
      trip_input_new = st.text_input("If 'Add New Trip' is selected, enter here (e.g., Vancouver-Jan25)")
      
      if selected_trip == "Add New Trip":
          trip_input = trip_input_new
      else:
          trip_input = selected_trip
      # The widget will return None until a user enters a value
      amount_for_number_of_travelers = st.number_input(
         "Amount of Travelers", 
         min_value=1, 
         value=None,  # This allows the variable to be None initially
         placeholder="Type a number...",
         step=1
      )

      paid_for_number_of_travlerers = st.number_input(
         "Amount of Travelers I Paid", 
         min_value=0, 
         value=None, 
         placeholder="Type a number...",
         step=1
      )
    
      trip = trip_input if trip_input else None

      #expense items handling
      expense_common_items = st.session_state.get("common_item_select")
      expense_items = st.session_state.get("custom_item_input")
  
      final_expense_items = common_items_combined(expense_common_items, expense_items)

    
      review_button = st.form_submit_button("Review")

      if review_button:
         st.session_state[expense_data_key] = {
            "date" : expense_date,
            "amount":  expense_amount,
            "category": expense_category,
            "items": final_expense_items,
            "payment_method": how_paid,
            "source_notes": source_notes,
            "traveling_category": traveling,
            "trip" : trip,
            "amount_for_number_of_travelers": amount_for_number_of_travelers,
            "paid_for_number_of_travlerers": paid_for_number_of_travlerers
         }
         st.session_state[edit_mode_form] = False
         st.session_state[data_saved_key] = False
         st.rerun()  
   return review_button