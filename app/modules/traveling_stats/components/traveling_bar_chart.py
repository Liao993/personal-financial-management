import seaborn as sns # type: ignore
import streamlit as st # type: ignore
import pandas as pd
import plotly.graph_objects as go # type: ignore

def create_category_spending_bar_chart(df):
    """
    Creates a bar chart showing spending amount for each category,
    with colors matching the pie chart, and a title indicating total spending.

    Args:
        df (pd.DataFrame): DataFrame with columns
            'traveling_category', 'category_spending', 'total_spending'.
    """
    # Check if the DataFrame is empty
    if df.empty:
        st.warning("The input DataFrame is empty. Cannot create bar chart.")
        return

    city, month_year = df['trip'].iloc[0].split('-')
    month_name = month_year[:-2]
    year_suffix = month_year[-2:]
    year = 2000 + int(year_suffix)
    
    total_spending = df['total_spending'].iloc[0] #get the total spending from the first row.
    amount_i_spent = df['total_I_spent'].iloc[0]
    
    category_colors = {

      'Food': '#e74c3c', #red
      'Gas/Parking': '#3498db', #blue
      'Gift': '#f7dc6f', #yellow
      'Hotel': '#00ab41', #green
      "Public Transportation": '#f39c12', #orange
      "Flight": '#1a5276', #navy
      "Tickets": '#a569bd', #purple
      "Others": '#aab7b8' #lightgray
    }

    # Ensure all categories in the DataFrame are in the color mapping.  If not, use a default color.
    colors = [category_colors.get(category, '#aab7b8') for category in df['traveling_category']]

    # Create the bar chart
    fig = go.Figure(data=[go.Bar(
        x=df['traveling_category'],
        y=df['category_spending'],
        marker_color=colors,  # Apply the colors
        hovertemplate='<b>%{x}</b><br>Spending: $%{y:.2f}<extra></extra>'
    )])

    # Set the title
    fig.update_layout(
        title=f"{city} trip in {month_name}, {year} : Total Spendings: ${total_spending:.2f}, and I spent ${amount_i_spent:.2f}",
        title_font=dict(size=20),
        xaxis_title="Spending Category",
        xaxis_title_font=dict(size=18),
        yaxis_title="Amount Spent",
        yaxis_title_font=dict(size=18),
        margin=dict(l=0, r=0, t=50, b=0), #add margin
        xaxis=dict(tickfont=dict(size=15)), # Added x-axis tick label size
        yaxis=dict(tickfont=dict(size=18)) # Added x-axis tick label size
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)


  

