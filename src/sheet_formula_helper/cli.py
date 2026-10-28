"""Command-line interface for Sheet Formula Helper."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .client import FormulaClient, FormulaClientError
from .config import Config, load_config, save_config
from .snippets import Snippet, SnippetStore, ensure_default_snippets


def _print_result(result) -> None:
    print(result.formula)


def cmd_generate(args: argparse.Namespace) -> int:
    config = load_config()
    client = FormulaClient(config)
    try:
        result = client.generate(args.request, sheet_type=args.sheet)
    except FormulaClientError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    _print_result(result)
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    config = load_config()
    changed = False
    if args.endpoint is not None:
        config.endpoint = args.endpoint
        changed = True
    if args.model is not None:
        config.model = args.model
        changed = True
    if args.temperature is not None:
        try:
            config.temperature = float(args.temperature)
        except ValueError:
            print("Error: temperature must be a number", file=sys.stderr)
            return 1
        changed = True
    if args.show:
        print(f"Endpoint: {config.endpoint}")
        print(f"Model: {config.model}")
        print(f"Temperature: {config.temperature}")
        print(f"Config file: {config.__class__.__name__}")
        return 0
    if changed:
        save_config(config)
        print("Configuration saved.")
    else:
        print("Nothing changed. Use --show to view current config.")
    return 0


def cmd_snippets(args: argparse.Namespace) -> int:
    store = SnippetStore()
    if args.list:
        snippets = store.list()
        if not snippets:
            ensure_default_snippets(store)
            snippets = store.list()
        for snippet in snippets:
            print(f"{snippet.name}: {snippet.formula}  ({snippet.description})")
        return 0
    if args.add:
        if not args.formula:
            print("Error: --add requires --formula", file=sys.stderr)
            return 1
        snippet = Snippet(
            name=args.add,
            formula=args.formula,
            description=args.description or "",
            request=args.request or "",
        )
        store.add(snippet)
        print(f"Saved snippet '{args.add}'.")
        return 0
    if args.get:
        snippet = store.get(args.get) or store.match(args.get)
        if snippet is None:
            print(f"Error: snippet '{args.get}' not found", file=sys.stderr)
            return 1
        print(snippet.formula)
        return 0
    if args.delete:
        if store.delete(args.delete):
            print(f"Deleted snippet '{args.delete}'.")
        else:
            print(f"Error: snippet '{args.delete}' not found", file=sys.stderr)
            return 1
        return 0
    if args.use:
        snippet = store.get(args.use) or store.match(args.use)
        if snippet is None:
            print(f"Error: snippet '{args.use}' not found", file=sys.stderr)
            return 1
        print(snippet.formula)
        return 0
    print("Error: specify one of --list / --add / --get / --delete / --use", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sheet-formula-helper",
        description=(
            "Turn plain-English requests into Excel and Google Sheets "
            "formulas using a local OpenAI-compatible endpoint (default Ollama)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate a formula from a request")
    gen.add_argument("request", help="Plain-English description of the formula")
    gen.add_argument(
        "--sheet",
        choices=["excel", "google"],
        default="excel",
        help="Target spreadsheet app (default: excel)",
    )
    gen.set_defaults(func=cmd_generate)

    cfg = sub.add_parser("config", help="View or change configuration")
    cfg.add_argument("--endpoint", help="Chat completions endpoint URL")
    cfg.add_argument("--model", help="Model name to use")
    cfg.add_argument("--temperature", help="Sampling temperature (0-2)")
    cfg.add_argument("--show", action="store_true", help="Show current config")
    cfg.set_defaults(func=cmd_config)

    snip = sub.add_parser("snippets", help="Manage saved formula snippets")
    snip.add_argument("--list", action="store_true", help="List saved snippets")
    snip.add_argument("--add", metavar="NAME", help="Name of snippet to save")
    snip.add_argument("--formula", metavar="FORMULA", help="Formula to save")
    snip.add_argument(
        "--description", metavar="TEXT", help="Description for --add"
    )
    snip.add_argument(
        "--request", metavar="TEXT", help="Original request for --add"
    )
    snip.add_argument("--get", metavar="NAME", help="Print a saved snippet's formula")
    snip.add_argument("--delete", metavar="NAME", help="Delete a saved snippet")
    snip.add_argument("--use", metavar="NAME", help="Print a saved snippet's formula")
    snip.set_defaults(func=cmd_snippets)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
