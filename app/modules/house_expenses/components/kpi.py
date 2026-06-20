

# get persoonal income deposit

# 1. Get all  total Mortgage Amount (pct for total Mortgage/total deposit)
# 2. Get all  total Extra Mortgage Amount
# 3. Get all  total Tax Amount
# 4. Get all  total Insurance Amount
# 5. Get all  total energy total (Oil + Electricity)
# 6. Get all  water total & sewage total
import streamlit as st #type:ignore
import streamlit.components.v1 as components #type:ignore
import pandas as pd #type:ignore
from decimal import Decimal
from utils.data import mortgage_payment_history, total_principal_paid


PRINCIPAL_PAID = total_principal_paid
MORTGAGE_HISTORY = mortgage_payment_history


def to_decimal(value):
    return value if isinstance(value, Decimal) else Decimal(str(value))


def money_sum(series):
    return to_decimal(series.sum())


def annualized(value, months_between):
    return value / months_between * 12


def percentage(part, total):
    if total == 0:
        return Decimal("0")
    return part / total * 100


def render_kpi_card(title, total, annual_average, color, note=None):
    note_html = f"<div class='house-kpi-note'>{note}</div>" if note else ""
    st.markdown(
        f"""
        <div class="house-kpi-card" style="border-top-color: {color};">
            <div class="house-kpi-title" style="color: {color};">{title}</div>
            <div class="house-kpi-value">${total:.2f}</div>
            <div class="house-kpi-subtitle">Annual avg</div>
            <div class="house-kpi-average">${annual_average:.2f}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mix_card(
    title,
    total_cash_paid,
    principal_paid,
    principal_pct,
    interest_paid,
    interest_pct,
    operating_cost,
    operating_pct,
    color,
):
    st.markdown(
        f"""
        <div class="house-kpi-card" style="border-top-color: {color};">
            <div class="house-kpi-title" style="color: {color};">{title}</div>
            <div class="house-kpi-mix-total">${total_cash_paid:.2f}</div>
            <div class="house-kpi-mix-row">
                <span>Principal</span>
                <strong>${principal_paid:.2f}<em style="margin-left: 10px;">{principal_pct:.1f}%</em></strong>
            </div>
            <div class="house-kpi-mix-row">
                <span>Interest</span>
                <strong>${interest_paid:.2f}<em style="margin-left: 10px;">{interest_pct:.1f}%</em></strong>
            </div>
            <div class="house-kpi-mix-row">
                <span>Operating cost</span>
                <strong>${operating_cost:.2f}<em style="margin-left: 10px;">{operating_pct:.1f}%</em></strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mortgage_summary(
    total_mortgage,
    total_principal_paid,
    total_interest_paid,
    avg_annual_mortgage,
    principal_mortgage_pct,
    interest_mortgage_pct,
):
    return f"""
        <div class="house-kpi-mortgage-panel mortgage">
            <div class="house-kpi-panel-title mortgage">Mortgage Totals</div>
            <div class="house-kpi-total-label">Total mortgage paid</div>
            <div class="house-kpi-total-amount">${total_mortgage:.2f}</div>
            <div class="house-kpi-annual-line">Annual avg <strong>${avg_annual_mortgage:.2f}</strong></div>
            <div class="house-kpi-mortgage-split">
                <div class="house-kpi-mini-metric principal">
                    <span>Principal paid</span>
                    <strong>${total_principal_paid:.2f}</strong>
                    <em>{principal_mortgage_pct:.1f}% of mortgage</em>
                </div>
                <div class="house-kpi-mini-metric interest">
                    <span>Interest paid</span>
                    <strong>${total_interest_paid:.2f}</strong>
                    <em>{interest_mortgage_pct:.1f}% of mortgage</em>
                </div>
            </div>
        </div>
    """


def build_mortgage_history_rows(total_principal_paid, total_interest_paid, current_year):
    history_rows = []
    recorded_principal = Decimal("0")
    recorded_interest = Decimal("0")

    for year in sorted(MORTGAGE_HISTORY):
        principal = MORTGAGE_HISTORY[year]["principal"]
        interest = MORTGAGE_HISTORY[year]["interest"]
        recorded_principal += principal
        recorded_interest += interest
        history_rows.append((year, principal, interest))

    current_principal = total_principal_paid - recorded_principal
    current_interest = total_interest_paid - recorded_interest
    if current_principal != 0 or current_interest != 0:
        history_rows.append((current_year, current_principal, current_interest))

    return history_rows


def render_mortgage_history(rows):
    history_rows = ""
    for year, principal, interest in rows:
        total = principal + interest
        principal_pct = percentage(principal, total)
        interest_pct = percentage(interest, total)
        history_rows += f"""
            <div class="house-kpi-history-row">
                <span>{year}</span>
                <strong>${principal:.2f}</strong>
                <strong>${interest:.2f}</strong>
                <strong>${total:.2f}</strong>
                <em>{principal_pct:.1f}%</em>
                <em>{interest_pct:.1f}%</em>
            </div>
        """

    return f"""
        <div class="house-kpi-mortgage-panel history">
            <div class="house-kpi-panel-title history">Principal vs. Interest by Year</div>
            <div class="house-kpi-history-grid">
                <div class="house-kpi-history-head">
                    <span>Year</span>
                    <span>Principal</span>
                    <span>Interest</span>
                    <span>Total</span>
                    <span>Principal %</span>
                    <span>Interest %</span>
                </div>
                {history_rows}
            </div>
        </div>
    """


def render_mortgage_breakdown(
    total_mortgage,
    total_principal_paid,
    total_interest_paid,
    avg_annual_mortgage,
    principal_mortgage_pct,
    interest_mortgage_pct,
    history_rows,
):
    summary_html = render_mortgage_summary(
        total_mortgage,
        total_principal_paid,
        total_interest_paid,
        avg_annual_mortgage,
        principal_mortgage_pct,
        interest_mortgage_pct,
    )
    history_html = render_mortgage_history(history_rows)

    components.html(
        f"""
        <style>
            body {{
                margin: 0;
                background: transparent;
                font-family: "Source Sans Pro", sans-serif;
            }}
            .house-kpi-mortgage-layout {{
                display: grid;
                grid-template-columns: minmax(300px, 1fr) minmax(480px, 1.35fr);
                gap: 16px;
                align-items: stretch;
            }}
            .house-kpi-mortgage-panel {{
                box-sizing: border-box;
                min-height: 286px;
                padding: 16px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
            }}
            .house-kpi-mortgage-panel.mortgage {{
                border-top: 4px solid #ca8a04;
            }}
            .house-kpi-mortgage-panel.history {{
                border-top: 4px solid #0f766e;
            }}
            .house-kpi-panel-title {{
                padding-top: 2px;
                font-size: 1rem;
                font-weight: 800;
            }}
            .house-kpi-panel-title.mortgage {{
                color: #ca8a04;
            }}
            .house-kpi-panel-title.history {{
                color: #0f766e;
            }}
            .house-kpi-total-label {{
                margin-top: 18px;
                color: #374151;
                font-size: 0.86rem;
                font-weight: 700;
            }}
            .house-kpi-total-amount {{
                margin-top: 4px;
                color: #111827;
                font-size: 1.95rem;
                line-height: 1.1;
                font-weight: 850;
            }}
            .house-kpi-annual-line {{
                margin-top: 5px;
                color: #6b7280;
                font-size: 0.82rem;
            }}
            .house-kpi-annual-line strong {{
                color: #111827;
                font-size: 0.9rem;
            }}
            .house-kpi-mortgage-split {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 12px;
                margin-top: 18px;
            }}
            .house-kpi-mini-metric {{
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: #f9fafb;
            }}
            .house-kpi-mini-metric span {{
                display: block;
                font-size: 0.9rem;
                font-weight: 800;
            }}
            .house-kpi-mini-metric.principal span {{
                color: #65a30d;
            }}
            .house-kpi-mini-metric.interest span {{
                color: #ea580c;
            }}
            .house-kpi-mini-metric strong {{
                display: block;
                margin: 4px 0;
                color: #111827;
                font-size: 1.18rem;
            }}
            .house-kpi-mini-metric em {{
                display: block;
                color: #4b5563;
                font-size: 0.82rem;
                font-style: normal;
            }}
            .house-kpi-history-head,
            .house-kpi-history-row {{
                display: grid;
                grid-template-columns: 0.75fr repeat(5, minmax(0, 1fr));
                gap: 8px;
                align-items: center;
                text-align: right;
            }}
            .house-kpi-history-head {{
                color: #6b7280;
                font-size: 0.72rem;
                font-weight: 800;
                text-transform: uppercase;
                border-bottom: 1px solid #e5e7eb;
                padding: 9px 0 8px;
            }}
            .house-kpi-history-row {{
                color: #111827;
                border-bottom: 1px solid #f3f4f6;
                padding: 9px 0;
                font-size: 0.88rem;
                font-weight: 650;
            }}
            .house-kpi-history-row em {{
                color: #374151;
                font-style: normal;
            }}
            .house-kpi-history-head span:first-child,
            .house-kpi-history-row span:first-child {{
                text-align: left;
            }}
            @media (max-width: 900px) {{
                .house-kpi-mortgage-layout {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
        <div class="house-kpi-mortgage-layout">
            {summary_html}
            {history_html}
        </div>
        """,
        height=320,
        scrolling=False,
    )


def latest_mortgage_year(expense, fallback_year):
    if "year" not in expense.columns:
        return fallback_year

    mortgage_years = expense.loc[expense["house_category"] == "Mortgage", "year"].dropna()
    if mortgage_years.empty:
        return fallback_year

    return int(mortgage_years.max())


def annual_kpi(expense, transaction):
    st.markdown(
        """
        <style>
            .house-kpi-section-title {
                font-size: 1.35rem;
                font-weight: 800;
                margin: 1.35rem 0 0.55rem;
            }
            .house-kpi-card {
                height: 214px;
                padding: 16px 16px 14px;
                border: 1px solid #d1d5db;
                border-top: 4px solid;
                border-radius: 8px;
                background: #ffffff;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
            }
            .house-kpi-title {
                height: 42px;
                font-size: 0.98rem;
                line-height: 1.2;
                font-weight: 700;
            }
            .house-kpi-value {
                margin-top: 10px;
                color: #111827;
                font-size: 1.6rem;
                line-height: 1.15;
                font-weight: 800;
            }
            .house-kpi-subtitle {
                margin-top: 11px;
                color: #6b7280;
                font-size: 0.78rem;
                text-transform: uppercase;
            }
            .house-kpi-average {
                color: #111827;
                font-size: 1.05rem;
                font-weight: 700;
            }
            .house-kpi-note {
                margin-top: 8px;
                color: #4b5563;
                font-size: 0.82rem;
                line-height: 1.25;
            }
            .house-kpi-mix-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
                margin-top: 8px;
                color: #374151;
                font-size: 0.92rem;
            }
            .house-kpi-mix-row strong {
                color: #111827;
                font-size: 0.96rem;
            }
            .house-kpi-mix-row em {
                color: #4f46e5;
                font-size: 0.86rem;
                font-style: normal;
            }
            .house-kpi-mix-total {
                margin-top: 4px;
                padding-bottom: 9px;
                border-bottom: 1px solid #e5e7eb;
                color: #111827;
                font-size: 1.48rem;
                line-height: 1.1;
                font-weight: 800;
            }
            .house-kpi-mortgage-layout {
                display: grid;
                grid-template-columns: minmax(300px, 1fr) minmax(480px, 1.35fr);
                gap: 16px;
                align-items: stretch;
            }
            .house-kpi-mortgage-panel {
                min-height: 286px;
                padding: 16px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
            }
            .house-kpi-mortgage-panel.mortgage {
                border-top: 4px solid #ca8a04;
            }
            .house-kpi-mortgage-panel.history {
                border-top: 4px solid #0f766e;
            }
            .house-kpi-panel-title {
                padding-top: 2px;
                font-size: 1rem;
                font-weight: 800;
            }
            .house-kpi-panel-title.mortgage {
                color: #ca8a04;
            }
            .house-kpi-panel-title.history {
                color: #0f766e;
            }
            .house-kpi-total-label {
                margin-top: 18px;
                color: #374151;
                font-size: 0.86rem;
                font-weight: 700;
            }
            .house-kpi-total-amount {
                margin-top: 4px;
                color: #111827;
                font-size: 1.95rem;
                line-height: 1.1;
                font-weight: 850;
            }
            .house-kpi-annual-line {
                margin-top: 5px;
                color: #6b7280;
                font-size: 0.82rem;
            }
            .house-kpi-annual-line strong {
                color: #111827;
                font-size: 0.9rem;
            }
            .house-kpi-mini-metric {
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: #f9fafb;
            }
            .house-kpi-mini-metric span {
                display: block;
                font-size: 0.9rem;
                font-weight: 800;
            }
            .house-kpi-mini-metric.principal span {
                color: #65a30d;
            }
            .house-kpi-mini-metric.interest span {
                color: #ea580c;
            }
            .house-kpi-mini-metric strong {
                display: block;
                margin: 4px 0;
                color: #111827;
                font-size: 1.18rem;
            }
            .house-kpi-mini-metric em {
                display: block;
                color: #4b5563;
                font-size: 0.82rem;
                font-style: normal;
            }
            .house-kpi-history-head {
                display: grid;
                grid-template-columns: 0.75fr repeat(5, minmax(0, 1fr));
                gap: 8px;
                color: #6b7280;
                font-size: 0.72rem;
                font-weight: 800;
                text-transform: uppercase;
                text-align: right;
                border-bottom: 1px solid #e5e7eb;
                padding: 9px 0 8px;
            }
            .house-kpi-history-row {
                display: grid;
                grid-template-columns: 0.75fr repeat(5, minmax(0, 1fr));
                gap: 8px;
                color: #111827;
                border-bottom: 1px solid #f3f4f6;
                padding: 9px 0;
                text-align: right;
                font-size: 0.88rem;
                font-weight: 650;
            }
            .house-kpi-history-row em {
                color: #374151;
                font-style: normal;
            }
            .house-kpi-history-head span:first-child,
            .house-kpi-history-row span:first-child {
                text-align: left;
            }
            @media (max-width: 900px) {
                .house-kpi-mortgage-layout {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        <h2 style='text-align: center;'>Total House Spending Overview</h2>
        """,
        unsafe_allow_html=True,
    )
    #get how many from from 2024-02-24 until today
    start_date = pd.to_datetime('2024-02-24')
    end_date = pd.to_datetime('today')

    # Calculate the difference in years and months
    # Adding 1 makes it inclusive of both the start and end months
    months_between = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1


    house_sum = money_sum(transaction[transaction['fund_category'] == 'House']['amount'])
    total_cash_outflow = money_sum(expense[expense["house_category"] != "Extra Mortgage"]["amount"])
    total_extra_mortgage = money_sum(expense[expense["house_category"] == "Extra Mortgage"]["amount"])
    total_principal_paid = PRINCIPAL_PAID - total_extra_mortgage
    total_house_cost = total_cash_outflow - total_principal_paid

    total_mortgage = money_sum(expense[expense["house_category"] == "Mortgage"]["amount"])
    total_interest_paid = total_mortgage - total_principal_paid
    total_operating_cost = total_cash_outflow - total_mortgage
    principal_cash_pct = percentage(total_principal_paid, total_cash_outflow)
    interest_cash_pct = percentage(total_interest_paid, total_cash_outflow)
    operating_cash_pct = percentage(total_operating_cost, total_cash_outflow)
    principal_mortgage_pct = percentage(total_principal_paid, total_mortgage)
    interest_mortgage_pct = percentage(total_interest_paid, total_mortgage)

    regular_maintenance_category = ['Regular Expenses', 'Tax']
    total_maintenance_cost = money_sum(
        expense[expense["house_summary_category"].isin(regular_maintenance_category)]['amount']
    )
    other_operating_category = ['Regular Expenses', 'Tax', 'Mortgage', 'Extra Mortgage']
    total_other_operating_cost = money_sum(
        expense[~expense["house_summary_category"].isin(other_operating_category)]['amount']
    )
    repair_mask = expense["house_summary_category"].str.contains("Repairs", case=False, na=False)
    total_repair_cost = money_sum(
        expense[
            repair_mask
            & ~expense["house_summary_category"].isin(['Mortgage', 'Extra Mortgage'])
        ]['amount']
    )
    total_move_in_other_cost = total_other_operating_cost - total_repair_cost

    energy_use_category = ['Electricity', 'Oil']
    total_energy_cost = money_sum(expense[expense["house_category"].isin(energy_use_category)]['amount'])
    total_water_cost = money_sum(expense[expense["house_category"] == "Water & Sewage"]["amount"])

    st.markdown("<div class='house-kpi-section-title'>Overview</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("House Income Deposit", house_sum, annualized(house_sum, months_between), "#d97706")
    with col2:
        render_kpi_card(
            "Total Cash Paid",
            total_cash_outflow,
            annualized(total_cash_outflow, months_between),
            "#dc2626",
            "Mortgage payment plus operating costs. Principal included.",
        )
    with col3:
        render_kpi_card(
            "True House Cost",
            total_house_cost,
            annualized(total_house_cost, months_between),
            "#b91c1c",
            "Interest plus operating costs. Principal excluded.",
        )
    with col4:
        render_mix_card(
            "Total Cash Paid Mix",
            total_cash_outflow,
            total_principal_paid,
            principal_cash_pct,
            total_interest_paid,
            interest_cash_pct,
            total_operating_cost,
            operating_cash_pct,
            "#4f46e5",
        )

    st.markdown("<div class='house-kpi-section-title'>Mortgage Breakdown</div>", unsafe_allow_html=True)
    mortgage_history_year = latest_mortgage_year(expense, end_date.year)
    mortgage_history_rows = build_mortgage_history_rows(
        total_principal_paid,
        total_interest_paid,
        mortgage_history_year,
    )
    render_mortgage_breakdown(
        total_mortgage,
        total_principal_paid,
        total_interest_paid,
        annualized(total_mortgage, months_between),
        principal_mortgage_pct,
        interest_mortgage_pct,
        mortgage_history_rows,
    )

    st.markdown("<div class='house-kpi-section-title'>Operating Costs</div>", unsafe_allow_html=True)
    col7, col8, col9, col10, col11 = st.columns(5)
    with col7:
        render_kpi_card(
            "Regular Maintenance + Tax",
            total_maintenance_cost,
            annualized(total_maintenance_cost, months_between),
            "#28913f",
        )
    with col8:
        render_kpi_card(
            "Repairs",
            total_repair_cost,
            annualized(total_repair_cost, months_between),
            "#7c3aed",
        )
    with col9:
        render_kpi_card(
            "Move-In, Furniture + Other",
            total_move_in_other_cost,
            annualized(total_move_in_other_cost, months_between),
            "#9333ea",
        )
    with col10:
        render_kpi_card("Energy", total_energy_cost, annualized(total_energy_cost, months_between), "#0284c7")
    with col11:
        render_kpi_card("Water & Sewage", total_water_cost, annualized(total_water_cost, months_between), "#e74c3c")
