from __future__ import annotations

import re


DIMENSION_ALIASES = {
    "month": lambda date_column: f"DATE_TRUNC('month', {date_column})::date",
    "year": lambda date_column: f"EXTRACT(YEAR FROM {date_column})::integer",
}


def _dimension_expression(metric_def: dict, dimension: str) -> str:
    date_column = metric_def.get("date_column")
    if dimension in DIMENSION_ALIASES:
        if not date_column:
            raise ValueError(f"Dimension '{dimension}' requires a date column")
        return DIMENSION_ALIASES[dimension](date_column)

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", dimension):
        raise ValueError(f"Unsafe dimension '{dimension}'")
    return dimension


def _validated_dimensions(metric_def: dict, dimensions: list[str] | None) -> list[str]:
    requested = dimensions or []
    if not requested:
        return []

    allowed = set(metric_def.get("allowed_dimensions", []))
    invalid = [dimension for dimension in requested if dimension not in allowed]
    if invalid:
        raise ValueError(
            "Unsupported dimension(s): "
            + ", ".join(invalid)
            + ". Allowed dimensions: "
            + ", ".join(sorted(allowed))
        )

    return requested


def build_metric_query(metric_def: dict, start_date=None, end_date=None, dimensions=None):
    """Return (sql, params) for one non-derived metric definition."""
    table = metric_def["table"]
    join_clause = metric_def.get("join", "") or ""
    filters = list(metric_def.get("filters", []))
    date_column = metric_def.get("date_column")
    dimensions = _validated_dimensions(metric_def, dimensions)
    params = []

    if date_column and start_date and end_date:
        filters.append(f"{date_column} BETWEEN %s AND %s")
        params.extend([start_date, end_date])

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(f"({item})" for item in filters)

    if metric_def.get("type") == "records":
        columns = metric_def.get("columns", ["*"])
        order_by = metric_def.get("order_by", "")
        limit = int(metric_def.get("limit", 50))
        order_clause = f"ORDER BY {order_by}" if order_by else ""
        sql = f"""
            SELECT {", ".join(columns)}
            FROM {table}
            {join_clause}
            {where_clause}
            {order_clause}
            LIMIT {limit}
        """
        return sql, tuple(params)

    aggregation = metric_def["aggregation"]
    if dimensions:
        select_dimensions = [
            f"{_dimension_expression(metric_def, dimension)} AS {dimension}"
            for dimension in dimensions
        ]
        group_by = ", ".join(_dimension_expression(metric_def, dimension) for dimension in dimensions)
        order_by = metric_def.get("group_order_by", "value DESC")
        sql = f"""
            SELECT {", ".join(select_dimensions)}, {aggregation} AS value
            FROM {table}
            {join_clause}
            {where_clause}
            GROUP BY {group_by}
            ORDER BY {order_by}
        """
        return sql, tuple(params)

    sql = f"""
        SELECT {aggregation} AS value
        FROM {table}
        {join_clause}
        {where_clause}
    """
    return sql, tuple(params)
