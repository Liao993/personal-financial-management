from __future__ import annotations

import json
import os
import re
import ast
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from modules.ai_semantic.ollama_client import OllamaUnavailableError, ask_ollama
from modules.ai_semantic.query_builder import build_metric_query
from modules.ai_semantic.semantic_loader import get_metric_catalog_text, load_semantic_layer
from utils.connection import get_db_connection


METRICS = load_semantic_layer()
CATALOG_TEXT = get_metric_catalog_text(METRICS)
APP_TIMEZONE = ZoneInfo(os.environ.get("APP_TIMEZONE", "America/Halifax"))


def _today() -> date:
    return datetime.now(APP_TIMEZONE).date()

ROUTER_SYSTEM_PROMPT = f"""You are a router for a personal finance assistant.
You do not answer questions yourself. Pick exactly one metric from the catalog
and choose a date range.

Available metrics:
{CATALOG_TEXT}

Rules:
- Respond only with JSON.
- Format: {{"metric": "<metric_name>", "dimensions": ["dimension_name"] or [], "start_date": "YYYY-MM-DD" or null, "end_date": "YYYY-MM-DD" or null}}
- If no metric matches, respond: {{"metric": null, "dimensions": [], "start_date": null, "end_date": null}}
- Default to the current calendar year when the user does not specify a date range.
- Today's date is {_today().isoformat()}.
"""


DIMENSION_PHRASES = {
    "category": ("category", "categories"),
    "summary_category": ("summary category", "summary categories"),
    "payment_method": ("payment method", "payment", "card"),
    "traveling_category": ("travel category", "traveling category"),
    "trip": ("trip", "trips"),
    "house_category": ("house category", "house categories"),
    "fund_category": ("fund", "fund category", "fund categories"),
    "transaction_type": ("transaction type", "deposit vs withdrawal"),
    "account_name": ("account", "account name"),
    "transfer_to_account": ("transfer account", "transfer to account"),
    "source": ("income source", "source"),
    "regular": ("regular", "regular income"),
    "month": ("month", "monthly"),
    "year": ("year", "annual", "yearly"),
}

MONTH_NAMES = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


def _parse_router_response(raw_response: str) -> dict[str, Any]:
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_response, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _parse_iso_date(value: Any, field_name: str) -> date | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a YYYY-MM-DD string or null")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format") from exc


def _normalize_date_range(parsed: dict[str, Any]) -> tuple[str, str]:
    today = _today()
    start = _parse_iso_date(parsed.get("start_date"), "start_date")
    end = _parse_iso_date(parsed.get("end_date"), "end_date")

    if start is None:
        start = date(today.year, 1, 1)
    if end is None:
        end = today
    if start > end:
        raise ValueError("start_date cannot be after end_date")

    return start.isoformat(), end.isoformat()


def _date_range_from_question(question: str) -> dict[str, str | None]:
    normalized = question.lower()
    today = _today()

    for month_name, month_number in MONTH_NAMES.items():
        match = re.search(rf"\b{month_name}\b\s+(\d{{4}})", normalized)
        if match:
            year = int(match.group(1))
            start = date(year, month_number, 1)
            if month_number == 12:
                end = date(year, 12, 31)
            else:
                end = date(year, month_number + 1, 1).replace(day=1)
                end = date.fromordinal(end.toordinal() - 1)
            return {"start_date": start.isoformat(), "end_date": end.isoformat()}

    year_match = re.search(r"\b(20\d{2})\b", normalized)
    if year_match:
        year = int(year_match.group(1))
        return {"start_date": f"{year}-01-01", "end_date": f"{year}-12-31"}

    if "all time" in normalized or "all years" in normalized:
        return {"start_date": "1900-01-01", "end_date": today.isoformat()}

    return {"start_date": None, "end_date": None}


def _extract_dimensions(question: str, metric_def: dict, routed_dimensions: Any = None) -> list[str]:
    allowed = metric_def.get("allowed_dimensions", [])
    if not allowed:
        return []

    dimensions = []
    if isinstance(routed_dimensions, list):
        dimensions.extend(item for item in routed_dimensions if isinstance(item, str))

    normalized = re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()
    if "group by all" in normalized or "by all columns" in normalized or "all columns" in normalized:
        dimensions.extend(allowed)
    else:
        for dimension, phrases in DIMENSION_PHRASES.items():
            if dimension not in allowed:
                continue
            if any(phrase in normalized for phrase in phrases):
                dimensions.append(dimension)

    deduped = []
    for dimension in dimensions:
        if dimension in allowed and dimension not in deduped:
            deduped.append(dimension)
    return deduped


def _rule_based_route(question: str) -> dict[str, Any] | None:
    normalized = re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()
    words = normalized.split()
    has_withdrawal = any(word in words for word in ("withdraw", "withdrawal", "withdrawals", "withdrew"))
    wants_records = any(word in words for word in ("find", "list", "show", "all", "details", "records"))
    parsed_dates = _date_range_from_question(question)
    all_time_dates = {"start_date": "1900-01-01", "end_date": _today().isoformat()} if "all" in words else parsed_dates

    if "parent support" in normalized or "parents support" in normalized:
        if has_withdrawal and wants_records:
            return {"metric": "parent_support_withdrawals", "dimensions": [], **all_time_dates}
        if has_withdrawal:
            return {"metric": "parent_support_withdrawals_total", "dimensions": [], "start_date": None, "end_date": None}
        if "deposit" in normalized or "received" in normalized:
            return {"metric": "parent_support_deposits", "dimensions": [], "start_date": None, "end_date": None}
        if "balance" in normalized or "left" in normalized:
            return {"metric": "parent_support_balance", "dimensions": [], "start_date": None, "end_date": None}

    wants_grouping = "group by" in normalized or "breakdown" in normalized or " by " in f" {normalized} "
    if wants_grouping:
        if any(word in words for word in ("income", "earning", "earnings", "salary")):
            return {"metric": "total_income", "dimensions": [], **parsed_dates}
        if "deposit" in words or "deposits" in words:
            return {"metric": "total_transaction_deposits", "dimensions": [], **parsed_dates}
        if has_withdrawal:
            return {"metric": "total_transaction_withdrawals", "dimensions": [], **parsed_dates}
        if any(word in words for word in ("transaction", "transactions")):
            return {"metric": "total_transaction_amount", "dimensions": [], **parsed_dates}
        if any(word in words for word in ("spending", "spend", "expense", "expenses")):
            return {"metric": "total_expense", "dimensions": [], **parsed_dates}

    return None


def _run_simple_metric(name: str, start_date: str | None, end_date: str | None) -> float:
    sql, params = build_metric_query(METRICS[name], start_date, end_date)
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return float(row[0]) if row and row[0] is not None else 0.0
    finally:
        cursor.close()
        conn.close()


def _run_grouped_metric(name: str, start_date: str | None, end_date: str | None, dimensions: list[str]) -> list[dict[str, Any]]:
    sql, params = build_metric_query(METRICS[name], start_date, end_date, dimensions=dimensions)
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def _run_record_metric(name: str, start_date: str | None, end_date: str | None) -> list[dict[str, Any]]:
    sql, params = build_metric_query(METRICS[name], start_date, end_date)
    conn = get_db_connection()
    if not conn:
        raise RuntimeError("Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def _evaluate_formula(formula: str, values: dict[str, float]) -> float:
    operators = {
        ast.Add: lambda left, right: left + right,
        ast.Sub: lambda left, right: left - right,
        ast.Mult: lambda left, right: left * right,
        ast.Div: lambda left, right: left / right if right else 0.0,
        ast.USub: lambda item: -item,
        ast.UAdd: lambda item: item,
    }

    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name) and node.id in values:
            return float(values[node.id])
        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in operators:
            return operators[type(node.op)](eval_node(node.operand))
        raise ValueError(f"Unsupported formula expression: {ast.dump(node)}")

    parsed = ast.parse(formula, mode="eval")
    return float(eval_node(parsed))


def _format_value(value: float, unit: str) -> str:
    if unit == "percent":
        return f"{value:.2f}%"
    if unit == "count":
        return f"{value:.0f}"
    return f"${value:,.2f}"


def _format_period(start_date: str | None, end_date: str | None, date_column: str | None) -> str:
    if not date_column:
        return "currently"
    return f"from {start_date} to {end_date}"


def _format_metric_answer(metric_name: str, value: float, start_date: str, end_date: str) -> str:
    definition = METRICS[metric_name]
    label = definition.get("label", metric_name.replace("_", " "))
    unit = definition.get("unit", "currency")
    period = _format_period(start_date, end_date, definition.get("date_column"))
    return f"Your {label} {period} is {_format_value(value, unit)}."


def _format_record_answer(metric_name: str, rows: list[dict[str, Any]], start_date: str, end_date: str) -> str:
    definition = METRICS[metric_name]
    label = definition.get("label", metric_name.replace("_", " "))
    period = _format_period(start_date, end_date, definition.get("date_column"))
    if not rows:
        return f"I found 0 {label} {period}."

    total = sum(abs(float(row.get("amount") or 0)) for row in rows if "amount" in row)
    return f"I found {len(rows)} {label} {period}, totaling ${total:,.2f}."


def _format_grouped_answer(metric_name: str, rows: list[dict[str, Any]], dimensions: list[str], start_date: str, end_date: str) -> str:
    definition = METRICS[metric_name]
    label = definition.get("label", metric_name.replace("_", " "))
    period = _format_period(start_date, end_date, definition.get("date_column"))
    dimension_text = ", ".join(dimensions)
    if not rows:
        return f"I found no {label} grouped by {dimension_text} {period}."

    return f"Here is your {label} grouped by {dimension_text} {period}."


def _resolve_metric(name: str, start_date: str | None, end_date: str | None, seen=None) -> float:
    seen = seen or set()
    if name in seen:
        raise ValueError(f"Circular metric reference detected at '{name}'")
    seen.add(name)

    definition = METRICS[name]
    if definition.get("type") != "derived":
        return _run_simple_metric(name, start_date, end_date)

    formula = definition["formula"]
    referenced_names = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", formula))
    values = {
        ref: _resolve_metric(ref, start_date, end_date, seen.copy())
        for ref in referenced_names
        if ref in METRICS
    }
    return _evaluate_formula(formula, values)


def answer_question(question: str) -> dict:
    parsed = _rule_based_route(question)
    if parsed is None:
        try:
            raw_response = ask_ollama(ROUTER_SYSTEM_PROMPT, question, expect_json=True)
            parsed = _parse_router_response(raw_response)
        except OllamaUnavailableError as exc:
            return {
                "answer": (
                    f"{exc} On the host, run: brew install ollama; "
                    "brew services start ollama; ollama pull llama3.1:8b"
                ),
                "metric": None,
                "value": None,
                "rows": None,
                "mode": "error",
            }
        except Exception as exc:
            return {
                "answer": f"I couldn't route that question cleanly: {exc}",
                "metric": None,
                "value": None,
                "rows": None,
                "mode": "error",
            }

    metric_name = parsed.get("metric")
    if not metric_name or metric_name not in METRICS:
        return {
            "answer": (
                "That's not in the semantic layer yet. Available metrics: "
                + ", ".join(METRICS.keys())
            ),
            "metric": None,
            "value": None,
            "rows": None,
            "mode": "no_match",
        }

    try:
        start_date, end_date = _normalize_date_range(parsed)
    except ValueError as exc:
        return {
            "answer": f"I couldn't use the date range from the router: {exc}",
            "metric": metric_name,
            "value": None,
            "rows": None,
            "mode": "error",
        }

    dimensions = _extract_dimensions(question, METRICS[metric_name], parsed.get("dimensions"))

    try:
        if METRICS[metric_name].get("type") == "records":
            rows = _run_record_metric(metric_name, start_date, end_date)
            return {
                "answer": _format_record_answer(metric_name, rows, start_date, end_date),
                "metric": metric_name,
                "value": None,
                "rows": rows,
                "dimensions": [],
                "mode": "semantic_layer",
                "start_date": start_date,
                "end_date": end_date,
            }

        if dimensions:
            if METRICS[metric_name].get("type") == "derived":
                raise ValueError("Derived metrics do not support grouping yet")
            rows = _run_grouped_metric(metric_name, start_date, end_date, dimensions)
            return {
                "answer": _format_grouped_answer(metric_name, rows, dimensions, start_date, end_date),
                "metric": metric_name,
                "value": None,
                "rows": rows,
                "dimensions": dimensions,
                "mode": "semantic_layer",
                "start_date": start_date,
                "end_date": end_date,
            }

        value = _resolve_metric(metric_name, start_date, end_date)
    except Exception as exc:
        return {
            "answer": f"I found the metric, but couldn't calculate it: {exc}",
            "metric": metric_name,
            "value": None,
            "rows": None,
            "dimensions": dimensions,
            "mode": "error",
        }

    return {
        "answer": _format_metric_answer(metric_name, value, start_date, end_date),
        "metric": metric_name,
        "value": value,
        "rows": None,
        "dimensions": dimensions,
        "mode": "semantic_layer",
        "start_date": start_date,
        "end_date": end_date,
    }
