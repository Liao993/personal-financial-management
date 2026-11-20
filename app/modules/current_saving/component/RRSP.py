import streamlit as st  # type: ignore
import pandas as pd
import datetime

from utils.data import years


def RRSP(original_data, room):
    room = float(room)
    color = '#F38701'
    current_year = datetime.date.today().year

    st.markdown(
        f"<h3 style='text-align: center; color:{color};'>"
        "RRSP Contribution Status</h3>",
        unsafe_allow_html=True
    )

    selected_year = st.selectbox(
    "Select Year for RRSP Contribution:",
    years,
    index=years.index(datetime.date.today().year)
)
    # --------------------------------------------------
    # 1. Filter RRSP accounts
    # --------------------------------------------------
    rrsp_data = original_data[
        original_data['account_name']
        .str.contains('RRSP', case=False, na=False)
    ].copy()

    # --------------------------------------------------
    # 2. Normalize data types
    # --------------------------------------------------
    rrsp_data['amount'] = pd.to_numeric(
        rrsp_data['amount'],
        errors='coerce'
    ).fillna(0.0)

    rrsp_data['date'] = pd.to_datetime(
        rrsp_data['date'],
        errors='coerce'
    )

    rrsp_data['transaction_type'] = (
        rrsp_data['transaction_type']
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------
    # 3. Filter cash flow transactions only
    # --------------------------------------------------
    transfer_in = rrsp_data[
        rrsp_data['transaction_type'] == 'transfer in'
    ].copy()

    transfer_out = rrsp_data[
        rrsp_data['transaction_type'] == 'transfer out'
    ].copy()

    # --------------------------------------------------
    # 4. Calculate contributions
    # --------------------------------------------------
    rrsp_contribution = float(
        transfer_in['amount'].sum()
    )

    selected_year_contribution = float(
        transfer_in[
            transfer_in['date'].dt.year == selected_year
        ]['amount'].sum()
    )

    other_year_contribution = (
        rrsp_contribution - selected_year_contribution
    )

    # --------------------------------------------------
    # 5. Calculate withdrawals
    # --------------------------------------------------
    rrsp_withdrawal = float(
        transfer_out['amount'].abs().sum()
    )

    # Net cash flow from transfers only
    rrsp_amount = rrsp_contribution - rrsp_withdrawal

    # --------------------------------------------------
    # 6. Calculate contribution room
    # --------------------------------------------------
    total_room = room
    total_left = total_room - rrsp_contribution

    # --------------------------------------------------
    # 7. Create summary DataFrame
    # --------------------------------------------------
    rrsp_summary_data = {
        'action': [
            f"{selected_year} Contribution",
            "Other Year Contribution",
            "Total Contribution",
            "Total Withdrawal",
            "Net Cash Flow",
            f'Total Room in {current_year}',
            f'Room Left in {current_year}'
        ],
        'amount': [
            selected_year_contribution,
            other_year_contribution,
            rrsp_contribution,
            rrsp_withdrawal,
            rrsp_amount,
            total_room,
            total_left
        ]
    }

    rrsp_summary_df = (
        pd.DataFrame(rrsp_summary_data)
        .set_index('action')
    )

    # --------------------------------------------------
    # 8. Display dashboard
    # --------------------------------------------------
    st.dataframe(
        rrsp_summary_df,
        use_container_width=True
    )