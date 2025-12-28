{{ config(materialized='view') }}

SELECT
    *,
    (amount / NULLIF(COALESCE(amount_for_number_of_travelers, 1), 0)) * COALESCE(paid_for_number_of_travlerers, 1) AS amount_I_spend,
    CASE
        --WHEN category = 'House' THEN 'House'
        -- for data clean-up purposes
        WHEN category = 'Saved for Love' THEN 'Saved for Love'
        WHEN category = 'Saved For Love' THEN 'Saved For Love'
        WHEN category IN ('Donation', 'Gifts') THEN 'Donation and Gifts'
        WHEN category = 'Education' THEN 'Education'
        WHEN category = 'Traveling' THEN 'Traveling'
        
        ELSE 'Daily Expenses'
    END AS summary_category,

    CASE
        WHEN house_category = 'Mortgage' THEN 'Mortgage'
        WHEN house_category = 'Extra Mortgage' THEN 'Extra Mortgage'
        WHEN house_category IN ('Internet', 'Electricity', 'Insurance', 'Water & Sewage','Oil', 'Snow Removal') THEN 'Regular Expenses'
        WHEN house_category LIKE '%Repair%' THEN 'Repairs'
        WHEN house_category LIKE '%Tax%' THEN 'Tax'
        ELSE 'Other'
    END AS house_summary_category
FROM {{ source('public', 'expense') }}