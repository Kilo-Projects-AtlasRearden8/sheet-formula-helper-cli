"""Saved formula snippets stored as a local JSON file."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .config import DATA_DIR

SNIPPETS_FILE = DATA_DIR / "snippets.json"


@dataclass
class Snippet:
    name: str
    formula: str
    description: str = ""
    request: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Snippet":
        return cls(
            name=str(data.get("name", "")),
            formula=str(data.get("formula", "")),
            description=str(data.get("description", "")),
            request=str(data.get("request", "")),
        )


class SnippetStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path is not None else SNIPPETS_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._snippets: dict[str, Snippet] = self._load()

    def _load(self) -> dict[str, Snippet]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}
        snippets: dict[str, Snippet] = {}
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    snippets[str(key)] = Snippet.from_dict(value)
        return snippets

    def _save(self) -> None:
        tmp = self.path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(
                {k: v.to_dict() for k, v in self._snippets.items()},
                fh,
                indent=2,
            )
        tmp.replace(self.path)

    def add(self, snippet: Snippet) -> None:
        self._snippets[snippet.name] = snippet
        self._save()

    def get(self, name: str) -> Snippet | None:
        return self._snippets.get(name)

    def delete(self, name: str) -> bool:
        if name in self._snippets:
            del self._snippets[name]
            self._save()
            return True
        return False

    def list(self) -> list[Snippet]:
        return sorted(self._snippets.values(), key=lambda s: s.name)

    def all(self) -> dict[str, Snippet]:
        return dict(self._snippets)

    def match(self, query: str) -> Snippet | None:
        """Return exact match, else the first snippet whose name contains query."""
        q = query.lower()
        if query in self._snippets:
            return self._snippets[query]
        for snippet in self.list():
            if q in snippet.name.lower():
                return snippet
        return None


def ensure_default_snippets(store: SnippetStore) -> None:
    """Seed a few beginner-friendly snippets if the store is empty."""
    if store.list():
        return
    defaults = [
        Snippet(
            name="sum column",
            formula="=SUM(A:A)",
            description="Adds up every number in column A.",
            request="sum everything in column A",
        ),
        Snippet(
            name="average column",
            formula="=AVERAGE(B:B)",
            description="Averages all numbers in column B.",
            request="average of column B",
        ),
        Snippet(
            name="count non-empty",
            formula="=COUNTA(C:C)",
            description="Counts non-empty cells in column C.",
            request="count non-empty cells in column C",
        ),
        Snippet(
            name="lookup value",
            formula="=VLOOKUP(E2,A:B,2,FALSE)",
            description="Looks up E2 in column A and returns column B.",
            request="look up E2 in column A and return the matching value from column B",
        ),
        Snippet(
            name="if blank",
            formula="=IF(D2=\"\",\"blank\",\"filled\")",
            description="Says whether cell D2 is blank or filled.",
            request="check if D2 is blank",
        ),
    ]
    for snippet in defaults:
        store.add(snippet)
