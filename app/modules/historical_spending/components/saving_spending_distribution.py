import pandas as pd # type: ignore


SAVING_SPENDING_CATEGORIES = [
    'Total Other Spending',
    'House Spending',
    'Retirement Saving',
    'Medium-term Saving',
    'Traveling Funds',
]

SAVING_SPENDING_COLORS = {
    'Total Other Spending': 'red',
    'Traveling Funds': "#6e3181",
    'Retirement Saving': '#1AA7EC',
    'Medium-term Saving': '#f39c12',
    "House Spending": "#16a085",
}


def build_saving_spending_distribution(expense, transaction, period_col):
    total_spending = (
        expense.groupby(period_col, as_index=False)['amount']
        .sum()
        .rename(columns={'amount': 'total_amount'})
    )
    total_spending['category'] = "Total Other Spending"

    transaction = transaction.rename(columns={'fund_category': "category"}).copy()
    transaction_filtered = transaction.copy()
    transaction_filtered.loc[transaction_filtered['category'] == 'House', 'category'] = 'House Spending'
    transaction_filtered = transaction_filtered[transaction_filtered['category'] != 'Emergency Funds']
    transaction_filtered = (
        transaction_filtered.groupby([period_col, 'category'], as_index=False)['total_amount']
        .sum()
    )

    data = pd.concat([total_spending, transaction_filtered], ignore_index=True)
    data['total_amount'] = pd.to_numeric(data['total_amount'], errors='coerce').fillna(0)
    period_total = (
        data.groupby(period_col, as_index=False)['total_amount']
        .sum()
        .rename(columns={'total_amount': 'period_total'})
    )
    data = pd.merge(data, period_total, on=period_col, how='left')
    data['percentage'] = data.apply(
        lambda row: (row['total_amount'] / row['period_total']) * 100 if row['period_total'] != 0 else 0,
        axis=1
    )
    return data
