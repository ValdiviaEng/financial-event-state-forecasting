#!/usr/bin/env python3
"""Validate that the operational event ledger is newline-delimited JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = PROJECT_ROOT / "docs" / "agent" / "agent_log" / "Event_Ledger.ndjson"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the event ledger JSONL file.")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    ledger = args.ledger if args.ledger.is_absolute() else PROJECT_ROOT / args.ledger
    line_count = validate_ledger(ledger)
    print(f"EVENT_LEDGER_JSONL_VALID lines={line_count}")
    return 0


def validate_ledger(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(f"missing event ledger: {path}")
    line_count = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"blank line in event ledger at line {line_number}")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"event ledger line {line_number} is not a JSON object")
        if not value.get("event_id"):
            raise ValueError(f"event ledger line {line_number} is missing event_id")
        line_count += 1
    return line_count


if __name__ == "__main__":
    raise SystemExit(main())
