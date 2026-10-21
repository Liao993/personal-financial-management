import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore

from modules.historical_spending.components.chart_style import apply_plotly_chart_style

def create_income_source_pie_chart(income_data, title="Total Earning by Source"):
    st.markdown(f"<h3 style='text-align: center; color: orange;'>{title}</h3>", unsafe_allow_html=True)

    if income_data.empty:
        st.info("No income data available.")
        return

    income_data = income_data.copy()
    income_data['amount'] = pd.to_numeric(income_data['amount'], errors='coerce').fillna(0)

    # Aggregate by source
    summary_data = income_data.groupby('source')['amount'].sum().reset_index()
    summary_data = summary_data[summary_data['amount'] > 0]
    
    colors = px.colors.qualitative.Pastel

    fig = go.Figure(data=[go.Pie(
        labels=summary_data['source'],
        values=summary_data['amount'],
        hole=.4,
        marker=dict(colors=colors),
        hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )])

    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
    )
    apply_plotly_chart_style(fig, show_legend=True)
    st.plotly_chart(fig, use_container_width=True)
