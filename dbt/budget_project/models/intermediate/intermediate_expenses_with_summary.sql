{{ config(materialized='view') }}

SELECT
    *,
    CASE
        WHEN category = 'House' THEN 'House'
        WHEN category = 'Saved for Love' THEN 'Saved for Love'
        WHEN category IN ('Donation', 'Gift') THEN 'Donation and Gift'
        WHEN category = 'Education' THEN 'Education'
        WHEN category = 'Traveling' THEN 'Traveling'
        ELSE 'Daily Expense'
    END AS summary_category
FROM {{ source('public', 'expense') }}