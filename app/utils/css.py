import streamlit as st # type: ignore

def drop_down_list():
  st.markdown(
    """
    <style>
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: lightcyan !important;
        color: black !important; /* Optional: Change text color */
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li[role="option"] {
        background-color: white !important; /* Background for each option */
        color: black !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li[role="option"]:hover {
        background-color: #f0f8ff !important; /* Hover color for options */
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
  