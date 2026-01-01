import pandas as pd
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
import streamlit as st # type: ignore
import plotly.graph_objects as go # type: ignore
import numpy as np

def create_annotation_pie_chart(df):
    """
    Creates a pie chart from a Pandas DataFrame with columns:
    'traveling_category', 'category_spending', 'total_spending', and 'percentage'.
    The chart is annotated with 'category_spending' and 'percentage' values.

    Args:
        df (pd.DataFrame): DataFrame containing the data for the pie chart.
    """
    # Check if the DataFrame is empty
    if df.empty:
        st.warning("The input DataFrame is empty. Cannot create pie chart.")
        return

    # Check for required columns
    required_columns = ['traveling_category', 'category_spending', 'total_spending', 'percentage_total']
    if not all(col in df.columns for col in required_columns):
        missing_columns = [col for col in required_columns if col not in df.columns]
        st.error(f"DataFrame is missing the following columns: {', '.join(missing_columns)}")
        return
    # Define the color mapping to match the pie chart
    category_colors = {
        'Food': '#e74c3c',
        'Gas/Parking': '#3498db',
        'Gift': '#f7dc6f',
        'Hotel': '#00ab41',
        "Public Transportation": '#f39c12',
        "Flight": '#1a5276',
        "Tickets": '#a569bd',
        "Others": '#aab7b8'
    }
 

    # 1. Basic Pie Chart
    fig = go.Figure(data=[go.Pie(
        labels=df['traveling_category'],
        values=df['category_spending'],
        # Use the 'percentage' column directly
        textinfo='percent+label',  # Display label and text (which we'll define)
        textfont=dict(size=18),  # Position labels outside the pie slices
        marker=dict(colors=[category_colors.get(category, '#aab7b8') for category in df['traveling_category']])
    )])

    fig.update_layout(
        showlegend=True,
         legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=20)
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    # 3. Display the Chart
    st.plotly_chart(fig, use_container_width=True, key='total_pie_chart')


 
