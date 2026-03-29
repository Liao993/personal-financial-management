import streamlit as st # type: ignore
import pandas as pd # type: ignore

def display_saving_kpis(total_saving, travel_saving, retirement_saving, medium_term_saving, emergency_funds):
    """Displays the saving KPIs with custom styling."""
   
    st.markdown("<h1 style='text-align: center;'>Saving Overview</h1>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5= st.columns(5)
    with col1:
        st.markdown(
            f"<p style='font-size: 22px; color: green;'><b>Total</b></p>"
            f"<p style='font-size: 26px; color: green;'><b>${total_saving:.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<p style='font-size: 20px; color: #a879e0;'>Traveling Funds</p>"
            f"<p style='font-size: 24px; color: #a879e0;'>${travel_saving:.2f}</p>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"<p style='font-size: 20px; color: orange;'>Retirement</p>"
            f"<p style='font-size: 24px; color: orange;'>${retirement_saving:.2f}</p>",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"<p style='font-size: 20px; color: lightgreen;'>Medium-Term</p>"
            f"<p style='font-size: 24px; color: lightgreen;'>${medium_term_saving:.2f}</p>",
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"<p style='font-size: 20px; color: lightblue;'>RBC Saving</p>"
            f"<p style='font-size: 24px; color: lightblue;'>${emergency_funds:.2f}</p>",
            unsafe_allow_html=True,
        )
   
   