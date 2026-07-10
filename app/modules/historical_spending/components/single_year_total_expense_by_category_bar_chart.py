import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore

from modules.historical_spending.components.chart_style import apply_plotly_chart_style


def create_summary_bar_chart(expense, title="Annual Expense Distribution by Category"):
    st.markdown(f"<h3 style='text-align: center; color: #5dade2;'>{title}</h3>", unsafe_allow_html=True)

    # Group data by 'category' and calculate the sum of 'amount'
    summary_data = expense.groupby('category')['amount'].sum().reset_index()

    selected_categories = [
        'Car', 'Cell Phone', 'Donation', 'Education', 'Food Outside', 'Gas',
        'Gifts', 'Grocery', 'Household Goods', 'Saved For Love', 'Transportation',
    ]
    # not in selected category -> Others
    summary_data.loc[~summary_data['category'].isin(selected_categories), 'category'] = 'Others'
    summary_data = summary_data.groupby('category')['amount'].sum().reset_index()
    # order from least to most so the largest bar lands at the top
    summary_data = summary_data.sort_values(by='amount', ascending=True)

    total_amount = summary_data['amount'].sum()
    summary_data['percentage'] = (summary_data['amount'] / total_amount * 100) if total_amount else 0

    # --- Fix for "annotated number is cut" -------------------------------
    # The old version drew the $ amount with plt.text() right at the end of
    # each bar (ha='left'). For the largest bar(s) that text landed at or
    # past the right edge of the figure and got clipped off. Instead of a
    # floating annotation, the amount + percentage is now folded straight
    # into the y-axis tick label itself (left side of the plot), so it
    # never depends on how long the bar is and can never be cut off.
    summary_data['category_label'] = summary_data.apply(
        lambda row: f"{row['category']}  \u2014  ${row['amount']:,.2f} ({row['percentage']:.1f}%)",
        axis=1,
    )

    fig = go.Figure(go.Bar(
        x=summary_data['amount'],
        y=summary_data['category_label'],
        orientation='h',
        marker_color="#5dade2",
        hovertemplate="<b>%{y}</b><br>Amount: $%{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        xaxis_title='Amount',
        yaxis_title=None,
    )
    apply_plotly_chart_style(fig, show_legend=False)
    st.plotly_chart(fig, use_container_width=True)
