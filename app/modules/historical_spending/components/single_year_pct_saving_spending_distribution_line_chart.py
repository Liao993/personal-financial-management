import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore
import streamlit as st  # type: ignore

from modules.historical_spending.components.saving_spending_distribution import (
    SAVING_SPENDING_COLORS,
    build_saving_spending_distribution,
)
from modules.historical_spending.components.chart_style import apply_plotly_chart_style


def create_monthly_saving_spending_distribution_line_chart(expense, income, transaction):
    st.markdown(
        "<h3 style='text-align: center; color: #f1c40f;'>Percentage of Spending and Saving Balance by Month</h3>",
        unsafe_allow_html=True,
    )
    expense = expense.copy()
    transaction = transaction.copy()
    expense['date'] = pd.to_datetime(expense['date'])
    expense['month'] = expense['date'].dt.month

    merged_df = build_saving_spending_distribution(expense, transaction, 'month')
    all_categories = merged_df['category'].unique()
    palette = {cat: SAVING_SPENDING_COLORS.get(cat, 'gray') for cat in all_categories}

    fig = go.Figure()
    for category in all_categories:
        category_df = merged_df[merged_df['category'] == category].sort_values('month')
        fig.add_trace(go.Scatter(
            x=category_df['month'],
            y=category_df['percentage'],
            mode='lines+markers',
            name=category,
            line=dict(color=palette.get(category, 'gray'), width=3),
            marker=dict(size=8),
            hovertemplate=f"<b>{category}</b><br>Month: %{{x}}<br>Allocation: %{{y:.1f}}%<extra></extra>",
        ))

    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    max_pct = merged_df['percentage'].max()
    if pd.isna(max_pct) or max_pct <= 0:
        max_pct = 5
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Percentage of Total Allocation',
    )
    apply_plotly_chart_style(fig)
    fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), ticktext=month_labels)
    fig.update_yaxes(tickmode='array', tickvals=list(range(0, int(max_pct + 5), 5)))
    st.plotly_chart(fig, use_container_width=True)
