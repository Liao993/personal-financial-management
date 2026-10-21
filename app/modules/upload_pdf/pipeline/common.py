from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st  # type: ignore


SOURCE_OPTIONS = ["RBC", "PC", "Scotia_Red"]


def infer_statement_year(lines, filename: str | None = None) -> str | None:
    """Prefer statement text for year detection; filename is only a fallback."""
    for line in lines or []:
        match = re.search(r"\b(20\d{2})\b", str(line))
        if match:
            return match.group(1)

    if filename:
        match = re.search(r"\b(20\d{2})\b", Path(filename).name)
        if match:
            st.warning(
                f"Using filename year for {filename}. Please confirm dates in the review table."
            )
            return match.group(1)

    return None


def exclude_payment_credits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Credit-card payment rows are money paid toward the card, not expenses.
    Drop rows where the description contains payment and the parsed amount is negative.
    """
    if df.empty or not {"items", "amount"}.issubset(df.columns):
        return df

    amounts = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    has_payment_word = df["items"].astype(str).str.contains(
        r"\bpayment\b", case=False, regex=True, na=False
    )
    filtered_df = df.loc[~(has_payment_word & (amounts < 0))].copy()
    removed_count = len(df) - len(filtered_df)
    if removed_count:
        st.info(f"Excluded {removed_count} payment row(s) from the expense review.")
    return filtered_df
