
import streamlit as st
import pandas as pd

from datetime import date, datetime

from backend.transaction_backend import fetch_all_transaction_data

from backend.retirement_limits_backend import (
    fetch_retirement_limits,
    fetch_retirement_limit_entries,
    update_retirement_limits_by_year,
)
from utils.data import years

from modules.current_saving.component.TFSA import TFSA
from modules.current_saving.component.RRSP import RRSP


st.set_page_config(
    page_title="Current_Status",
    page_icon="💰",
    layout="wide",
)


def format_updated_date(updated_at):
    """Format the database timestamp for display."""

    if updated_at is None:
        return "Not recorded"

    if isinstance(updated_at, datetime):
        return updated_at.strftime("%Y-%m-%d")

    if isinstance(updated_at, date):
        return updated_at.strftime("%Y-%m-%d")

    return str(updated_at)


def TFSA_and_RRSP():

    st.markdown(
        "<h1 style='text-align: center;'>TFSA and RRSP</h1>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------
    # Fetch persisted contribution limits
    # --------------------------------------------------

    limits = fetch_retirement_limits()

    # --------------------------------------------------
    # Calculation notes
    # --------------------------------------------------

    with st.expander("How are contributions and withdrawals calculated?", expanded=False):

        st.markdown(
            """
            **Contribution calculation**
            - Only `Transfer In` transactions count as contributions.
            - `Deposit` transactions are excluded because they may represent
              interest, capital gains, or other internal account activity.
            - Other transaction types are excluded.

            **Withdrawal calculation**
            - Only `Transfer Out` transactions count as withdrawals.
            - `Withdrawal` transactions and other transaction types are excluded.

            **Net cash flow**

            Net Cash Flow = Total Contributions - Total Withdrawals

            **Remaining contribution room**

            Remaining Room = Manually Maintained Limit - Total Contributions

            Note: Withdrawals are displayed separately and are not automatically
            added back to the remaining contribution room in this tracker.
            """
        )

    # --------------------------------------------------
    # Display current limits and last-updated dates
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="TFSA Total Limit",
            value=f"${float(limits['TFSA']):,.2f}",
        )

        st.caption(
            f"Last updated: "
            f"{format_updated_date(limits['TFSA_updated_at'])}"
        )

    with col2:
        st.metric(
            label="RRSP Total Limit",
            value=f"${float(limits['RRSP']):,.2f}",
        )

        st.caption(
            f"Last updated: "
            f"{format_updated_date(limits['RRSP_updated_at'])}"
        )

    # --------------------------------------------------
    # Edit contribution limits
    # --------------------------------------------------

    with st.expander("Edit contribution limits by year", expanded=False):

        with st.form("retirement_account_limits_form"):
            saved_entries = fetch_retirement_limit_entries()
            saved = {
                (int(entry["year"]), entry["account_type"]): float(entry["amount"])
                for entry in saved_entries
            }
            # Include the full contribution-history window beginning in 2019,
            # plus the configured future years and any years already saved.
            entry_years = sorted(
                set(range(2019, max(years) + 1))
                | {year for year, _ in saved}
            )
            limits_df = pd.DataFrame({
                "Year": entry_years,
                "TFSA": [saved.get((year, "TFSA"), 0.0) for year in entry_years],
                "RRSP": [saved.get((year, "RRSP"), 0.0) for year in entry_years],
            })
            edited_limits = st.data_editor(
                limits_df,
                hide_index=True,
                use_container_width=True,
                disabled=["Year"],
                column_config={
                    "Year": st.column_config.NumberColumn("Year", format="%d"),
                    "TFSA": st.column_config.NumberColumn("TFSA", min_value=0.0, step=100.0, format="$%.2f"),
                    "RRSP": st.column_config.NumberColumn("RRSP", min_value=0.0, step=100.0, format="$%.2f"),
                },
            )

            submitted = st.form_submit_button("Save limits")

            if submitted:

                entries = []
                for row in edited_limits.to_dict("records"):
                    entries.extend([
                        {"year": int(row["Year"]), "account_type": "TFSA", "amount": row["TFSA"]},
                        {"year": int(row["Year"]), "account_type": "RRSP", "amount": row["RRSP"]},
                    ])
                update_retirement_limits_by_year(entries)

                st.success("TFSA and RRSP limits updated.")

                st.rerun()

    # --------------------------------------------------
    # Fetch transaction data
    # --------------------------------------------------

    columns_names, all_data = fetch_all_transaction_data()

    original_data = pd.DataFrame(
        all_data,
        columns=columns_names,
    )

    # --------------------------------------------------
    # Display TFSA and RRSP components
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        TFSA(original_data, limits["TFSA"])

    with col2:
        RRSP(original_data, limits["RRSP"])


if __name__ == "__main__":
    TFSA_and_RRSP()
