from __future__ import annotations

import streamlit as st  # type: ignore
import pandas as pd
import numpy as np
from utils.data import (
    expense_category_options as category_list,
    traveling_category_options,
    fund_categories,
)
from modules.upload_pdf.pipeline.load import load_expense_data
from modules.upload_pdf.component.monthly_summary import monthly_summary
from backend.trip_backend import fetch_all_trips

edit_mode_form = "edit_mode_expense"
data_saved_key = "data_saved_expense"
review_data    = "review_expense_data"


def _is_blank(value) -> bool:
    return value is None or pd.isna(value) or str(value).strip() == ""


def _row_numbers(frame: pd.DataFrame, mask: pd.Series) -> str:
    return ", ".join(str(position + 1) for position, flagged in enumerate(mask) if flagged)


def validate_statement_review_data(
    edited_df: pd.DataFrame,
    single_trip: bool,
    trip_input: str | None,
) -> bool:
    travel_mask = (
        edited_df["category"].eq("Traveling")
        | edited_df["traveling_category"].notna()
    )
    if not travel_mask.any():
        return True

    travel_rows = edited_df.loc[travel_mask].copy()
    issues = []

    if single_trip and _is_blank(trip_input):
        issues.append("Select a trip or add a new trip before confirming traveling rows.")

    missing_category = travel_rows["traveling_category"].isna()
    if missing_category.any():
        issues.append(
            "Traveling rows must have a Traveling Category. Check row(s): "
            + _row_numbers(travel_rows, missing_category)
        )

    category_mismatch = travel_rows["category"].ne("Traveling")
    if category_mismatch.any():
        issues.append(
            "Rows with a Traveling Category must also use category Traveling. Check row(s): "
            + _row_numbers(travel_rows, category_mismatch)
        )

    missing_withdrawal = ~travel_rows["exclude_from_monthly"].fillna(False).astype(bool)
    if missing_withdrawal.any():
        issues.append(
            "Every traveling row must have Fund Withdrawal Required checked. Check row(s): "
            + _row_numbers(travel_rows, missing_withdrawal)
        )

    missing_primary = travel_rows["target_fund_category"].isna()
    if missing_primary.any():
        issues.append(
            "Every traveling row must have a Primary Target Fund selected. Check row(s): "
            + _row_numbers(travel_rows, missing_primary)
        )

    secondary_selected = travel_rows["split_fund_category_1"].notna()
    secondary_amount = pd.to_numeric(travel_rows["split_amount_1"], errors="coerce").fillna(0.0)

    missing_secondary_amount = secondary_selected & (secondary_amount <= 0)
    if missing_secondary_amount.any():
        issues.append(
            "Rows with a Secondary Target Fund must have a Secondary Amount greater than 0. "
            "Check row(s): " + _row_numbers(travel_rows, missing_secondary_amount)
        )

    amount = pd.to_numeric(travel_rows["amount"], errors="coerce").fillna(0.0)
    secondary_too_large = secondary_selected & (secondary_amount >= amount)
    if secondary_too_large.any():
        issues.append(
            "Secondary Amount must be smaller than the expense amount so the Primary Fund "
            "still has an amount. Check row(s): " + _row_numbers(travel_rows, secondary_too_large)
        )

    amount_without_secondary = (~secondary_selected) & (secondary_amount > 0)
    if amount_without_secondary.any():
        issues.append(
            "Rows with a Secondary Amount must also select a Secondary Target Fund. Check row(s): "
            + _row_numbers(travel_rows, amount_without_secondary)
        )

    for issue in issues:
        st.warning(issue)

    return not issues


def build_statement_review_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    review_df = dataframe.copy()
    amount = pd.to_numeric(review_df["amount"], errors="coerce").fillna(0.0)
    secondary_amount = pd.to_numeric(review_df["split_amount_1"], errors="coerce").fillna(0.0)
    has_secondary = review_df["split_fund_category_1"].notna()

    review_df["primary_fund_amount"] = np.where(
        review_df["exclude_from_monthly"].fillna(False).astype(bool),
        np.where(has_secondary, amount - secondary_amount, amount),
        0.0,
    )
    review_df["secondary_fund_amount"] = np.where(has_secondary, secondary_amount, 0.0)

    columns = [
        "date",
        "items",
        "amount",
        "category",
        "traveling_category",
        "trip",
        "exclude_from_monthly",
        "target_fund_category",
        "primary_fund_amount",
        "split_fund_category_1",
        "secondary_fund_amount",
        "payment_method",
        "source_notes",
    ]
    columns = [column for column in columns if column in review_df.columns]
    return review_df[columns]


def display_editable_dataframe(dataframe, bank):

    if edit_mode_form not in st.session_state:
        st.session_state[edit_mode_form] = True
    if data_saved_key not in st.session_state:
        st.session_state[data_saved_key] = False
    if review_data not in st.session_state:
        st.session_state[review_data] = dataframe

    if "Not Categorized" not in category_list:
        category_list.append("Not Categorized")

    if st.session_state[edit_mode_form]:
        st.success("Your data is being processed")
        st.markdown(
            """
            <style>
            .stAlert p { font-size: 20px !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="font-size:22px; color: #ff9900; padding: 6px; border-radius: 5px;">📍 Traveling Section</div>',
            unsafe_allow_html=True,
        )
        st.write("Please input your trip below!")
        single_trip = st.checkbox("Single Trip", value=True)

        existing_trips = fetch_all_trips()
        trip_options   = existing_trips + ["Add New Trip"]
        selected_trip  = st.selectbox("Select Trip", options=[None] + trip_options)

        if selected_trip == "Add New Trip":
            trip_input = st.text_input("Trip-MonthYear (e.g., Vancouver-012025)")
        else:
            trip_input = selected_trip

        st.markdown(
            '<div style="font-size:28px; color: #ff9900; padding: 10px; border-radius: 5px;">📊 PDF Data Editor</div>',
            unsafe_allow_html=True,
        )
        st.warning("⚠️ Please exclude House-related expenses!")

        # Initialise columns if missing
        df = st.session_state[review_data]
        df = df.drop(
            columns=["split_fund_category_2", "split_amount_2"],
            errors="ignore",
        )
        for col, default in [
            ("exclude_from_monthly",  False),
            ("target_fund_category",  None),
            ("split_fund_category_1", None),
            ("split_amount_1",        0.0),
        ]:
            if col not in df.columns:
                df[col] = default
        st.session_state[review_data] = df

        edited_df = st.data_editor(
            st.session_state[review_data],
            column_config={
                "date": st.column_config.DateColumn(
                    "Date", format="YYYY-MM-DD", required=True
                ),
                "category": st.column_config.SelectboxColumn(
                    "category",
                    options=category_list if category_list else dataframe["category"].unique(),
                    required=True,
                ),
                "traveling_category": st.column_config.SelectboxColumn(
                    "Traveling Category",
                    options=[None] + traveling_category_options,
                    required=False,
                ),
                "exclude_from_monthly": st.column_config.CheckboxColumn(
                    "Fund Withdrawal Required",
                    help="Check this to auto-create a withdrawal from the Target Fund. "
                         "This expense will be excluded from monthly spending totals.",
                    default=False,
                ),
                "target_fund_category": st.column_config.SelectboxColumn(
                    "Primary Target Fund",
                    help="Required when Fund Withdrawal is checked.",
                    options=[None] + fund_categories,
                    default=None,
                ),
                "split_fund_category_1": st.column_config.SelectboxColumn(
                    "Secondary Target Fund",
                    options=[None] + fund_categories,
                    default=None,
                ),
                "split_amount_1": st.column_config.NumberColumn(
                    "Amount (Secondary)",
                    default=0.0,
                    format="%.2f",
                ),
            },
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
        )

        if st.button("Confirm your changes"):
            if not validate_statement_review_data(edited_df, single_trip, trip_input):
                st.stop()
            if single_trip:
                edited_df.loc[edited_df["category"] == "Traveling", "trip"] = trip_input
                edited_df.loc[edited_df["category"] != "Traveling", "trip"] = None
            st.info("Loading your information...")
            st.session_state[review_data]    = edited_df
            st.session_state[edit_mode_form] = False
            st.session_state[data_saved_key] = False
            st.rerun()

    else:
        if not st.session_state.get(data_saved_key, False):
            st.info("View your information again before saving.")
            reviewed_data_dict = st.session_state[review_data]
            review_table = build_statement_review_table(reviewed_data_dict)
            st.dataframe(
                review_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "amount": st.column_config.NumberColumn("Expense Amount", format="$%.2f"),
                    "exclude_from_monthly": st.column_config.CheckboxColumn("Fund Withdrawal"),
                    "target_fund_category": st.column_config.TextColumn("Primary Fund"),
                    "primary_fund_amount": st.column_config.NumberColumn(
                        "Primary Fund Amount", format="$%.2f"
                    ),
                    "split_fund_category_1": st.column_config.TextColumn("Secondary Fund"),
                    "secondary_fund_amount": st.column_config.NumberColumn(
                        "Secondary Fund Amount", format="$%.2f"
                    ),
                },
            )
            monthly_summary(reviewed_data_dict)

            col1, col2 = st.columns(2)
            with col1:
                confirm_button = st.button("Save your information")
            with col2:
                edit_button = st.button("Edit your information")

            if confirm_button:
                data_to_saved = reviewed_data_dict
                st.info("Saving your information...")
                if load_expense_data(data_to_saved, bank):
                    st.session_state[data_saved_key] = True
                    st.rerun()

            if edit_button:
                st.session_state[edit_mode_form] = True
                st.session_state[data_saved_key] = False
                st.rerun()

        elif st.session_state.get(data_saved_key, True):
            st.success(
                "Expense data from your statement successfully saved! "
                "Moving back to upload page."
            )
            return True
