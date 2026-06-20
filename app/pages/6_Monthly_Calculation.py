import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime  # type: ignore

from modules.monthly_stats.components.savingKpi import display_saving_kpis  # type: ignore
from modules.monthly_stats.components.goal_form import financial_goals_form
from modules.monthly_stats.components.monthly_pie import create_expense_pie_chart  # type: ignore
from modules.monthly_stats.components.spending_table import display_spending_table  # type: ignore
from modules.monthly_stats.middle_layer.monthly_saving import monthly_savings_action
from modules.monthly_stats.calculation.saving_calculation import expense_and_saving_calculation  # type: ignore
from backend.transaction_backend import fetch_transaction_deposit_check, insert_transaction_data
from models.transaction_models import Transaction
import os
st.set_page_config(page_title="Monthly Stats", page_icon="💰", layout="wide")


# ─────────────────────────────────────────────
# Rerun Calculation helpers
# ─────────────────────────────────────────────

def delete_month_saving_deposits(year: int, month: int) -> bool:
    """
    Delete existing 'saved from' deposit transactions for the given month
    so they can be recreated with updated amounts.
    Only touches rows with source_notes LIKE 'saved from%'.
    Manually added deposits for the same month are untouched.
    """
    from utils.connection import get_db_connection
    import psycopg2

    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM transactions
            WHERE EXTRACT(YEAR FROM date)  = %s
              AND EXTRACT(MONTH FROM date) = %s
              AND transaction_type = 'Deposit'
              AND source_notes LIKE 'saved from%%'
              AND expense_id IS NULL
            """,
            (year, month),
        )
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Error deleting saving deposits: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def rerun_monthly_saving(
    goal_datetime,
    source_notes,
    travel_saving,
    retirement_saving,
    medium_term_saving,
    emergency_funds,
    home_deposit,
) -> bool:
    """
    Delete existing saving deposits for the month and recreate with new amounts.
    Same logic as monthly_savings_data_handling but skips the duplicate check
    and deletes first.
    """
    year  = goal_datetime.year
    month = goal_datetime.month

    deleted = delete_month_saving_deposits(year, month)
    if not deleted:
        return False
    raw_accounts = os.environ.get("ACCOUNT_NAMES", "")
    Chequing_Account = raw_accounts.split(",")[0].strip() if raw_accounts else "Default Chequing"
    House_Account = raw_accounts.split(",")[1].strip() if len(raw_accounts.split(",")) > 1 else "Default House Account"
    transactions_to_insert = [
        Transaction(
            date=goal_datetime,
            account_name=Chequing_Account,
            transaction_type="Deposit",
            amount=travel_saving,
            fund_category="Traveling Funds",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name=Chequing_Account,
            transaction_type="Deposit",
            amount=retirement_saving,
            fund_category="Retirement Saving",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name=Chequing_Account,
            transaction_type="Deposit",
            amount=medium_term_saving,
            fund_category="Medium-term Saving",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name=Chequing_Account,
            transaction_type="Deposit",
            amount=emergency_funds,
            fund_category="Emergency Funds",
            source_notes=source_notes,
        ),
        Transaction(
            date=goal_datetime,
            account_name=House_Account,
            transaction_type="Deposit",
            amount=home_deposit,
            fund_category="House",
            source_notes=source_notes,
        ),
    ]

    insertion_errors = []
    for transaction in transactions_to_insert:
        try:
            validated = Transaction(**transaction.dict())
            success = insert_transaction_data(validated.dict())
            if not success:
                insertion_errors.append(validated.dict())
        except Exception as e:
            st.error(f"Validation error: {e}")
            return False

    return len(insertion_errors) == 0


# ─────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────

def monthly_stats_page():
    st.markdown(
        "<h1 style='color: #5e548e; text-align: center;'>Monthly Stats</h1>",
        unsafe_allow_html=True,
    )

    if st.session_state.get("monthly_rerun_success_message"):
        st.success(st.session_state.pop("monthly_rerun_success_message"))

    financial_goals = financial_goals_form()

    if financial_goals:
        (
            goal_date,
            total_saving,
            travel_saving,
            retirement_saving,
            medium_term_saving,
            emergency_funds,
            monthly_expense_daily_data,
            monthly_income,
            monthly_expense,
            home_deposit_amount,
        ) = expense_and_saving_calculation(financial_goals)

        # Store in session state
        st.session_state["goal_datetime"]    = goal_date
        st.session_state["source_notes"]     = f"saved from {goal_date.year} {goal_date.month:02d}"
        st.session_state["travel_saving"]    = travel_saving
        st.session_state["retirement_saving"]= retirement_saving
        st.session_state["medium_term_saving"]= medium_term_saving
        st.session_state["emergency_funds"]  = emergency_funds
        st.session_state["home_deposit"]     = home_deposit_amount

        st.write("---")
        display_saving_kpis(
            total_saving, travel_saving, retirement_saving,
            medium_term_saving, emergency_funds
        )
        st.write(" ")
        st.write(" ")

        left_col, right_col = st.columns(2)

        with left_col:
            display_spending_table(
                monthly_expense_daily_data, monthly_income, home_deposit_amount
            )
            st.write(" ")
            st.write(" ")

            # ── Check if saving already recorded for this month ──────────
            existing = fetch_transaction_deposit_check(
                goal_date.year, goal_date.month
            )
            already_saved = not existing.empty

            if not already_saved:
                # First time save
                if st.button("💾 Save Your Results", on_click=monthly_savings_action):
                    pass
            else:
                # Month already has saving records — show Rerun option
                st.info(
                    f"Saving records already exist for "
                    f"{goal_date.year}-{goal_date.month:02d}. "
                    "Use **Rerun Calculation** if your expenses changed "
                    "(e.g. refund received, entry deleted)."
                )

                if st.button(
                    "🔄 Rerun Calculation",
                    type="primary",
                    key="rerun_btn",
                ):
                    success = rerun_monthly_saving(
                        goal_date,
                        f"saved from {goal_date.year} {goal_date.month:02d}",
                        travel_saving,
                        retirement_saving,
                        medium_term_saving,
                        emergency_funds,
                        home_deposit_amount,
                    )
                    if success:
                        st.session_state["monthly_rerun_success_message"] = (
                            f"✅ Saving records for "
                            f"{goal_date.year}-{goal_date.month:02d} "
                            "updated successfully in the transaction database."
                        )
                        st.session_state.pop("financial_goals_data", None)
                        st.rerun()
                    else:
                        st.error("Rerun failed. Please check the errors above.")

        with right_col:
            create_expense_pie_chart(
                monthly_expense, total_saving, travel_saving, home_deposit_amount
            )


if __name__ == "__main__":
    monthly_stats_page()
