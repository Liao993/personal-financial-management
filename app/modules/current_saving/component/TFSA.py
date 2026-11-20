import streamlit as st  # type: ignore
import pandas as pd
import datetime

from utils.data import years


def TFSA(original_data, room):
    room = float(room)
    color = '#69B41E'
    current_year = datetime.date.today().year

    st.markdown(
        f"<h3 style='text-align: center; color:{color};'>"
        "TFSA Contribution Status</h3>",
        unsafe_allow_html=True
    )

    selected_year = st.selectbox(
    "Select Year for TFSA Contribution:",
    years,
    index=years.index(datetime.date.today().year)
)

    # --------------------------------------------------
    # 1. Filter TFSA accounts
    # --------------------------------------------------
    tfsa_data = original_data[
        original_data['account_name']
        .str.contains('TFSA', case=False, na=False)
    ].copy()

    # --------------------------------------------------
    # 2. Normalize data types
    # --------------------------------------------------
    tfsa_data['amount'] = pd.to_numeric(
        tfsa_data['amount'],
        errors='coerce'
    ).fillna(0.0)

    tfsa_data['date'] = pd.to_datetime(
        tfsa_data['date'],
        errors='coerce'
    )

    tfsa_data['transaction_type'] = (
        tfsa_data['transaction_type']
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------
    # 3. Filter cash flow transactions only
    # --------------------------------------------------
    transfer_in = tfsa_data[
        tfsa_data['transaction_type'] == 'transfer in'
    ].copy()

    transfer_out = tfsa_data[
        tfsa_data['transaction_type'] == 'transfer out'
    ].copy()

    # --------------------------------------------------
    # 4. Calculate contributions
    # --------------------------------------------------
    total_contribution = float(
        transfer_in['amount'].sum()
    )

    selected_year_contribution = float(
        transfer_in[
            transfer_in['date'].dt.year == selected_year
        ]['amount'].sum()
    )

    other_year_contribution = (
        total_contribution - selected_year_contribution
    )

    # --------------------------------------------------
    # 5. Calculate withdrawals
    # --------------------------------------------------
    total_withdrawal = float(
        transfer_out['amount'].abs().sum()
    )

    # Net cash flow from transfers only
    total_amount = total_contribution - total_withdrawal

    # --------------------------------------------------
    # 6. Calculate contribution room
    # --------------------------------------------------
    total_room = room
    total_left = total_room - total_contribution

    # --------------------------------------------------
    # 7. Create summary DataFrame
    # --------------------------------------------------
    tfsa_summary_data = {
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
            total_contribution,
            total_withdrawal,
            total_amount,
            total_room,
            total_left
        ]
    }

    tfsa_summary_df = (
        pd.DataFrame(tfsa_summary_data)
        .set_index('action')
    )

    # --------------------------------------------------
    # 8. Display dashboard
    # --------------------------------------------------
    st.dataframe(
        tfsa_summary_df,
        use_container_width=True
    )