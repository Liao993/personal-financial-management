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
    """Return one monthly-detail table with annual total rows by fund category."""
    monthly = _fund_category_period_rows(transaction)
    if monthly.empty:
        return pd.DataFrame(
            columns=["Year", "Month", "Deposit", "Withdrawal", "Net Monthly Saving", "R", "M", "T", "R+M", "R+M+T"]
        )

    category_order = ("R", "M", "T", "R+M", "R+M+T")
    monthly_values = monthly.pivot_table(
        index=["Year", "Month"], columns="Fund Category", values="Net Saving", aggfunc="sum", fill_value=0.0
    ).reset_index()
    for category in category_order:
        if category not in monthly_values.columns:
            monthly_values[category] = 0.0

    totals = (
        monthly[monthly["Fund Category"].isin(("R", "M", "T"))]
        .groupby(["Year", "Month"], as_index=False)[["Deposit", "Withdrawal"]]
        .sum()
    )
    monthly_values = monthly_values.drop(columns=["Deposit", "Withdrawal"], errors="ignore").merge(
        totals, on=["Year", "Month"], how="left"
    )
    monthly_values["Net Monthly Saving"] = monthly_values["Deposit"] - monthly_values["Withdrawal"]
    monthly_values["_sort_month"] = monthly_values["Month"]
    monthly_values["Month"] = monthly_values["Month"].map(
        lambda month: pd.Timestamp(2000, int(month), 1).strftime("%B")
    )

    annual_values = monthly_values.groupby("Year", as_index=False)[
        ["Deposit", "Withdrawal", *category_order]
    ].sum()
    annual_values["Net Monthly Saving"] = annual_values["Deposit"] - annual_values["Withdrawal"]
    annual_values["Month"] = "Annual Total"
    annual_values["_sort_month"] = 13

    summary = pd.concat([annual_values, monthly_values], ignore_index=True, sort=False)
    return (
        summary.sort_values(["Year", "_sort_month"], ascending=[False, False])
        [["Year", "Month", "Deposit", "Withdrawal", "Net Monthly Saving", *category_order]]
        .reset_index(drop=True)
    )


def calculate_account_flow_summary(
    transaction: pd.DataFrame,
    hidden_accounts: set[str] | None = None,
) -> pd.DataFrame:
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
    yearly_net = summary.groupby(["Year", "Account"], as_index=False)["Net Account Flow"].sum()
    yearly_net = yearly_net.rename(columns={"Net Account Flow": "Yearly Net Account Flow"})
    summary = summary.merge(yearly_net, on=["Year", "Account"], how="left")
    if hidden_accounts:
        summary = summary[~summary["Account"].isin(hidden_accounts)].copy()
    summary = summary.sort_values(["Year", "Month", "Account"], ascending=[False, False, True]).reset_index(drop=True)
    summary["Month"] = summary["Month"].map(lambda month: pd.Timestamp(2000, int(month), 1).strftime("%B"))
    return summary[
        ["Year", "Month", "Account", "Deposit", "Withdrawal", "Transfer In", "Transfer Out", "Net Account Flow", "Yearly Net Account Flow"]
    ]
