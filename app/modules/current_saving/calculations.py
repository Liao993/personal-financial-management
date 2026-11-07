from __future__ import annotations

import pandas as pd


SAVING_CATEGORIES = ("Retirement Saving", "Medium-term Saving", "Traveling Funds")
TRANSACTION_TYPES = ("Deposit", "Withdrawal", "Transfer In", "Transfer Out")


def calculate_yearly_fund_summary(transaction: pd.DataFrame) -> pd.DataFrame:
    """Return yearly net fund activity using the historical KPI definition.

    Transfer pairs are included because the historical KPI sums all transaction
    types. Expense-linked withdrawals are excluded so this matches the
    historical statistics query and does not double-count expense spending.
    """
    if transaction.empty:
        return pd.DataFrame()

    data = transaction.copy()
    if "expense_id" in data.columns:
        data = data[data["expense_id"].isna()].copy()

    data = data[
        data["fund_category"].isin(SAVING_CATEGORIES)
        & data["transaction_type"].isin(TRANSACTION_TYPES)
    ].copy()
    if data.empty:
        return pd.DataFrame()

    data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0.0)
    data["year"] = pd.to_datetime(data["date"], errors="coerce").dt.year
    data = data.dropna(subset=["year"])

    rows = []
    for year in sorted(data["year"].astype(int).unique()):
        year_df = data[data["year"].astype(int) == year]

        def sums(categories):
            category_df = year_df[year_df["fund_category"].isin(categories)]
            deposit = category_df.loc[category_df["transaction_type"] == "Deposit", "amount"].sum()
            withdrawal = category_df.loc[category_df["transaction_type"] == "Withdrawal", "amount"].sum()
            transfer_in = category_df.loc[category_df["transaction_type"] == "Transfer In", "amount"].sum()
            transfer_out = category_df.loc[category_df["transaction_type"] == "Transfer Out", "amount"].sum()
            return deposit, withdrawal, transfer_in, transfer_out

        values = {
            "R": sums(["Retirement Saving"]),
            "M": sums(["Medium-term Saving"]),
            "T": sums(["Traveling Funds"]),
            "(R+M)": sums(["Retirement Saving", "Medium-term Saving"]),
            "(R+M+T)": sums(SAVING_CATEGORIES),
        }
        row = {"Year": str(year)}
        for label, (deposit, withdrawal, transfer_in, transfer_out) in values.items():
            row[f"{label} - Yearly Deposit"] = float(deposit)
            row[f"{label} - Yearly Withdrawal"] = float(withdrawal)
            row[f"{label} - Transfer In"] = float(transfer_in)
            row[f"{label} - Transfer Out"] = float(transfer_out)
            row[f"{label} - Net Activity"] = float(
                deposit + withdrawal + transfer_in + transfer_out
            )
        rows.append(row)

    return pd.DataFrame(rows).set_index("Year").T.reset_index().rename(
        columns={"index": "Metrics"}
    )
