{%- macro get_summary_category(col) -%}
    {#1. List all Category #}
    {%- set simple_category = ['Saved For Love', 'Education', 'Traveling', "House"] -%}
    CASE 
        {# For Loop for 1:1 Map Category #}
        {%- for cat in simple_category %}
            WHEN {{col}} = '{{cat}}' THEN '{{cat}}'
        {%-endfor %}
        WHEN {{col}} IN ('Donation', 'Gifts') THEN 'Donation and Gifts'
        ELSE 'Daily Expenses'
    END
{%- endmacro -%}