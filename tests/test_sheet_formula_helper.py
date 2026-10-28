"""Tests for Sheet Formula Helper using mocked endpoints (no keys)."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
import requests

from sheet_formula_helper.client import FormulaClient, FormulaClientError
from sheet_formula_helper.config import Config, load_config, save_config
from sheet_formula_helper.snippets import Snippet, SnippetStore


def _fake_post(payload_side_effect=None):
    """Return a mock requests.Session.post that answers like Ollama."""

    class _Response:
        def __init__(self, data, status_code=200):
            self._data = data
            self.status_code = status_code
            self.text = json.dumps(data)

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")

        def json(self):
            return self._data

    def _post(*args, **kwargs):
        if payload_side_effect:
            payload_side_effect(kwargs.get("json"))
        return _Response(
            {"choices": [{"message": {"content": "=SUM(A:A)"}}]}
        )

    return _post


def test_generate_returns_formula():
    with patch("sheet_formula_helper.client.requests.Session.post", _fake_post()):
        client = FormulaClient(Config(endpoint="http://localhost:11434/v1/chat/completions"))
        result = client.generate("sum column A")
        assert result.formula == "=SUM(A:A)"
        assert result.model == "llama3.2"
        assert "localhost:11434" in result.endpoint


def test_generate_sends_sheet_type_in_prompt():
    captured = {}

    def capture(*args, **kwargs):
        captured["messages"] = kwargs.get("json", {}).get("messages")
        captured["model"] = kwargs.get("json", {}).get("model")
        return _fake_post()(*args, **kwargs)

    with patch("sheet_formula_helper.client.requests.Session.post", capture):
        client = FormulaClient(Config(model="mistral", endpoint="http://example.local/v1/chat/completions"))
        client.generate("total of column B", sheet_type="google")
        assert captured["model"] == "mistral"
        user_text = captured["messages"][1]["content"]
        assert "Google Sheets" in user_text or "google" in user_text.lower()


def test_generate_cleans_markdown_fences():
    class _Response:
        status_code = 200
        text = json.dumps(
            {"choices": [{"message": {"content": "```\n=SUM(A:A)\n```"}}]}
        )

        def raise_for_status(self):
            pass

        def json(self):
            return json.loads(self.text)

    with patch(
        "sheet_formula_helper.client.requests.Session.post",
        lambda *args, **kwargs: _Response(),
    ):
        client = FormulaClient(Config())
        result = client.generate("sum column A")
        assert result.formula == "=SUM(A:A)"


def test_generate_adds_equals_sign():
    class _Response:
        status_code = 200
        text = json.dumps({"choices": [{"message": {"content": "SUM(A:A)"}}]})

        def raise_for_status(self):
            pass

        def json(self):
            return json.loads(self.text)

    with patch(
        "sheet_formula_helper.client.requests.Session.post",
        lambda *args, **kwargs: _Response(),
    ):
        client = FormulaClient(Config())
        result = client.generate("sum column A")
        assert result.formula == "=SUM(A:A)"


def test_generate_endpoint_error():
    class _Response:
        status_code = 500
        text = "boom"

        def raise_for_status(self):
            raise requests.HTTPError("HTTP 500")

        def json(self):
            return {}

    with patch(
        "sheet_formula_helper.client.requests.Session.post",
        lambda *args, **kwargs: _Response(),
    ):
        client = FormulaClient(Config())
        with pytest.raises(FormulaClientError):
            client.generate("sum column A")


def test_snippets_add_list_get_delete(tmp_path):
    store = SnippetStore(tmp_path / "snippets.json")
    assert store.list() == []

    store.add(Snippet(name="sum", formula="=SUM(A:A)", description="adds up column A"))
    snippets = store.list()
    assert len(snippets) == 1
    assert snippets[0].name == "sum"

    got = store.get("sum")
    assert got is not None and got.formula == "=SUM(A:A)"

    # persistence: new store reading same file
    store2 = SnippetStore(tmp_path / "snippets.json")
    assert store2.get("sum") is not None

    assert store.delete("sum") is True
    assert store.get("sum") is None
    assert store.delete("missing") is False


def test_snippets_match_fuzzy():
    store = SnippetStore()
    store.add(Snippet(name="sum column", formula="=SUM(A:A)"))
    assert store.match("sum") is not None
    assert store.match("sum column") is not None
    assert store.match("nothing") is None


def test_ensure_defaults_seed_empty_store():
    store = SnippetStore()
    # The module-level default path may already have snippets; use a temp path.
    import tempfile
    from sheet_formula_helper import snippets as snippets_mod

    tmp_store = SnippetStore(tempfile.mktemp(suffix=".json"))
    snippets_mod.ensure_default_snippets(tmp_store)
    names = [s.name for s in tmp_store.list()]
    assert "sum column" in names
    assert "average column" in names


def test_config_save_load(tmp_path, monkeypatch):
    import sheet_formula_helper.config as config_mod

    config_mod.CONFIG_FILE = tmp_path / "config.json"
    config_mod.CONFIG_DIR = tmp_path
    cfg = Config(endpoint="http://custom.local/v1/chat/completions", model="my-model", temperature=0.7)
    save_config(cfg)
    loaded = load_config()
    assert loaded.endpoint == "http://custom.local/v1/chat/completions"
    assert loaded.model == "my-model"
    assert loaded.temperature == 0.7


def test_cli_generate(monkeypatch, capsys):
    from sheet_formula_helper import cli as cli_mod

    with patch(
        "sheet_formula_helper.client.requests.Session.post", _fake_post()
    ):
        rc = cli_mod.main(["generate", "sum column A", "--sheet", "excel"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == "=SUM(A:A)"


def test_cli_snippets(tmp_path, monkeypatch, capsys):
    from sheet_formula_helper import cli as cli_mod

    snippets_file = tmp_path / "snippets.json"
    monkeypatch.setattr(cli_mod, "SnippetStore", lambda *a, **k: SnippetStore(snippets_file))

    rc = cli_mod.main(["snippets", "--add", "total", "--formula", "=SUM(A:A)", "--description", "adds column A"])
    assert rc == 0
    rc = cli_mod.main(["snippets", "--list"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "total" in out and "=SUM(A:A)" in out
    rc = cli_mod.main(["snippets", "--get", "total"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "=SUM(A:A)"
    rc = cli_mod.main(["snippets", "--delete", "total"])
    assert rc == 0
    assert cli_mod.main(["snippets", "--get", "total"]) == 1
