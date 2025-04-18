import streamlit as st # type: ignore
import pandas as pd
import plotly.graph_objects as go # type: ignore

def create_expense_pie_chart(total_expense, total_saving, travel_saving):
    st.markdown("<h3 style='text-align: center;'>Expense vs. Saving Distribution</h3>", unsafe_allow_html=True)
    labels = ['Total Expense', 'Total Saving', "Total Travel Saving"]
    actual_saving = total_saving - travel_saving
    values = [total_expense, actual_saving, travel_saving]
    colors = ['#f44336', '#4caf50', "#a879e0"]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker_colors=colors,
                                 textinfo='percent+label',
                                 textfont=dict(size=18))]) # Larger annotation text

    fig.update_layout(
       legend=dict(
        orientation="v",  # Vertical orientation
        yanchor="top",
        y=1,
        xanchor="left",
        x=0,
        font=dict(size=16) # Larger legend font size
    ),
        margin=dict(t=10) # Reduce top margin of the chart (adjust as needed)
    )
    st.plotly_chart(fig, use_container_width=True)