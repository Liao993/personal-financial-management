import streamlit as st # type: ignore

def review_income_input(review_data_key):

    st.subheader("Your Input Information:")
    reviewed_data = st.session_state.get(review_data_key, {})
    st.write(f"**Date:** {reviewed_data.get('date', '')}")
    st.write(f"**Amount:** {reviewed_data.get('amount', '')}")
    st.write(f"**Source:** {reviewed_data.get('source', '')}")
    st.write(f"**Regular Income:** {'Yes' if reviewed_data.get('regular', False) else 'No'}")

    return reviewed_data