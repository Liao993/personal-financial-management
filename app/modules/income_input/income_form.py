import streamlit as st # type: ignore
from datetime import date
from utils.data import fixed_income_data, account_name_list


def income_input_form(edit_mode_form_key, review_data_key):

    review_button = False

    form_version = st.session_state.get("income_form_version", 0)
    with st.form(f"income_form_{form_version}"):
        income_date = st.date_input("Date", value=date.today())
        income_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=fixed_income_data)

        source_options = ["Gov", "Tax Return", "Other"]
        selected_source = st.selectbox("Source", source_options)
        income_source = selected_source

        notes_input = st.text_input("Notes", "")
        notes = notes_input if notes_input else None  # Set notes to None if empty string

        income_regular = st.checkbox("Regular Income", value=True)

        # Deposit account selector
        # Default to the first account (the main chequing account)
        default_account = account_name_list[0] if account_name_list else "Main Chequing"
        default_index = 0
        deposit_account = st.selectbox(
            "Deposit Into Account",
            options=account_name_list if account_name_list else [default_account],
            index=default_index,
            help=(
                "Choose which account this income is deposited into. "
                "Chequing deposits are tracked in your monthly savings calculation. "
                "Non-chequing deposits automatically create a linked transaction."
            ),
        )

        review_button = st.form_submit_button("Review")

    if review_button:
        st.session_state[review_data_key] = {
            "date": income_date,
            "amount": income_amount,
            "source": income_source,
            "regular": income_regular,
            "notes": notes,
            "deposit_account": deposit_account,
        }
        st.session_state[edit_mode_form_key] = False
        st.session_state['data_saved_income'] = False
        st.rerun()

    return review_button
