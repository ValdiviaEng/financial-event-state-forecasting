#!/usr/bin/env python3
"""Plan or execute Stage 8 weekly Alpha Vantage news updates."""

from __future__ import annotations

import sys

from stage8_data_update_common import run_news_update


def main(argv: list[str] | None = None) -> int:
    return run_news_update("weekly", argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
