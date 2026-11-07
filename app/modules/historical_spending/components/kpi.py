import streamlit as st
import pandas as pd
import html

def kpi(expense, income, transaction, all_year=False, fund_withdrawals=None):


    # --- 1. Calculations ---
    expense = expense.copy()
    expense['date'] = pd.to_datetime(expense['date'])
    if all_year:
        unique_month = expense['date'].dt.to_period('M').nunique()
    else:
        expense['month'] = expense['date'].dt.month
        unique_month = expense['month'].nunique()
    
    # Avoid division by zero
    divisor = unique_month if unique_month > 0 else 1

    # Financial Totals (Cast to float for math safety)
    total_income = float(income['total_income'].sum())
    spending_expense = expense[expense["category"] != "Traveling"]
    total_expense = float(spending_expense['amount'].sum())
    
    house_df = transaction[transaction['fund_category'] == 'House']
    house_sum = float(house_df['total_amount'].sum()) if not house_df.empty else 0.0
    
    total_spending = total_expense + house_sum

    grocery_expense = expense[expense["category"] == "Grocery"].copy()
    grocery_items = grocery_expense.get(
        "items", pd.Series("", index=grocery_expense.index)
    ).fillna("").astype(str).str.upper()
    grocery_store = pd.Series("OTHERS", index=grocery_expense.index)
    grocery_store = grocery_store.mask(grocery_items.str.contains("SUPER", na=False), "Loblaws")
    grocery_store = grocery_store.mask(grocery_items.str.contains("NOFRILL", na=False), "Loblaws")
    grocery_store = grocery_store.mask(grocery_items.str.contains("MIKE & ANDREEA'S", na=False), "Loblaws")
    grocery_store = grocery_store.mask(grocery_items.str.contains("COSTCO", na=False), "Costco")
    grocery_store = grocery_store.mask(grocery_items.str.contains("SOBEY", na=False), "Sobeys")
    grocery_breakdown = grocery_expense.assign(store=grocery_store).groupby("store")["amount"].sum()
    grocery_note = "Grocery filter: category = 'Grocery'.\n" + (
        "\n".join(f"- {store}: ${amount:,.2f}" for store, amount in grocery_breakdown.sort_values(ascending=False).items())
        if not grocery_breakdown.empty else "- No grocery records"
    )
    fund_withdrawals = fund_withdrawals if fund_withdrawals is not None else pd.DataFrame()
    withdrawal_totals = {}
    if not fund_withdrawals.empty:
        withdrawal_totals = fund_withdrawals.set_index("fund_category")["total_withdrawal"].to_dict()
    medium_withdrawal = float(withdrawal_totals.get("Medium-term Saving", 0.0))
    traveling_withdrawal = float(withdrawal_totals.get("Traveling Funds", 0.0))

    st.markdown(
        """
        <style>
        .kpi-info {
            position: relative;
            display: inline-block;
            color: #888;
            font-size: 14px;
            cursor: help;
        }
        .kpi-info::after {
            content: attr(data-tooltip);
            visibility: hidden;
            opacity: 0;
            position: absolute;
            z-index: 9999;
            left: 50%;
            bottom: 150%;
            transform: translateX(-50%);
            width: 280px;
            padding: 10px;
            border-radius: 6px;
            background: #222;
            color: #fff;
            text-align: left;
            white-space: pre-line;
            font-size: 13px;
            font-weight: normal;
            line-height: 1.35;
            box-shadow: 0 2px 8px rgba(0,0,0,.35);
            pointer-events: none;
            transition: opacity .15s ease;
        }
        .kpi-info:hover::after {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Helper function for data processing
    def get_stats(current_sum, total_inc, div):
        current_sum = float(current_sum)
        avg = current_sum / div
        pct = (current_sum / total_inc * 100) if total_inc > 0 else 0
        return current_sum, avg, pct

    # --- 2. Render Top Section (Headers, Totals, Averages) ---
    cols = st.columns(10)

    # Column 1: Row Labels
    with cols[0]:
        st.markdown(
            f"<p style='font-size: 20px; text-align: center;'><b>Category</b></p>"
            f"<p style='font-size: 22px; text-align: center; color: gray;'>Total Sum</p>"
            f"<p style='font-size: 22px; text-align: center; color: gray;'>Monthly Avg</p>",
            unsafe_allow_html=True,
        )

    # Data configuration for the categories
    categories = [
        {"name": "Earning", "color": "orange", "sum": total_income, "definition": "Income filter: income table records for the selected period, excluding Interest Earning and Capital Gain."},
        {"name": "All Spending", "color": "#e74c3c", "sum": total_spending, "definition": "Eligible expense records where exclude_from_monthly = FALSE, category != 'House', category != 'Traveling', and house_category IS NULL, plus non-expense-linked House fund allocations (expense_id IS NULL). This includes Daily, Offerings, Grocery, and other eligible non-travel categories; it is not just Daily + House."},
        {"name": "Daily", "color": "#f1c40f", "sum": expense[expense["summary_category"] == "Daily Expenses"]["amount"].sum(), "definition": "Expense filter: summary_category = 'Daily Expenses'. Donation/Gifts and House records are excluded."},
        {"name": "House", "color": "#bce784", "sum": house_sum, "definition": "House fund filter: fund_category = 'House'. This is the amount deposited/allocated from salary, not actual House spending."},
        {"name": "Offerings", "color": "#989fce", "sum": expense[expense["summary_category"] == "Donation and Gifts"]["amount"].sum(), "definition": "Offerings filter: summary_category = 'Donation and Gifts', covering Donation and Gifts categories."},
        {"name": "Grocery", "color": "#ff8fab", "sum": grocery_expense['amount'].sum(), "definition": grocery_note},
        {"name": "Retirement", "color": "#1AA7EC", "sum": transaction[(transaction['fund_category'] == 'Retirement Saving')]['total_amount'].sum(), "definition": "Retirement filter: fund_category = 'Retirement Saving' in the transaction summary."},
        {"name": "Medium Withdrawal", "color": "#9b59b6", "sum": medium_withdrawal, "definition": "Withdrawal filter: transaction_type = 'Withdrawal' and fund_category = 'Medium-term Saving'. Expense-linked and manual withdrawals are included."},
        {"name": "Traveling Withdrawal", "color": "#e67e22", "sum": traveling_withdrawal, "definition": "Withdrawal filter: transaction_type = 'Withdrawal' and fund_category = 'Traveling Funds'. Expense-linked and manual withdrawals are included."},
    ]

    # Render data for columns 2-8
    for i, cat in enumerate(categories):
        c_sum, c_avg, c_pct = get_stats(cat['sum'], total_income, divisor)
        categories[i]['pct'] = c_pct # Save for bottom row
        
        with cols[i+1]:
            definition = html.escape(cat.get("definition", ""))
            st.markdown(
                f"<p style='font-size: 20px; color: {cat['color']}; text-align: center;'><b>{cat['name']}"
                f" <span class=\"kpi-info\" title=\"{definition}\" data-tooltip=\"{definition}\">ⓘ</span></b></p>"
                f"<p style='font-size: 22px; text-align: center;'>${c_sum:,.0f}</p>"
                f"<p style='font-size: 22px; text-align: center;'>${c_avg:,.0f}</p>",
                unsafe_allow_html=True,
            )

    # --- 3. The Whole-Width Dashed Line ---
    st.markdown("<hr style='margin: 0px; border: none; border-top: 2px dashed #bbb;'>", unsafe_allow_html=True)
    # --- 4. Render Bottom Section (% by Income) ---
    bcols = st.columns(10)

    with bcols[0]:
        st.markdown("<p style='font-size: 22px; text-align: center; font-weight: bold;'>% of Income</p>", unsafe_allow_html=True)

    for i in range(len(categories)):
        with bcols[i+1]:
            # Earning (index 0) is 100%, others use their calculated %
            display_pct = 100.0 if i == 0 else categories[i]['pct']
            st.markdown(f"<p style='font-size: 22px; text-align: center;'><b>{display_pct:.1f}%</b></p>", unsafe_allow_html=True)
