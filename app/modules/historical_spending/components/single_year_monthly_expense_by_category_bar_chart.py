import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore

from modules.historical_spending.components.expense_grouping import (
    EXPENSE_GROUPS,
    EXPENSE_GROUP_COLORS,
    build_expense_group_pivot,
)
from modules.historical_spending.components.chart_style import apply_plotly_chart_style

def create_monthly_expense_bar_chart(expense, transaction):
    st.markdown("<h3 style='text-align: center; color: orange;'>Monthly Expense by Category</h3>", unsafe_allow_html=True)

    expense = expense.copy()
    transaction = transaction.copy()
    expense['month'] = pd.to_datetime(expense['date']).dt.month
    pivot_data = build_expense_group_pivot(expense, transaction, 'month').reindex(range(1, 13), fill_value=0)
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    fig = go.Figure()
    for col in EXPENSE_GROUPS:
        fig.add_bar(
            x=month_labels,
            y=pivot_data[col],
            name=col,
            marker_color=EXPENSE_GROUP_COLORS[col],
            hovertemplate=f"<b>{col}</b><br>Month: %{{x}}<br>Amount: $%{{y:,.2f}}<extra></extra>",
        )

    fig.update_layout(
        barmode='stack',
        xaxis_title='Month',
        yaxis_title='Amount',
    )
    apply_plotly_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)
