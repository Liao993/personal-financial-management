import streamlit as st
import pandas as pd
import html

def kpi(expense, income, transaction, all_year=False, fund_withdrawals=None, fund_deposits=None):

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
    earned_income = float(income['total_income'].sum())
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
    emergency_withdrawal = float(withdrawal_totals.get("Emergency Funds", 0.0))
    total_cash_pool = earned_income + emergency_withdrawal

    fund_deposits = fund_deposits if fund_deposits is not None else pd.DataFrame()
    deposit_totals = {}
    if not fund_deposits.empty:
        deposit_totals = fund_deposits.set_index("fund_category")["total_deposit"].to_dict()
    retirement_deposit = float(deposit_totals.get("Retirement Saving", 0.0))
    medium_deposit = float(deposit_totals.get("Medium-term Saving", 0.0))
    emergency_deposit = float(deposit_totals.get("Emergency Funds", 0.0))
    traveling_deposit = float(deposit_totals.get("Traveling Funds", 0.0))

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

    # Data configuration for the categories
    categories = [
        {"name": "Earning", "color": "orange", "sum": earned_income, "definition": "Income filter: income table records for the selected period, excluding Interest Earning and Capital Gain."},
        {"name": "Drawdown", "color": "#b71074", "sum": emergency_withdrawal, "definition": "The amount of money drawn down from the emergency fund, which is the sum of all withdrawals from the Emergency Fund category."},
        {"name": "All Spending", "color": "#e74c3c", "sum": total_spending, "definition": "Daily + House + Other All Spending, such as Education and other eligible categories. Saving (Medium and Traveling) Withdrawal is excluded."},
        {"name": "Daily", "color": "#f1c40f", "sum": expense[expense["summary_category"] == "Daily Expenses"]["amount"].sum(), "definition": "Daily-life maintenance spending such as car, grocery, household goods, cell phone, and transportation. House and Donation/Gifts are excluded."},
        {"name": "House", "color": "#bce784", "sum": house_sum, "definition": "House fund filter: fund_category = 'House'. This is the amount deposited/allocated from salary, not actual House spending."},
        {"name": "Offerings", "color": "#989fce", "sum": expense[expense["summary_category"] == "Donation and Gifts"]["amount"].sum(), "definition": "Offerings filter: summary_category = 'Donation and Gifts', covering Donation and Gifts categories."},
        {"name": "Grocery", "color": "#ff8fab", "sum": grocery_expense['amount'].sum(), "definition": grocery_note},
    ]

    # --- 2. Render Top Section (Headers, Totals, Averages) ---
    cols = st.columns(len(categories) + 1)

    # Column 1: Row Labels
    with cols[0]:
        st.markdown(
            f"<p style='font-size: 20px; text-align: center;'><b>Category</b></p>"
            f"<p style='font-size: 22px; text-align: center; color: gray;'>Total Sum</p>"
            f"<p style='font-size: 22px; text-align: center; color: gray;'>Monthly Avg</p>",
            unsafe_allow_html=True,
        )

    # Render data for columns 2 to N
    for i, cat in enumerate(categories):
        c_sum, c_avg, c_pct = get_stats(cat['sum'], total_cash_pool, divisor)
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
    bcols = st.columns(len(categories) + 1)

    with bcols[0]:
        st.markdown("<p style='font-size: 22px; text-align: center; font-weight: bold;'>% of Total Cash</p>", unsafe_allow_html=True)

    for i in range(len(categories)):
        with bcols[i+1]:
            display_pct = 100.0 if i == 0 else categories[i]['pct']
            st.markdown(f"<p style='font-size: 22px; text-align: center;'><b>{display_pct:.1f}%</b></p>", unsafe_allow_html=True)

    # --- 5. Fund Savings & Withdrawals Section ---
    fund_cols = st.columns(6)
    with fund_cols[0]:
        st.markdown(
            f"<p style='font-size: 19px; color: #1AA7EC; text-align: center; margin-bottom: 0;'><b>Retirement Saving</b></p>"
            f"<p style='font-size: 24px; color: #1AA7EC; text-align: center;'><b>${retirement_deposit:,.2f} ({retirement_deposit / earned_income:.1%})</b></p>",
            unsafe_allow_html=True,
        )
    with fund_cols[1]:
        st.markdown(
            f"<p style='font-size: 19px; color: #e67e22; text-align: center; margin-bottom: 0;'><b>Medium Saving</b></p>"
            f"<p style='font-size: 24px; color: #e67e22; text-align: center;'><b>${medium_deposit:,.2f} ({medium_deposit / earned_income:.1%})</b></p>",
            unsafe_allow_html=True,
        )
    with fund_cols[2]:
        st.markdown(
            f"<p style='font-size: 19px; color: #27ae60; text-align: center; margin-bottom: 0;'><b>Traveling Deposit</b></p>"
            f"<p style='font-size: 24px; color: #27ae60; text-align: center;'><b>${traveling_deposit:,.2f}</b> ({traveling_deposit / earned_income:.1%})</p>",
            unsafe_allow_html=True,
        )
    with fund_cols[3]:
        st.markdown(
            f"<p style='font-size: 19px; color: #b71074; text-align: center; margin-bottom: 0;'><b>Emergency Deposit</b></p>"
            f"<p style='font-size: 24px; color: #b71074; text-align: center;'><b>${emergency_deposit:,.2f} ({emergency_deposit / earned_income:.1%})</b></p>",
            unsafe_allow_html=True,
        )
    with fund_cols[4]:
        st.markdown(
            f"<p style='font-size: 19px; color: #e67e22; text-align: center; margin-bottom: 0;'><b>Medium Withdrawal</b></p>"
            f"<p style='font-size: 24px; color: #e67e22; text-align: center;'><b>${medium_withdrawal:,.2f}</b></p>",
            unsafe_allow_html=True,
        )
    with fund_cols[5]:
        st.markdown(
            f"<p style='font-size: 19px; color: #27ae60; text-align: center; margin-bottom: 0;'><b>Traveling Withdrawal</b></p>"
            f"<p style='font-size: 24px; color: #27ae60; text-align: center;'><b>${traveling_withdrawal:,.2f}</b></p>",
            unsafe_allow_html=True,
        )