import streamlit as st  # type: ignore
from datetime import date

from utils.data import (
    expense_category_options,
    common_store_list,
    payment_method,
    traveling_category_options,
    fund_categories,
)
from utils.validation import validate_expense_data
from backend.expense_backend import insert_expense_data
from backend.trip_backend import fetch_all_trips
from modules.expense_input.middle_layer.common_items_combined import common_items_combined


def render_expense_section():
    st.subheader("🧾 Quick Expense")
    if st.session_state.pop("mobile_expense_success_message", None):
        st.success("Expense saved.")

    form_version = st.session_state.get("mobile_expense_form_version", 0)
    key_prefix = f"mobile_expense_{form_version}"

    with st.form(f"mobile_expense_form_{form_version}"):
        expense_date = st.date_input("Date", value=date.today(), key=f"{key_prefix}_date")
        common_item = st.selectbox(
            "Store (if common)", common_store_list, key=f"{key_prefix}_common_item"
        )
        custom_item = st.text_input(
            "Item name (only if not in list above)", key=f"{key_prefix}_custom_item"
        )
        expense_amount = st.number_input(
            "Amount", min_value=0.0, format="%.2f", value=20.00, key=f"{key_prefix}_amount"
        )
        expense_category = st.selectbox(
            "Category", expense_category_options, key=f"{key_prefix}_category"
        )
        how_paid = st.selectbox("Payment Method", payment_method, key=f"{key_prefix}_payment_method")
        notes_input = st.text_input("Notes (optional)", "", key=f"{key_prefix}_notes")

        with st.expander("Traveling Section", expanded=expense_category == "Traveling"):
            traveling_category = st.selectbox(
                "Traveling Category",
                [None] + traveling_category_options,
                key=f"{key_prefix}_traveling_category",
            )
            existing_trips = fetch_all_trips()
            trip_options = existing_trips + ["Add New Trip"]
            selected_trip = st.selectbox(
                "Select Trip",
                options=[None] + trip_options,
                key=f"{key_prefix}_selected_trip",
            )
            new_trip = st.text_input(
                "If 'Add New Trip' is selected, enter here (e.g., Vancouver-Jan25)",
                key=f"{key_prefix}_new_trip",
            )

            if selected_trip == "Add New Trip":
                trip_input = new_trip
            else:
                trip_input = selected_trip

            amount_for_number_of_travelers = st.number_input(
                "Amount of Travelers",
                min_value=1,
                value=None,
                placeholder="Type a number...",
                step=1,
                key=f"{key_prefix}_amount_for_travelers",
            )
            paid_for_number_of_travlerers = st.number_input(
                "Amount of Travelers I Paid",
                min_value=0,
                value=None,
                placeholder="Type a number...",
                step=1,
                key=f"{key_prefix}_paid_for_travelers",
            )
            trip = trip_input if trip_input else None

        with st.expander("Fund Withdrawal", expanded=False):
            exclude_from_monthly = st.checkbox(
                "Deduct this expense from a saved fund",
                key=f"{key_prefix}_exclude_from_monthly",
            )
            target_fund_category = st.selectbox(
                "Primary Fund",
                [None] + fund_categories,
                key=f"{key_prefix}_target_fund_category",
            )
            split_fund_category_1 = st.selectbox(
                "Secondary Fund (optional)",
                [None] + fund_categories,
                key=f"{key_prefix}_split_fund_category_1",
            )
            split_amount_1 = st.number_input(
                "Secondary Amount",
                min_value=0.0,
                format="%.2f",
                value=0.0,
                key=f"{key_prefix}_split_amount_1",
            )

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
            "traveling_category": traveling_category,
            "trip": trip,
            "amount_for_number_of_travelers": amount_for_number_of_travelers,
            "paid_for_number_of_travlerers": paid_for_number_of_travlerers,
            "exclude_from_monthly": exclude_from_monthly,
            "target_fund_category": target_fund_category,
            "split_fund_category_1": split_fund_category_1,
            "split_amount_1": split_amount_1,
        }
        if validate_expense_data(expense_data):
            insert_expense_data(expense_data)
            st.session_state["mobile_expense_success_message"] = True
            st.session_state["mobile_expense_form_version"] = form_version + 1
            st.rerun()
