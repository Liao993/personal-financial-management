import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore

from modules.historical_spending.components.chart_style import apply_plotly_chart_style

def create_annual_income_source_bar_chart(income_data):
    st.markdown("<h3 style='text-align: center; color: orange;'>Annual Earning by Source</h3>", unsafe_allow_html=True)

    if income_data.empty:
        st.info("No income data available.")
        return

    income_data = income_data.copy()
    income_data['year'] = pd.to_datetime(income_data['date']).dt.year
    income_data['amount'] = pd.to_numeric(income_data['amount'], errors='coerce').fillna(0)

    pivot_data = income_data.pivot_table(index='year', columns='source', values='amount', aggfunc='sum', fill_value=0)
    years = pivot_data.index.astype(int).astype(str)
    sources = pivot_data.columns.tolist()

    fig = go.Figure()
    colors = px.colors.qualitative.Pastel

    for i, col in enumerate(sources):
        fig.add_bar(
            y=years,
            x=pivot_data[col],
            name=col,
            orientation='h',
            marker_color=colors[i % len(colors)],
            hovertemplate=f"<b>{col}</b><br>Year: %{{y}}<br>Amount: $%{{x:,.2f}}<extra></extra>",
        )

    fig.update_layout(
        barmode='stack',
        xaxis_title='Amount',
        yaxis_title='Year',
    )
    apply_plotly_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)
