import streamlit as st  # type: ignore

from modules.mobile_quick_actions.css import inject_mobile_css
from modules.mobile_quick_actions.income_section import render_income_section
from modules.mobile_quick_actions.expense_section import render_expense_section
from modules.mobile_quick_actions.transaction_section import render_transaction_section
from modules.mobile_quick_actions.saving_status_section import render_saving_status_section
from modules.mobile_quick_actions.portfolio_section import render_portfolio_section

st.set_page_config(
    page_title="Quick Actions",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def mobile_quick_actions_page():
    inject_mobile_css()
    st.markdown(
        "<h2 style='text-align: center; color: #00ab41;'>📱 Quick Actions</h2>",
        unsafe_allow_html=True,
    )

    action = st.selectbox(
        "Choose an action",
        [
            "💰 Income",
            "🧾 Expense",
            "🔁 Transaction",
            "📊 Saving Status",
            "📈 Portfolio",
        ],
        key="mobile_action_choice",
    )

    st.divider()

    if action == "💰 Income":
        render_income_section()
    elif action == "🧾 Expense":
        render_expense_section()
    elif action == "🔁 Transaction":
        render_transaction_section()
    elif action == "📊 Saving Status":
        render_saving_status_section()
    elif action == "📈 Portfolio":
        render_portfolio_section()


if __name__ == "__main__":
    mobile_quick_actions_page()