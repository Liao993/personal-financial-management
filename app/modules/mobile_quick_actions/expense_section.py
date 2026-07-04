import streamlit as st  # type: ignore
from datetime import date

from utils.data import expense_category_options, common_store_list, payment_method
from utils.validation import validate_expense_data
from backend.expense_backend import insert_expense_data
from modules.expense_input.middle_layer.common_items_combined import common_items_combined

# "Traveling" is excluded here — trip expenses need trip/traveler details
# that don't fit this condensed mobile form. Use the full Manual Expense
# Input page on desktop for those.
EXPENSE_CATEGORY_OPTIONS_QUICK = [c for c in expense_category_options if c != "Traveling"]


def render_expense_section():
    st.subheader("🧾 Quick Expense")
    with st.form("mobile_expense_form"):
        expense_date = st.date_input("Date", value=date.today(), key="mobile_expense_date")
        common_item = st.selectbox(
            "Store (if common)", common_store_list, key="mobile_common_item"
        )
        custom_item = st.text_input(
            "Item name (only if not in list above)", key="mobile_custom_item"
        )
        expense_amount = st.number_input(
            "Amount", min_value=0.0, format="%.2f", value=20.00, key="mobile_expense_amount"
        )
        expense_category = st.selectbox(
            "Category", EXPENSE_CATEGORY_OPTIONS_QUICK, key="mobile_expense_category"
        )
        how_paid = st.selectbox("Payment Method", payment_method, key="mobile_payment_method")
        notes_input = st.text_input("Notes (optional)", "", key="mobile_expense_notes")
        submitted = st.form_submit_button("Save Expense")

    if submitted:
        final_item = common_items_combined(common_item, custom_item)
        expense_data = {
            "date": expense_date,
            "amount": expense_amount,
            "category": expense_category,
            "items": final_item,
            "payment_method": how_paid,
            "source_notes": notes_input if notes_input else None,
            "traveling_category": None,
            "trip": None,
            "amount_for_number_of_travelers": None,
            "paid_for_number_of_travlerers": None,
            "exclude_from_monthly": False,
            "target_fund_category": None,
            "split_fund_category_1": None,
            "split_amount_1": 0.0,
        }
        if validate_expense_data(expense_data):
            insert_expense_data(expense_data)
            st.success(f"✅ Expense of ${expense_amount:.2f} saved.")

    st.caption(
        "Need to log a trip expense or a fund withdrawal? Use the full "
        "Manual Expense Input page on desktop."
    )