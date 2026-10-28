"""OpenAI-compatible chat client for formula generation.

Talks to any endpoint shaped like Ollama's /v1/chat/completions.
No API keys are ever used or required.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import requests

from .config import Config, DEFAULT_ENDPOINT, DEFAULT_MODEL, DEFAULT_TEMPERATURE


class FormulaClientError(RuntimeError):
    """Raised when the formula endpoint cannot produce a formula."""


@dataclass
class FormulaResult:
    formula: str
    model: str
    endpoint: str


class FormulaClient:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def generate(self, request: str, sheet_type: str = "excel") -> FormulaResult:
        """Turn a plain-English request into a spreadsheet formula."""
        system_prompt = self.config.system_prompt
        if sheet_type.lower() in {"google", "googlesheets", "sheets"}:
            user_prompt = (
                f"Google Sheets formula for: {request}\n"
                "Reply with ONLY the formula starting with '='."
            )
        else:
            user_prompt = (
                f"Excel formula for: {request}\n"
                "Reply with ONLY the formula starting with '='."
            )

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.config.temperature,
            "stream": False,
        }

        try:
            response = self.session.post(
                self.config.endpoint, json=payload, timeout=60
            )
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network
            raise FormulaClientError(
                f"Could not reach formula endpoint {self.config.endpoint}: {exc}"
            ) from exc

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise FormulaClientError(
                f"Endpoint returned invalid JSON: {response.text[:200]}"
            ) from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise FormulaClientError(
                f"Endpoint response missing expected content: {data!r}"
            ) from exc

        formula = self._clean_formula(content)
        return FormulaResult(
            formula=formula, model=self.config.model, endpoint=self.config.endpoint
        )

    @staticmethod
    def _clean_formula(content: str) -> str:
        formula = content.strip()
        # Strip accidental markdown fences some models add.
        if formula.startswith("```"):
            lines = formula.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            formula = "\n".join(lines).strip()
        if not formula.startswith("="):
            formula = "=" + formula
        return formula.replace("\n", " ").strip()
