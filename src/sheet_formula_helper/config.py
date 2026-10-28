"""Configuration for Sheet Formula Helper.

Configuration lives in a JSON file under XDG_CONFIG_HOME
(default ~/.config/sheet-formula-helper/config.json). Environment
variables (SHEET_FORMULA_*) override the file, so nothing ever needs
a secret or an API key: the default endpoint is a local Ollama server.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_ENDPOINT = "http://localhost:11434/v1/chat/completions"
DEFAULT_MODEL = "llama3.2"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_SYSTEM_PROMPT = (
    "You convert plain-English requests into spreadsheet formulas. "
    "Reply with ONLY the formula, starting with '='. No markdown fences, "
    "no explanation, no extra text. Support both Excel and Google Sheets "
    "(they share most functions). If a request cannot be expressed as a "
    "single formula, reply with the closest usable formula and nothing else."
)

CONFIG_DIR = Path(
    os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
) / "sheet-formula-helper"
CONFIG_FILE = CONFIG_DIR / "config.json"
DATA_DIR = Path(
    os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")
) / "sheet-formula-helper"
SNIPPETS_FILE = DATA_DIR / "snippets.json"


@dataclass
class Config:
    endpoint: str = DEFAULT_ENDPOINT
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    system_prompt: str = DEFAULT_SYSTEM_PROMPT

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


def load_config() -> Config:
    """Load config from file, overridden by environment variables."""
    config = Config()
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as fh:
                file_data = json.load(fh)
            if isinstance(file_data, dict):
                config = Config.from_dict(file_data)
        except (json.JSONDecodeError, OSError):
            # Corrupt config is ignored rather than crashing the user.
            pass
    endpoint = os.environ.get("SHEET_FORMULA_ENDPOINT")
    if endpoint:
        config.endpoint = endpoint
    model = os.environ.get("SHEET_FORMULA_MODEL")
    if model:
        config.model = model
    temperature = os.environ.get("SHEET_FORMULA_TEMPERATURE")
    if temperature is not None:
        try:
            config.temperature = float(temperature)
        except ValueError:
            pass
    return config


def save_config(config: Config) -> None:
    """Persist config to the config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as fh:
        json.dump(config.to_dict(), fh, indent=2)
