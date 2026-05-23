#!/usr/bin/env python3
"""Plan or execute Stage 8 daily Twelve Data OHLCV updates."""

from __future__ import annotations

import sys

from stage8_data_update_common import run_ohlcv_update


def main(argv: list[str] | None = None) -> int:
    return run_ohlcv_update("daily", argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
