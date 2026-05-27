{{ config(materialized='view') }}


SELECT
    *,
    {# Calculate amount I spend #}
    COALESCE(
    (amount / NULLIF(amount_for_number_of_travelers, 0)) * paid_for_number_of_travlerers, 
    0
    ) AS amount_I_spend,

    {# Call the Macro for Summary Category #}
    {{ get_summary_category('category') }} AS summary_category,

    {#  House Summary Category #}
    CASE
        WHEN house_category = 'Mortgage' THEN 'Mortgage'
        WHEN house_category = 'Extra Mortgage' THEN 'Extra Mortgage'
        WHEN house_category IN ('Internet', 'Electricity', 'Insurance', 'Water & Sewage','Oil', 'Snow Removal') THEN 'Regular Expenses'
        WHEN house_category LIKE '%Repair%' THEN 'Repairs'
        WHEN house_category LIKE '%Tax%' THEN 'Tax'
        ELSE 'Other'
    END AS house_summary_category

FROM {{ source('public', 'expense') }}

{#
    exclude_from_monthly = TRUE means the expense is paid from a fund category
    (e.g. traveling, hotel, laptop from medium-term saving).
    These are already tracked as withdrawal transactions in the transactions table,
    so including them here would double-count spending in monthly and historical reports.
    House expenses are also excluded here — they are tracked via the house pipeline.
#}
WHERE exclude_from_monthly = FALSE
  AND category != 'House'
