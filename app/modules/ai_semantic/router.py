from __future__ import annotations

import ast
import json
import os
import re
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
- Format: {{"metric": "<metric_name>", "start_date": "YYYY-MM-DD" or null, "end_date": "YYYY-MM-DD" or null}}
- If no metric matches, respond: {{"metric": null, "start_date": null, "end_date": null}}
- Default to the current calendar year when the user does not specify a date range.
- Today's date is {_today().isoformat()}.
"""


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
            "mode": "error",
        }
    except Exception as exc:
        return {
            "answer": f"I couldn't route that question cleanly: {exc}",
            "metric": None,
            "value": None,
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
            "mode": "no_match",
        }

    try:
        start_date, end_date = _normalize_date_range(parsed)
    except ValueError as exc:
        return {
            "answer": f"I couldn't use the date range from the router: {exc}",
            "metric": metric_name,
            "value": None,
            "mode": "error",
        }

    try:
        value = _resolve_metric(metric_name, start_date, end_date)
    except Exception as exc:
        return {
            "answer": f"I found the metric, but couldn't calculate it: {exc}",
            "metric": metric_name,
            "value": None,
            "mode": "error",
        }

    phrasing_prompt = (
        f'The user asked: "{question}"\n'
        f'The metric "{metric_name}" ({METRICS[metric_name].get("description", "")}) '
        f"for {start_date} to {end_date} is {value:.2f}.\n"
        "Write one short natural sentence answering the user. Use a dollar sign "
        "for currency amounts and a percent sign for rates. Do not add caveats, "
        "assumptions, advice, or commentary that is not directly supported by this metric."
    )
    try:
        answer = ask_ollama(
            "You turn metric results into short personal-finance answers. One sentence only.",
            phrasing_prompt,
        ).strip()
    except Exception:
        answer = f"{metric_name} from {start_date} to {end_date} is {value:.2f}."

    return {
        "answer": answer,
        "metric": metric_name,
        "value": value,
        "mode": "semantic_layer",
        "start_date": start_date,
        "end_date": end_date,
    }
