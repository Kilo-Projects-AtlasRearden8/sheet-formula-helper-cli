# Sheet Formula Helper

Turn plain-English requests into Excel and Google Sheets formulas — no coding,
no API keys, nothing leaves your computer unless you want it to.

Built by **Asdale Dynamics, LLC** — beginner-friendly AI tools, guides, and
templates for anyone learning AI "like a friend would": plain English, step by
step, never condescending.

## What it does

You describe what you want in plain English, and the CLI writes the formula for
you:

```
sheet-formula-helper "add up everything in column A"
=SUM(A:A)
```

It works for both Excel and Google Sheets, remembers formulas you save as
snippets, and talks to a local AI server (Ollama by default) so nothing needs
to leave your machine.

## Who this is for

This tool is for beginners, small-business owners, authors, nurses, and anyone
who wants spreadsheet formulas without memorizing function names. It's part of
Asdale Dynamics, LLC's mission to make AI approachable and practical — whether
you're tracking a budget, organizing paperwork, or building a KDP publishing
workflow.

## Install

You'll need Python 3.9 or newer.

```bash
# 1. Grab the project
git clone <this-repo>
cd sheet-formula-helper-cli

# 2. Create a virtual environment (keeps things tidy and local)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install the tool
pip install -e .
```

That's it. The `sheet-formula-helper` command is now available.

## Commands

### Generate a formula

Describe what you need, in plain English:

```bash
sheet-formula-helper "add up everything in column A"
# -> =SUM(A:A)

sheet-formula-helper "average of column B"
# -> =AVERAGE(B:B)

sheet-formula-helper "look up the value in E2 and return the match from column C"
# -> =VLOOKUP(E2,A:C,3,FALSE)
```

By default it targets Excel. For Google Sheets, add `--sheet google`:

```bash
sheet-formula-helper "average of column B" --sheet google
```

### Save and reuse snippets

Formulas you use often can be saved as snippets:

```bash
# See what's saved (the first time, a few beginner snippets appear automatically)
sheet-formula-helper snippets --list

# Save a new one
sheet-formula-helper snippets --add "monthly total" \
    --formula "=SUM(D:D)" \
    --description "adds up every number in column D"

# Print a saved formula
sheet-formula-helper snippets --get "monthly total"

# Remove one you no longer need
sheet-formula-helper snippets --delete "monthly total"
```

Snippets live in `~/.local/share/sheet-formula-helper/snippets.json` — a plain
file on your machine that you can back up, edit, or move anytime.

### Configure the endpoint

By default the tool talks to Ollama at
`http://localhost:11434/v1/chat/completions` using the `llama3.2` model.

See your current settings:

```bash
sheet-formula-helper config --show
```

Change them:

```bash
sheet-formula-helper config --endpoint http://localhost:11434/v1/chat/completions \
    --model llama3.2 --temperature 0.2
```

Settings are saved to `~/.config/sheet-formula-helper/config.json`. You can also
override them with environment variables — no file edits needed:

- `SHEET_FORMULA_ENDPOINT`
- `SHEET_FORMULA_MODEL`
- `SHEET_FORMULA_TEMPERATURE`

## Local-first by design

- Default endpoint is your own Ollama instance; nothing is sent to any cloud
  service unless you configure it to do so.
- No API keys are ever requested, stored, or transmitted.
- Formulas and snippets are stored only in files on your machine.

## Running the tests

Tests use a mocked endpoint — no keys, no network, no secrets:

```bash
source .venv/bin/activate
pip install pytest
pytest
```

## About

Asdale Dynamics, LLC (Indiana, formed October 2026) publishes beginner-friendly
AI education, open-source prompt tools, local-LLM utilities, and small-business
and author tools. Learn more at dylanasdale.github.io and in *The Massive AI
Manual*.

This project is MIT licensed. See LICENSE for details.
