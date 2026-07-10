import pandas as pd # type: ignore


EXPENSE_GROUPS = ['House', 'Grocery', 'Other', 'Car & Gas', 'Donation', 'Gifts']
EXPENSE_GROUP_COLORS = {
    'House': 'green',
    'Grocery': '#ff8fab',
    'Other': 'orange',
    'Car & Gas': 'lightblue',
    'Donation': 'red',
    'Gifts': 'purple',
}


def categorize_expense(category):
    if category == 'Donation':
        return 'Donation'
    elif category == 'Grocery':
        return 'Grocery'
    elif category == 'Gifts':
        return 'Gifts'
    elif category in ['Car', 'Gas']:
        return 'Car & Gas'
    else:
        return 'Other'


def build_expense_group_pivot(expense, transaction, period_col):
    expense = expense.copy()
    transaction = transaction.copy()
    expense['expense_group'] = expense['category'].apply(categorize_expense)

    summary_data = (
        expense.groupby([period_col, 'expense_group'])['amount']
        .sum()
        .reset_index()
    )

    house = transaction[transaction['fund_category'] == 'House'].copy()
    if not house.empty:
        house = (
            house.groupby(period_col, as_index=False)['total_amount']
            .sum()
            .rename(columns={'total_amount': 'amount'})
        )
        house['expense_group'] = 'House'
        summary_data = pd.concat(
            [summary_data, house[[period_col, 'expense_group', 'amount']]],
            ignore_index=True,
        )

    summary_data['amount'] = pd.to_numeric(summary_data['amount'], errors='coerce').fillna(0)
    pivot_data = summary_data.pivot_table(
        index=period_col,
        columns='expense_group',
        values='amount',
        aggfunc='sum',
        fill_value=0,
    ).sort_index()

    for col in EXPENSE_GROUPS:
        if col not in pivot_data.columns:
            pivot_data[col] = 0
    return pivot_data[EXPENSE_GROUPS]
