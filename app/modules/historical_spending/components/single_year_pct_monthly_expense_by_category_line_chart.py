import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from plotly.subplots import make_subplots  # type: ignore

from modules.historical_spending.components.chart_style import (
    apply_plotly_chart_style,
    house_percentage_table,
    nice_percentage_ticks,
)


def create_expense_line_chart(expense, income, transaction):
    expense = expense.copy()
    expense['date'] = pd.to_datetime(expense['date'])
    expense['month'] = expense['date'].dt.month
    expense = expense[expense['category'] != 'Traveling'].copy()

    categories_of_interest = [
        'Grocery', 'Food Outside', 'Donation', 'Gas', 'Gifts',
        'Education', 'Exercise', 'Car',
    ]

    expense['major_category'] = expense['category'].apply(
        lambda x: x if x in categories_of_interest else 'Others'
    )

    grouped = (
        expense.groupby(['month', 'major_category'], as_index=False)['amount']
        .sum()
        .rename(columns={'amount': 'total_amount'})
    )

    # add house amount
    house = transaction[transaction['fund_category'] == 'House'].copy()
    house = house.rename(columns={'fund_category': 'major_category'})
    grouped = pd.concat([grouped, house[['month', 'major_category', 'total_amount']]], ignore_index=True)

    # Create full month-category grid
    all_months = pd.Series(range(1, 13), name='month')
    all_categories = pd.Series(grouped['major_category'].unique(), name='major_category')
    full_grid = pd.merge(all_months.to_frame(), all_categories.to_frame(), how='cross')

    monthly_expenses = pd.merge(full_grid, grouped, on=['month', 'major_category'], how='left')
    monthly_expenses['total_amount'] = pd.to_numeric(monthly_expenses['total_amount'], errors='coerce').fillna(0)

    # Merge Income Data
    merged_df = pd.merge(monthly_expenses, income, on='month', how='left')
    merged_df['total_income'] = pd.to_numeric(merged_df['total_income'], errors='coerce').fillna(0)

    # Compute percentage with null income treatment
    merged_df['percentage'] = np.divide(
        merged_df['total_amount'],
        merged_df['total_income'],
        out=np.zeros(len(merged_df), dtype=float),
        where=merged_df['total_income'].to_numpy(dtype=float) != 0,
    ) * 100
    merged_df['percentage'] = pd.Series(merged_df['percentage']).replace([np.inf, -np.inf], 0).fillna(0)

    monthly_income = merged_df[merged_df['total_income'] != 0]['total_income'].mean()
    avg_income_text = f"${monthly_income:,.2f}" if pd.notna(monthly_income) else "$0.00"
    st.markdown(
        (
            "<h3 style='text-align: center; color: #bce784;'>"
            f"Percentage of Expense by Category by Month (Avg. Monthly Income: {avg_income_text})"
            "</h3>"
        ),
        unsafe_allow_html=True,
    )

    # --- Colors -------------------------------------------------------
    # Car was moved off blue — it previously clashed with Education and
    # Exercise, which are both blue/navy. Exercise is also now drawn
    # dashed below as an extra visual cue on top of the color change,
    # since dark navy vs. royal blue is still easy to mix up at a glance.
    category_colors = {
        'Grocery': '#ff8fab',
        'Food Outside': '#e0a539',
        'Gas': '#198553',
        'Donation': '#e62922',
        'Others': '#716E74',
        'Gifts': '#BD1CC5',
        'Education': '#130fe4',
        'Exercise': '#07294b',
        'Car': '#16a085',
    }
    dashed_categories = {'Exercise'}

    # a. Filter data for the main line plot (excluding 'House')
    df_plot = merged_df[merged_df['major_category'] != 'House'].copy()

    # b. Extract data for the House percentage table
    df_house = merged_df[merged_df['major_category'] == 'House'].copy()

    # c. Pivot and re-index House data to ensure all 12 months (1-12) are present
    house_pivot = (
        df_house.set_index('month')['percentage']
        .reindex(range(1, 13), fill_value=0)
    )

    # --- Plot -----------------------------------------------------------
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.76, 0.18],
        vertical_spacing=0.12,
        specs=[[{"type": "xy"}], [{"type": "table"}]],
    )
    month_labels = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ]

    for category in df_plot['major_category'].dropna().unique():
        cat_df = df_plot[df_plot['major_category'] == category].sort_values('month')
        fig.add_scatter(
            x=cat_df['month'],
            y=cat_df['percentage'],
            mode='lines+markers',
            name=category,
            line=dict(
                color=category_colors.get(category, 'gray'),
                width=3,
                dash='dash' if category in dashed_categories else 'solid',
            ),
            marker=dict(size=8),
            customdata=np.stack([cat_df['total_amount'], cat_df['total_income']], axis=-1),
            hovertemplate=(
                f"<b>{category}</b><br>"
                "Month: %{x}<br>"
                "Amount: $%{customdata[0]:,.2f}<br>"
                "Income: $%{customdata[1]:,.2f}<br>"
                "% of Income: %{y:.1f}%<extra></extra>"
            ),
            row=1,
            col=1,
        )

    max_pct = df_plot['percentage'].replace([np.inf, -np.inf], np.nan).dropna().max()
    fig.add_trace(house_percentage_table(house_pivot.tolist(), month_labels), row=2, col=1)
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Percentage of Earning (Income)',
    )
    apply_plotly_chart_style(fig)
    fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)), ticktext=month_labels)
    fig.update_xaxes(title_standoff=18, row=1, col=1)
    fig.update_yaxes(tickmode='array', tickvals=nice_percentage_ticks(max_pct))

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<h5 style='text-align: center;'>The sum of each category above should match the total spending in the below chart.</h5>",
        unsafe_allow_html=True,
    )
