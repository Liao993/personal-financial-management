import os
from pathlib import Path
from urllib.parse import urlparse

import requests


DEFAULT_OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")


class OllamaUnavailableError(RuntimeError):
    """Raised when the local Ollama server cannot be reached."""


def _running_in_container() -> bool:
    return Path("/.dockerenv").exists() or os.environ.get("APP_ENV") in {
        "development",
        "production",
    }


def get_ollama_host() -> str:
    configured_host = os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).strip()
    parsed_host = urlparse(configured_host)

    if _running_in_container() and parsed_host.hostname in {"localhost", "127.0.0.1"}:
        port = f":{parsed_host.port}" if parsed_host.port else ""
        return f"{parsed_host.scheme or 'http'}://host.docker.internal{port}"

    return configured_host.rstrip("/")


def ask_ollama(system_prompt: str, user_prompt: str, expect_json: bool = False) -> str:
    ollama_host = get_ollama_host()
    parsed_host = urlparse(ollama_host)
    if parsed_host.scheme not in {"http", "https"} or not parsed_host.netloc:
        raise OllamaUnavailableError(
            "OLLAMA_HOST must be a full HTTP URL, for example "
            "http://host.docker.internal:11434."
        )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    if expect_json:
        payload["format"] = "json"

    try:
        response = requests.post(f"{ollama_host}/api/chat", json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise OllamaUnavailableError(
            "Ollama is not reachable. Start Ollama on your Mac host and make sure "
            f"{ollama_host} responds before using AI Semantic Chat."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise OllamaUnavailableError(
            "Ollama did not respond before the request timed out. If the model is "
            "loading for the first time, wait a moment and try again."
        ) from exc

    try:
        return response.json()["message"]["content"]
    except (KeyError, TypeError, ValueError) as exc:
        raise OllamaUnavailableError("Ollama returned an unexpected response shape.") from exc
