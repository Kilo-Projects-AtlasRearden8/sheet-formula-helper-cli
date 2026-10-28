# STATUS

## What was built

`sheet-formula-helper` — a local-first Python CLI that turns plain-English
requests into Excel and Google Sheets formulas through a configurable
OpenAI-compatible chat endpoint (Ollama by default), with saved formula
snippets.

### Components

- `src/sheet_formula_helper/cli.py` — argparse CLI with `generate`, `config`,
  and `snippets` subcommands.
- `src/sheet_formula_helper/client.py` — `FormulaClient` POSTs to any
  OpenAI-compatible `/v1/chat/completions` endpoint, cleans model output
  (markdown fences, missing `=`) and returns the formula.
- `src/sheet_formula_helper/config.py` — config in
  `~/.config/sheet-formula-helper/config.json`, overridden by
  `SHEET_FORMULA_ENDPOINT` / `SHEET_FORMULA_MODEL` / `SHEET_FORMULA_TEMPERATURE`.
  Defaults: `http://localhost:11434/v1/chat/completions`, model `llama3.2`.
- `src/sheet_formula_helper/snippets.py` — `SnippetStore` persists snippets to
  `~/.local/share/sheet-formula-helper/snippets.json` (atomic writes); default
  beginner snippets seed an empty store.
- `tests/test_sheet_formula_helper.py` — 11 tests, all mocked endpoints; no
  keys, no network.
- `pyproject.toml` — installable package with `sheet-formula-helper` entry
  point; only runtime dependency is `requests`.

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Generate a formula:

```bash
sheet-formula-helper "add up everything in column A"
# -> =SUM(A:A)

sheet-formula-helper "average of column B" --sheet google
```

Manage snippets:

```bash
sheet-formula-helper snippets --list
sheet-formula-helper snippets --add "monthly total" --formula "=SUM(D:D)" \
    --description "adds up every number in column D"
sheet-formula-helper snippets --get "monthly total"
```

Configure:

```bash
sheet-formula-helper config --show
sheet-formula-helper config --endpoint http://localhost:11434/v1/chat/completions \
    --model llama3.2
```

## Verification results

- `pip install -e .` succeeds in a fresh venv (Python 3.13.5).
- `pytest` → 11 passed. All endpoint interactions are mocked; no API keys and
  no network calls anywhere in tests or code.
- `sheet-formula-helper --help` and `config --show` run correctly end to end.

## Known gaps

- Requires a running Ollama (or compatible) server to generate formulas live;
  the CLI gives a clear error if the endpoint is unreachable. Ollama itself is
  not installed by this project.
- Prompt is fixed in config; no per-request system-prompt override flag yet.
- Snippet store uses a plain JSON file (no locking); single-user local use
  assumed.
- No `.github/workflows` files by design; no CI configured.

## Credits and license

Built by Asdale Dynamics, LLC (Indiana, formed October 2026). Beginner-friendly
AI education, open-source prompt tools, local-LLM utilities, and small-business
and author tools. More at dylanasdale.github.io and in *The Massive AI Manual*.

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
