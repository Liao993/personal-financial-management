from __future__ import annotations

import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SEMANTIC_LAYER_PATH = PROJECT_ROOT / "dbt" / "budget_project" / "semantic_layer.yml"
REQUIRED_SIMPLE_FIELDS = ("table", "aggregation")
ENV_PATTERN = re.compile(r"\{\{\s*env\.([A-Z0-9_]+)\s*\}\}")


def _replace_env_placeholders(value: Any) -> Any:
    if isinstance(value, str):
        def replace(match: re.Match) -> str:
            name = match.group(1)
            fallback = "public" if name == "DBT_SCHEMA" else ""
            return os.getenv(name, fallback)

        return ENV_PATTERN.sub(replace, value)

    if isinstance(value, list):
        return [_replace_env_placeholders(item) for item in value]

    if isinstance(value, dict):
        return {key: _replace_env_placeholders(item) for key, item in value.items()}

    return value


def load_semantic_layer(path: str | Path | None = None) -> dict:
    layer_path = Path(path) if path else DEFAULT_SEMANTIC_LAYER_PATH
    with layer_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    metrics = deepcopy(raw.get("metrics", {}))
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError("semantic_layer.yml must define a non-empty 'metrics' mapping")

    metrics = _replace_env_placeholders(metrics)
    for name, definition in metrics.items():
        if not isinstance(definition, dict):
            raise ValueError(f"Metric '{name}' must be a mapping")

        if definition.get("type") == "derived":
            if not definition.get("formula"):
                raise ValueError(f"Derived metric '{name}' is missing 'formula'")
            continue

        for field in REQUIRED_SIMPLE_FIELDS:
            if not definition.get(field):
                raise ValueError(f"Metric '{name}' is missing required field '{field}'")

        if "filters" in definition and not isinstance(definition["filters"], list):
            raise ValueError(f"Metric '{name}' filters must be a list")

    return metrics


def get_metric_catalog_text(metrics: dict) -> str:
    lines = []
    for name, definition in metrics.items():
        description = definition.get("description", "")
        lines.append(f"- {name}: {description}")
    return "\n".join(lines)
