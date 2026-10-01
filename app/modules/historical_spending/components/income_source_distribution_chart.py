import pandas as pd # type: ignore
import plotly.graph_objects as go # type: ignore
import streamlit as st # type: ignore

from modules.historical_spending.components.chart_style import apply_plotly_chart_style


def create_income_source_distribution_chart(income_source_data: pd.DataFrame):
    st.markdown("<h3 style='text-align: center; color: orange;'>Earning Source Distribution</h3>", unsafe_allow_html=True)

    if income_source_data.empty:
        st.info("No income source data available.")
        return

    summary_data = income_source_data.copy()
    summary_data['amount'] = pd.to_numeric(summary_data['amount'], errors='coerce').fillna(0)
    summary_data = summary_data.sort_values(by='amount', ascending=False)
    
    total_amount = summary_data['amount'].sum()
    summary_data['percentage'] = (summary_data['amount'] / total_amount * 100) if total_amount else 0

    fig = go.Figure()

    for _, row in summary_data.iterrows():
        fig.add_bar(
            y=["Total Earnings"],
            x=[row['amount']],
            name=row['source'],
            orientation='h',
            hovertemplate="<b>%{data.name}</b><br>Amount: $%{x:,.2f}<br>Share: %{customdata:.1f}%<extra></extra>",
            customdata=[row['percentage']],
        )

    fig.update_layout(
        barmode='stack',
        xaxis_title='Amount',
        yaxis_title='',
    )
    apply_plotly_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)
