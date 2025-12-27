import streamlit as st # type: ignore
import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

def create_summary_category_chart(expense):
    st.markdown("<h3 style='text-align: center; color: #5dade2;'>Annual Expense by Summary Category</h3>", unsafe_allow_html=True)
    
    df = expense.copy()
    df.rename(columns={'house_summary_category': 'summary_category'}, inplace=True)
    
    # 1. Calculate Annual Total (Excluding Extra Mortgage)
    annual_totals = df[df['summary_category'] != 'Extra Mortgage'].groupby('year')['amount'].sum().to_dict()
    
    # 2. Group data by year and category
    summary_data = df.groupby(['year', 'summary_category'])['amount'].sum().reset_index()
    
    # 3. Add the "Total Spending" rows
    total_rows = []
    for yr, val in annual_totals.items():
        total_rows.append({'year': yr, 'summary_category': 'Total Spending', 'amount': val})
    
    final_df = pd.concat([summary_data, pd.DataFrame(total_rows)], ignore_index=True)
    
    # 4. Define Order and Categorical type
    # Make sure spellings match your database (Maintenance vs Maintainance)
    custom_order = ['Total Spending', 'Extra Mortgage', 'Mortgage', 'Maintenance', 'Repairs', 'Tax', 'Other']
    final_df['summary_category'] = pd.Categorical(
        final_df['summary_category'], 
        categories=custom_order, 
        ordered=True
    )
    hue_order = sorted(final_df['year'].unique())

    # 5. Plotting
    plt.figure(figsize=(12, 10))
    sns.set_style("whitegrid")
    
    ax = sns.barplot(
        data=final_df,
        y='summary_category',
        x='amount',
        hue='year',
        palette="muted",
        order=custom_order # Explicitly set order for horizontal bars
    )
    
    # 6. HORIZONTAL ANNOTATIONS (Amount + Percentage)
    for i, container in enumerate(ax.containers):
        current_year = hue_order[i]
        year_total = float(annual_totals.get(int(current_year), 1))
        for bar in container:
            width = float(bar.get_width())
            pct = (width / year_total) * 100
            label = f' ${width:,.0f} ({pct:.1f}%)'
                
            ax.annotate(
                label,
                (width, bar.get_y() + bar.get_height() / 2.),
                ha='left', va='center',
                xytext=(5, 0),
                textcoords='offset points',
                fontsize=16,
                color='black'
            )

    # Styling
    plt.xlabel(None)
    plt.xticks(None)
    plt.ylabel(None)
    plt.yticks(fontsize=18)
    plt.legend(title="Year", loc='lower right', fontsize=18)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    st.pyplot(plt.gcf())