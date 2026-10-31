import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore

from modules.historical_spending.components.chart_style import apply_plotly_chart_style

def create_monthly_income_source_bar_chart(income_data):
    st.markdown("<h3 style='text-align: center; color: orange;'>Monthly Earning by Source</h3>", unsafe_allow_html=True)

    if income_data.empty:
        st.info("No income data available.")
        return

    income_data = income_data.copy()
    income_data['month'] = pd.to_datetime(income_data['date']).dt.month
    income_data['amount'] = pd.to_numeric(income_data['amount'], errors='coerce').fillna(0)

    pivot_data = income_data.pivot_table(index='month', columns='source', values='amount', aggfunc='sum', fill_value=0)
    pivot_data = pivot_data.reindex(range(1, 13), fill_value=0)
    
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    sources = pivot_data.columns.tolist()

    fig = go.Figure()
    
    colors = px.colors.qualitative.Pastel

    for i, col in enumerate(sources):
        fig.add_bar(
            x=month_labels,
            y=pivot_data[col],
            name=col,
            marker_color=colors[i % len(colors)],
            hovertemplate=f"<b>{col}</b><br>Month: %{{x}}<br>Amount: $%{{y:,.2f}}<extra></extra>",
        )

    fig.update_layout(
        barmode='stack',
        xaxis_title='Month',
        yaxis_title='Amount',
    )
    apply_plotly_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)
