from __future__ import annotations

import pandas as pd


SAVING_CATEGORIES = ("Retirement Saving", "Medium-term Saving", "Traveling Funds")
TRANSACTION_TYPES = ("Deposit", "Withdrawal", "Transfer In", "Transfer Out")
FUND_CATEGORY_GROUPS = {
    "R": ("Retirement Saving",),
    "M": ("Medium-term Saving",),
    "T": ("Traveling Funds",),
    "R+M": ("Retirement Saving", "Medium-term Saving"),
    "R+M+T": SAVING_CATEGORIES,
}


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


def _fund_category_period_rows(transaction: pd.DataFrame) -> pd.DataFrame:
    data = transaction.copy()
    data = data[
        data["fund_category"].isin(SAVING_CATEGORIES)
        & data["transaction_type"].isin(("Deposit", "Withdrawal"))
    ].copy()
    if data.empty:
        return pd.DataFrame(
            columns=["Year", "Month", "Fund Category", "Deposit", "Withdrawal", "Net Saving"]
        )

    data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0.0)
    dates = pd.to_datetime(data["date"], errors="coerce")
    data["Year"] = dates.dt.year.astype("Int64")
    data["Month"] = dates.dt.month.astype("Int64")
    data["Deposit"] = data["amount"].where(data["transaction_type"] == "Deposit", 0.0)
    data["Withdrawal"] = (-data["amount"]).where(data["transaction_type"] == "Withdrawal", 0.0)
    data = data.dropna(subset=["Year", "Month"])

    rows = []
    for group_name, categories in FUND_CATEGORY_GROUPS.items():
        group = (
            data[data["fund_category"].isin(categories)]
            .groupby(["Year", "Month"], as_index=False)[["Deposit", "Withdrawal"]]
            .sum()
        )
        group["Fund Category"] = group_name
        group["Net Saving"] = group["Deposit"] - group["Withdrawal"]
        rows.append(group)

    return pd.concat(rows, ignore_index=True)


def calculate_fund_category_summary(transaction: pd.DataFrame) -> pd.DataFrame:
    """Combine monthly and annual deposit/withdrawal summaries by fund category."""
    monthly = _fund_category_period_rows(transaction)
    if monthly.empty:
        return pd.DataFrame(
            columns=["Period", "Year", "Month", "Fund Category", "Deposit", "Withdrawal", "Net Saving"]
        )

    monthly = monthly.assign(
        Period="Monthly",
        Month=monthly["Month"].map(lambda month: pd.Timestamp(2000, int(month), 1).strftime("%B")),
        _sort_month=monthly["Month"].astype(int),
    )
    annual = (
        monthly.groupby(["Year", "Fund Category"], as_index=False)[["Deposit", "Withdrawal"]]
        .sum()
        .assign(Period="Yearly", Month="Year Total")
    )
    annual["Net Saving"] = annual["Deposit"] - annual["Withdrawal"]
    monthly["Net Saving"] = monthly["Deposit"] - monthly["Withdrawal"]
    summary = pd.concat([annual, monthly], ignore_index=True, sort=False)
    summary["_sort_period"] = summary["Period"].map({"Yearly": 0, "Monthly": 1})
    summary["_sort_category"] = summary["Fund Category"].map(
        {name: index for index, name in enumerate(("R", "M", "T", "R+M", "R+M+T", *SAVING_CATEGORIES))}
    ).fillna(99)
    return (
        summary.sort_values(["Year", "_sort_period", "_sort_month", "_sort_category"], na_position="last")
        [["Period", "Year", "Month", "Fund Category", "Deposit", "Withdrawal", "Net Saving"]]
        .reset_index(drop=True)
    )


def calculate_account_flow_summary(transaction: pd.DataFrame) -> pd.DataFrame:
    """Summarize physical-account cash flow, including account transfers."""
    if transaction.empty:
        return pd.DataFrame()

    data = transaction.copy()
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0.0)
    dates = pd.to_datetime(data["date"], errors="coerce")
    data["Year"] = dates.dt.year.astype("Int64")
    data["Month"] = dates.dt.month.astype("Int64")
    data = data.dropna(subset=["Year", "Month", "account_name"])
    data["Deposit"] = data["amount"].where(data["transaction_type"] == "Deposit", 0.0)
    data["Withdrawal"] = (-data["amount"]).where(data["transaction_type"] == "Withdrawal", 0.0)
    data["Transfer In"] = data["amount"].where(data["transaction_type"] == "Transfer In", 0.0)
    data["Transfer Out"] = (-data["amount"]).where(data["transaction_type"] == "Transfer Out", 0.0)

    account_rows = data.groupby(["Year", "Month", "account_name"], as_index=False)[
        ["Deposit", "Withdrawal", "Transfer In", "Transfer Out"]
    ].sum().rename(columns={"account_name": "Account"})
    total_rows = data.groupby(["Year", "Month"], as_index=False)[
        ["Deposit", "Withdrawal", "Transfer In", "Transfer Out"]
    ].sum()
    total_rows["Account"] = "All Accounts"
    summary = pd.concat([account_rows, total_rows], ignore_index=True)
    summary["Net Account Flow"] = (
        summary["Deposit"]
        - summary["Withdrawal"]
        + summary["Transfer In"]
        - summary["Transfer Out"]
    )
    summary = summary.sort_values(["Year", "Month", "Account"]).reset_index(drop=True)
    summary["Month"] = summary["Month"].map(lambda month: pd.Timestamp(2000, int(month), 1).strftime("%B"))
    return summary[
        ["Year", "Month", "Account", "Deposit", "Withdrawal", "Transfer In", "Transfer Out", "Net Account Flow"]
    ]
