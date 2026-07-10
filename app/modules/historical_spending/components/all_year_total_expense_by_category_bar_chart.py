import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import streamlit as st # type: ignore

from modules.historical_spending.components.chart_style import apply_plotly_chart_style


def create_total_expense_distribution_chart(expense):
    st.markdown("<h3 style='text-align: center; color: #5dade2;'>Total Expense Distribution by Category</h3>", unsafe_allow_html=True)

    summary_data = expense.groupby('category')['amount'].sum().reset_index()
    selected_categories = [
        'Car',
        'Cell Phone',
        'Donation',
        'Education',
        'Food Outside',
        'Gas',
        'Gifts',
        'Grocery',
        'Household Goods',
        'Saved For Love',
        'Transportation',
    ]
    summary_data.loc[~summary_data['category'].isin(selected_categories), 'category'] = 'Others'
    summary_data = summary_data.groupby('category', as_index=False)['amount'].sum()
    summary_data['amount'] = pd.to_numeric(summary_data['amount'], errors='coerce').fillna(0)
    summary_data = summary_data.sort_values(by='amount', ascending=True)
    total_amount = summary_data['amount'].sum()
    summary_data['percentage'] = (summary_data['amount'] / total_amount * 100) if total_amount else 0

    fig = go.Figure(go.Bar(
        x=summary_data['amount'],
        y=summary_data['category'],
        orientation='h',
        hovertemplate="<b>%{y}</b><br>Amount: $%{x:,.2f}<br>Share: %{customdata:.1f}%<extra></extra>",
        customdata=summary_data['percentage'],
    ))
    fig.update_layout(
        xaxis_title='Amount',
        yaxis_title='Category',
    )
    apply_plotly_chart_style(fig, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)
