# Sheet Formula Helper

Plain-English requests turned into Excel and Google Sheets formulas, powered by
a local OpenAI-compatible endpoint (Ollama by default). No API keys, no
accounts, nothing leaves your machine unless you point it elsewhere.

Built by **Asdale Dynamics, LLC** — beginner-friendly AI tools, guides, and
templates for small businesses, authors, and anyone learning AI "like a friend
would": plain English, step by step, never condescending.

## What it does

Type a request in plain English and get a spreadsheet formula back:

```
sheet-formula-helper "add up everything in column A"
=SUM(A:A)
```

It works for Excel and Google Sheets, remembers formulas you save as snippets,
and talks to any OpenAI-compatible chat endpoint. Out of the box it points at
Ollama on `http://localhost:11434/v1/chat/completions`, so it runs fully
local-first with no keys and no signup.

## Install

```bash
git clone <this-repo>
cd sheet-formula-helper-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Or just run the module directly:

```bash
source .venv/bin/activate
python -m sheet_formula_helper generate "average of column B"
```

## Commands

### Generate a formula

```
sheet-formula-helper "total sales in column D"          # Excel (default)
sheet-formula-helper "total sales in column D" --sheet google
```

### Save and reuse snippets

```
sheet-formula-helper snippets --list
sheet-formula-helper snippets --add "monthly total" --formula "=SUM(D:D)" \
    --description "adds up every number in column D"
sheet-formula-helper snippets --get "monthly total"
sheet-formula-helper snippets --delete "monthly total"
```

Snippets live in `~/.local/share/sheet-formula-helper/snippets.json` and are
yours to keep, edit, or move.

### Configure the endpoint

```
sheet-formula-helper config --show
sheet-formula-helper config --endpoint http://localhost:11434/v1/chat/completions \
    --model llama3.2 --temperature 0.2
```

Configuration lives in
`~/.config/sheet-formula-helper/config.json`. Environment variables override
the file: `SHEET_FORMULA_ENDPOINT`, `SHEET_FORMULA_MODEL`,
`SHEET_FORMULA_TEMPERATURE`.

## Local-first by design

- Default endpoint is your own Ollama instance; nothing is sent to any cloud
  service unless you configure it.
- No API keys are ever requested, stored, or transmitted.
- Formulas and snippets are stored only in files on your machine.

## Running the tests

```bash
source .venv/bin/activate
pip install pytest
pytest
```

Tests use a mocked endpoint — no keys, no network, no secrets.

## About

Asdale Dynamics, LLC (Indiana, formed October 2026) publishes beginner-friendly
AI education, open-source prompt tools, local-LLM utilities, and small-business
and author tools. Learn more at dylanasdale.github.io and in *The Massive AI
Manual*.

This project is MIT licensed. See LICENSE for details.
