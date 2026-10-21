def build_metric_query(metric_def: dict, start_date=None, end_date=None):
    """Return (sql, params) for one non-derived metric definition."""
    table = metric_def["table"]
    join_clause = metric_def.get("join", "") or ""
    aggregation = metric_def["aggregation"]
    filters = list(metric_def.get("filters", []))
    date_column = metric_def.get("date_column")
    params = []

    if date_column and start_date and end_date:
        filters.append(f"{date_column} BETWEEN %s AND %s")
        params.extend([start_date, end_date])

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(f"({item})" for item in filters)

    sql = f"""
        SELECT {aggregation} AS value
        FROM {table}
        {join_clause}
        {where_clause}
    """
    return sql, tuple(params)
