import streamlit as st  # type: ignore


def inject_mobile_css():
    st.markdown(
        """
        <style>
        /* Keep inputs >= 16px so iOS/Android don't auto-zoom on focus */
        input, select, textarea, .stSelectbox div[data-baseweb="select"] {
            font-size: 16px !important;
        }
        /* Bigger touch targets for buttons */
        .stButton > button, .stFormSubmitButton > button {
            min-height: 3em;
            font-size: 18px;
            font-weight: 600;
        }
        .stRadio > div {
            gap: 0.5rem;
        }
        /* Less wasted vertical space on a small screen */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )