import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import streamlit as st # type: ignore

from modules.historical_spending.components.expense_grouping import (
    EXPENSE_GROUPS,
    EXPENSE_GROUP_COLORS,
    build_expense_group_pivot,
)
from modules.historical_spending.components.chart_style import apply_plotly_chart_style


def create_annual_expense_bar_chart(expense, transaction):
    st.markdown("<h3 style='text-align: center; color: orange;'>Annual Expense by Category</h3>", unsafe_allow_html=True)

    expense = expense.copy()
    transaction = transaction.copy()
    expense['year'] = pd.to_datetime(expense['date']).dt.year

    pivot_data = build_expense_group_pivot(expense, transaction, 'year')
    years = pivot_data.index.astype(int).astype(str)

    fig = go.Figure()
    for col in EXPENSE_GROUPS:
        fig.add_bar(
            y=years,
            x=pivot_data[col],
            name=col,
            orientation='h',
            marker_color=EXPENSE_GROUP_COLORS[col],
            hovertemplate=f"<b>{col}</b><br>Year: %{{y}}<br>Amount: $%{{x:,.2f}}<extra></extra>",
        )

    fig.update_layout(
        barmode='stack',
        xaxis_title='Amount',
        yaxis_title='Year',
    )
    apply_plotly_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)
