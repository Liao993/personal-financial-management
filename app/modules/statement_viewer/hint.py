import streamlit as st # type: ignore
from utils.data import expense_category_options, transaction_type_database, fund_categories,traveling_category_options,account_name_list 


def hint_page():
    cols = st.columns(3)
    with cols[0]:
        st.markdown("<h5 style='color: lightcoral;'>expense tables or dbt_budget.intermediate_expenses_with_summary</h5>", unsafe_allow_html=True)
        st.info("date, amount, items, catgory, traveling_category, trip")
    with cols[1]:
        st.markdown("<h5 style='color: lightcoral;'>income tables</h5>", unsafe_allow_html=True)
        st.info("date, amount, source, regular, notes")  
    with cols[2]:
        st.markdown("<h5 style='color: lightcoral;'>transactions tables</h5>", unsafe_allow_html=True)
        st.info("date, account_name, transaction_type, amount, fund_category, source_notes, transfer_to_account")

    st.write("___")
    cols = st.columns(2)
    with cols[0]:

        st.markdown("<h5 style='color: lightcoral;'>Expense Categories:</h5>", unsafe_allow_html=True)
        st.info(f"{', '.join(expense_category_options)}")
    with cols[1]:
        st.markdown("<h5 style='color: lightcoral;'>Usable Fund Categories:</h5>", unsafe_allow_html=True)
        st.info(f"{', '.join(fund_categories)}")
      
    cols = st.columns(3)
    with cols[0]:
        st.markdown("<h5 style='color: lightcoral;'>Transaction Types:</h5>", unsafe_allow_html=True)
        st.info(f"{', '.join(transaction_type_database)}")
      
    with cols[1]:
        st.markdown("<h5 style='color: lightcoral;'>Traveling Categories:</h5>", unsafe_allow_html=True)
        st.info(f"{', '.join(traveling_category_options)}")
    with cols[2]:
        st.markdown("<h5 style='color: lightcoral;'>Account Names:</h5>", unsafe_allow_html=True)
        st.info(f"{', '.join(account_name_list)}")

if __name__ == "__main__":
    hint_page()