import streamlit as st # type: ignore
from backend.expense_backend import fetch_last_expense_data
from modules.expense_input.components.expense_form import expense_form
from modules.expense_input.components.review_data import review_data_print_out
from modules.expense_input.middle_layer.confirmed_data_handling import confirmed_data_handling

st.set_page_config(page_title="Expense Input", page_icon="💸", layout='wide')

edit_mode_form = 'edit_mode_expense'
data_saved_key = 'data_saved_expense'
expense_data_key = 'expense_data'


def reset_manual_expense_state():
    for key in [
        expense_data_key,
        "common_item_select",
        "custom_item_input",
        "target_fund_category",
        "split_fund_category_1",
        "split_amount_1",
    ]:
        st.session_state.pop(key, None)
    st.session_state["expense_form_version"] = (
        st.session_state.get("expense_form_version", 0) + 1
    )
    st.session_state[edit_mode_form] = True
    st.session_state[data_saved_key] = False


def expense_input_page():
    st.markdown(
        "<h1 style='color: #2e86c1; text-align: center;'>Please Input Your Daily Expense</h1>",
        unsafe_allow_html=True,
    )

    # ── Prepaid & Refund rules info box ──────────────────────────────────
    st.info(
        "**📌 Before you record — Prepaid vs Refund rules:**\n\n"
        "**Prepaid (e.g. covering a friend's meal, expect full repayment soon):** "
        "Do NOT record it here. Simply skip it. "
        "Once your friend pays back, no action needed — it never touched your bookkeeping.\n\n"
        "**Paid and waiting for a refund (e.g. hotel deposit, returned item, cancelled booking):** "
        "Record it here as normal. "
        "When the refund arrives, go to **Page 16 Expense Editor** to update the amount or delete the record. "
        "If it was a regular expense affecting that month's saving total, go to **Page 6** and click **Rerun Calculation**. "
        "If it had a Fund Withdrawal, the linked transaction updates automatically."
    )

    # ── Session state init ────────────────────────────────────────────────
    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False
    if expense_data_key not in st.session_state:
        st.session_state[expense_data_key] = {}

    if st.session_state.pop("manual_expense_success_message", None):
        st.success("Expense data successfully saved.")

    # ── Show the form ─────────────────────────────────────────────────────
    if st.session_state[edit_mode_form]:
        expense_form(edit_mode_form, data_saved_key, expense_data_key)

        st.write("---")
        last_expense_data = fetch_last_expense_data()
        if not last_expense_data.empty:
            st.write("Last Expense Data:")
            st.table(last_expense_data)

    # ── Review mode ───────────────────────────────────────────────────────
    else:
        if not st.session_state.get(data_saved_key, False):
            reviewed_data = review_data_print_out(expense_data_key, edit_mode_form, data_saved_key)
            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Confirm")
            with col2:
                edit_button = st.button("Edit")

            if confirm_button:
                confirmed_data_handling(reviewed_data, data_saved_key)

            if edit_button:
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        elif st.session_state.get(data_saved_key, True):
            st.session_state["manual_expense_success_message"] = True
            reset_manual_expense_state()
            st.rerun()


if __name__ == "__main__":
    expense_input_page()
