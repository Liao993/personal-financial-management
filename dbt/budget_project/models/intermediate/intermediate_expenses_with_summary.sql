{{ config(materialized='view') }}

SELECT
    *,
    CASE
        WHEN category = 'Home Deposit' THEN 'House'
        WHEN category = 'Saved for Love' THEN 'Saved for Love'
        WHEN category IN ('Donation', 'Gifts') THEN 'Donation and Gifts'
        WHEN category = 'Education' THEN 'Education'
        WHEN category = 'Traveling' THEN 'Traveling'
        WHEN category = 'Saved For Love' THEN 'Saved For Love'
        ELSE 'Daily Expenses'
    END AS summary_category
FROM {{ source('public', 'expense') }}