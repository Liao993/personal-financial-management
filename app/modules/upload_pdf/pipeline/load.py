import streamlit as st # type: ignore
import pandas as pd
from utils.validation import validate_expense_data
from backend.expense_backend import find_matching_expense, insert_expense_data


def _normalize_duplicate_value(value):
    if value is None or pd.isna(value):
        return ""
    return str(value).strip().lower()


def _duplicate_key(expense_data: dict):
    amount = pd.to_numeric(expense_data.get("amount"), errors="coerce")
    amount_key = f"{float(amount):.2f}" if pd.notna(amount) else ""
    return (
        str(expense_data.get("date")),
        _normalize_duplicate_value(expense_data.get("payment_method")),
        amount_key,
        _normalize_duplicate_value(expense_data.get("items")),
        _normalize_duplicate_value(expense_data.get("source_notes")),
    )


def _describe_duplicate(expense_data: dict) -> str:
    note = expense_data.get("source_notes")
    note_text = f" | note: {note}" if note else ""
    return (
        f"{expense_data.get('date')} | {expense_data.get('payment_method')} | "
        f"{expense_data.get('amount')} | {expense_data.get('items')}{note_text}"
    )

# after verifying the data, load data into the database
def load_expense_data(updated_dataframe):
    if updated_dataframe is not None:
       # 3. Validate each row and collect valid data
        valid_expenses = []
        duplicate_messages = []
        seen_keys = set()
        for index, row in updated_dataframe.iterrows():
            # Convert row to dict and replace NaN with None
            expense_data = row.where(pd.notna(row), None).to_dict()
            expense_data.pop("statement_file", None)
            validated = validate_expense_data(expense_data)

            if validated:
                duplicate_key = _duplicate_key(expense_data)
                if duplicate_key in seen_keys:
                    duplicate_messages.append(
                        f"Row {index + 1} duplicates another row in this upload: "
                        + _describe_duplicate(expense_data)
                    )
                    continue
                seen_keys.add(duplicate_key)

                existing_matches = find_matching_expense(expense_data)
                if not existing_matches.empty:
                    duplicate_messages.append(
                        f"Row {index + 1} already exists in the expense database: "
                        + _describe_duplicate(expense_data)
                    )
                    continue

                valid_expenses.append(expense_data)
            else:
                st.error("No valid expenses found in the DataFrame.")
                return False

        if duplicate_messages:
            st.error(
                "Duplicate expense rows were found. Nothing was saved. "
                "If one is a separate real purchase, edit the item name or add a source note "
                "and save again."
            )
            for message in duplicate_messages:
                st.warning(message)
            return False

        for expense in valid_expenses:
            if not insert_expense_data(expense): #check if the insertion was successful
                st.error("Saving stopped because one expense could not be inserted.")
                return False
        st.success(f"Successfully validated and inserted {len(valid_expenses)} expenses.")
        return True
    else:
        st.error("Input DataFrame is None.")
        return False
