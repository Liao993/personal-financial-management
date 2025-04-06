import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def create_expense_pie_chart(total_expense, total_saving):
    st.markdown("<h3 style='text-align: center;'>Expense vs. Saving Distribution</h3>", unsafe_allow_html=True)
    labels = ['Total Expense', 'Total Saving']
    values = [total_expense, total_saving]
    colors = ['#f44336', '#4caf50']

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker_colors=colors,
                                 textinfo='percent+label',
                                 textfont=dict(size=18))]) # Larger annotation text

    fig.update_layout(
        legend=dict(
            font=dict(size=20) # Larger legend font size
        ),
        margin=dict(t=10, l=20) # Reduce top margin of the chart (adjust as needed)
    )
    st.plotly_chart(fig, use_container_width=True)