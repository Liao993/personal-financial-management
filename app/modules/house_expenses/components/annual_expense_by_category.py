import streamlit as st # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

def create_category_bar_chart(expense):
    st.markdown("<h3 style='text-align: center; color: #5dade2;'>Annual House Spending by Category by Year</h3>", unsafe_allow_html=True)
    
    # 1. Filter out "Extra Mortgage"
    expense = expense[expense['house_category'] != 'Extra Mortgage'].copy()
    
    # 2. Define specific categories and consolidate others
    selected_categories = [
        'Mortgage', 'Insurance', 'Tax', 'Internet', 'Electricity', 
        'Water & Sewage', 'Oil', 'Snow Removal', 'Repair'
    ]
    expense.loc[~expense['house_category'].isin(selected_categories), 'house_category'] = 'Others'  

    # 3. Define Ordering Logic (Top to Bottom)
    primary_order = ['Mortgage', 'Tax']
    other_cats = [c for c in expense['house_category'].unique() if c not in primary_order]
    
    # For Horizontal charts, Seaborn plots from the bottom up. 
    # To get Mortgage at the top, it must be the LAST item in the categorical list.
    final_order = sorted(other_cats) + ['Tax', 'Mortgage'] 
    expense['house_category'] = pd.Categorical(expense['house_category'], categories=final_order, ordered=True)
    
    # 4. PRE-CALCULATE ANNUAL TOTALS
    annual_totals = expense.groupby('year')['amount'].sum().to_dict()

    # 5. Group and process data
    summary_data = expense.groupby(['year', 'house_category'], observed=True)['amount'].sum().reset_index()
    summary_data['year'] = summary_data['year'].astype(str)
    hue_order = sorted(summary_data['year'].unique())

    # 6. Create the Plot
    plt.figure(figsize=(12, 10)) # Taller for horizontal rows
    sns.set_style("whitegrid")
    
    # SWAP: y=house_category, x=amount
    ax = sns.barplot(
        y='house_category', 
        x='amount', 
        hue='year', 
        data=summary_data,
        palette="viridis",
        order=final_order[::-1] # Reverse the order here to force Mortgage to the top
    )

    # 7. HORIZONTAL ANNOTATIONS (Amount + Percentage)
    for i, container in enumerate(ax.containers):
        current_year = hue_order[i]
        year_total = float(annual_totals.get(int(current_year), 1))
        
        for bar in container:
            width = float(bar.get_width())
            if width > 0:
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