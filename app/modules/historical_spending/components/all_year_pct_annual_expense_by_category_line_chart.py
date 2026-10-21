import streamlit as st  # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
from plotly.subplots import make_subplots # type: ignore

from modules.historical_spending.components.chart_style import (
    apply_plotly_chart_style,
    house_percentage_table,
    nice_percentage_ticks,
)


def create_annual_expense_percentage_chart(expense, income, transaction):
    expense = expense.copy()
    income = income.copy()
    transaction = transaction.copy()

    expense['date'] = pd.to_datetime(expense['date'])
    expense['year'] = expense['date'].dt.year
    expense = expense[expense['category'] != 'Traveling'].copy()

    categories_of_interest = ['Grocery', 'Food Outside', 'Donation', 'Gas', 'Gifts', 'Education', 'Exercise', 'Car']
    expense['major_category'] = expense['category'].apply(lambda x: x if x in categories_of_interest else 'Others')

    grouped = (
        expense.groupby(['year', 'major_category'], as_index=False)['amount']
        .sum()
        .rename(columns={'amount': 'total_amount'})
    )

    house = transaction[transaction['fund_category'] == 'House'].copy()
    if not house.empty:
        house = house.groupby('year', as_index=False)['total_amount'].sum()
        house['major_category'] = 'House'
        grouped = pd.concat([grouped, house[['year', 'major_category', 'total_amount']]], ignore_index=True)

    annual_income = income.groupby('year', as_index=False)['total_income'].sum()
    years = sorted(set(grouped['year'].dropna().astype(int)) | set(annual_income['year'].dropna().astype(int)))
    categories = sorted(grouped['major_category'].dropna().unique())
    full_grid = pd.MultiIndex.from_product([years, categories], names=['year', 'major_category']).to_frame(index=False)
    merged_df = pd.merge(full_grid, grouped, on=['year', 'major_category'], how='left')
    merged_df['total_amount'] = pd.to_numeric(merged_df['total_amount'], errors='coerce').fillna(0)
    merged_df = pd.merge(merged_df, annual_income, on='year', how='left')
    merged_df['total_income'] = pd.to_numeric(merged_df['total_income'], errors='coerce').fillna(0)
    merged_df['percentage'] = np.divide(
        merged_df['total_amount'],
        merged_df['total_income'],
        out=np.zeros(len(merged_df), dtype=float),
        where=merged_df['total_income'].to_numpy(dtype=float) != 0,
    ) * 100

    category_colors = {
        'Grocery': '#ff8fab',
        'Food Outside': "#e0a539",
        'Gas': "rgba(25, 133, 83, 0.63)",
        'Donation': "#e62922",
        'Others': "#716E74",
        'Gifts': "#BD1CC5",
        'Education': "#130fe4",
        'Exercise': "#07294b",
        'Car': "#5dade2",
        'House': "rgba(30, 178, 50, 0.59)",
    }
    palette = {cat: category_colors.get(cat, 'gray') for cat in categories}

    df_plot = merged_df[merged_df['major_category'] != 'House'].copy()
    df_house = merged_df[merged_df['major_category'] == 'House'].copy()
    house_pivot = df_house.set_index('year')['percentage'].reindex(years, fill_value=0)

    avg_annual_income = annual_income[annual_income['total_income'] != 0]['total_income'].mean()
    avg_income_text = f"${avg_annual_income:,.2f}" if pd.notna(avg_annual_income) else "$0.00"
    st.markdown(
        (
            "<h3 style='text-align: center; color: #bce784;'>"
            f"Percentage of Expense by Category by Year (Avg. Annual Income: {avg_income_text})"
            "</h3>"
        ),
        unsafe_allow_html=True,
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.76, 0.18],
        vertical_spacing=0.12,
        specs=[[{"type": "xy"}], [{"type": "table"}]],
    )
    dashed_categories = {'Exercise'}
    for category in df_plot['major_category'].dropna().unique():
        category_df = df_plot[df_plot['major_category'] == category]
        fig.add_scatter(
            x=category_df['year'],
            y=category_df['percentage'],
            mode='lines+markers',
            name=category,
            line=dict(
                color=palette.get(category, 'gray'),
                width=3,
                dash='dash' if category in dashed_categories else 'solid',
            ),
            marker=dict(size=8),
            customdata=np.stack([category_df['total_amount'], category_df['total_income']], axis=-1),
            hovertemplate=(
                f"<b>{category}</b><br>"
                "Year: %{x}<br>"
                "Amount: $%{customdata[0]:,.2f}<br>"
                "Income: $%{customdata[1]:,.2f}<br>"
                "% of Income: %{y:.1f}%<extra></extra>"
            ),
            row=1,
            col=1,
        )

    max_pct = df_plot['percentage'].replace([np.inf, -np.inf], np.nan).dropna().max()
    fig.add_trace(house_percentage_table(house_pivot.tolist(), [str(y) for y in years]), row=2, col=1)
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Percentage of Earning (Income)',
    )
    apply_plotly_chart_style(fig)
    fig.update_xaxes(tickmode='array', tickvals=years, ticktext=[str(y) for y in years])
    fig.update_xaxes(title_standoff=18, row=1, col=1)
    fig.update_yaxes(tickmode='array', tickvals=nice_percentage_ticks(max_pct))
    st.plotly_chart(fig, use_container_width=True)
