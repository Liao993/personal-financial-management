import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st # type: ignore
from utils.data import traveling_category_options

def create_trip_spending_stacked_bar_chart(df):
    """
    Creates a normalized stacked bar chart to visualize trip spending by category.

    Args:
        df (pd.DataFrame): DataFrame with columns 'trip', 'amount', and 'traveling_category'.
    """
    all_categories = traveling_category_options
  
    # Define colors
    category_colors = {
        'Food': '#e74c3c', #red
        'Gas': '#3498db', #blue
        'Gift': '#f7dc6f', #yellow
        'Hotel': '#00ab41', #green
        "Public Transportation": '#f39c12', #orange
        "Flight": '#1a5276', #navy
        "Tickets": '#a569bd', #purple
        "Others": '#aab7b8' #lightgray
    }
    palette = {cat: category_colors.get(cat, 'gray') for cat in all_categories}

    # 4. Create the stacked bar chart using seaborn
    plt.figure(figsize=(20, 8))  # Adjust figure size as needed
    ax = sns.barplot(
        x='trip', 
        y='category_spending',  
        hue='traveling_category',  # Use traveling_category for the colors (stacking)
        data=df,
        orient='v', # Horizontal bars
        palette=palette
    )

  

    # 5. Set the layout of the chart
    plt.ylabel('Amount of Spending', fontsize=20)
    plt.xticks(fontsize=24)
    plt.yticks(ticks=range(0, 1500, 100), fontsize=20)
    plt.ylim(0, 1500)  # Set x-axis limit for percentages
    plt.legend(fontsize= 20, title='Category', bbox_to_anchor=(1.05, 1), loc='upper left') 
    plt.grid(axis='y')
    plt.tight_layout()


    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Display the chart using streamlit
    st.pyplot(plt.gcf(), use_container_width=True)



 
