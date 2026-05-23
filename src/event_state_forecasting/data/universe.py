"""Frozen top-50 universe loading and validation for Stage 2."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_UNIVERSE_PATH = PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
EXPECTED_TOP50_COUNT = 50


class UniverseError(ValueError):
    """Raised when the frozen universe violates the approved contract."""


@dataclass(frozen=True, slots=True)
class UniverseMember:
    rank: int
    ticker: str
    name: str


@dataclass(frozen=True, slots=True)
class FrozenUniverse:
    path: Path
    members: tuple[UniverseMember, ...]

    @property
    def tickers(self) -> tuple[str, ...]:
        return tuple(member.ticker for member in self.members)


def load_top50_universe(path: Path | str = DEFAULT_UNIVERSE_PATH) -> FrozenUniverse:
    universe_path = Path(path)
    if not universe_path.exists():
        raise UniverseError(f"universe file does not exist: {universe_path}")

    members: list[UniverseMember] = []
    with universe_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if "ticker" not in (reader.fieldnames or []):
            raise UniverseError("universe file must include a ticker column")
        for index, row in enumerate(reader, start=1):
            ticker = (row.get("ticker") or "").strip()
            if not ticker:
                raise UniverseError(f"missing ticker at universe row {index}")
            rank_value = row.get("rank") or row.get("Rank") or index
            try:
                rank = int(rank_value)
            except ValueError as exc:
                raise UniverseError(f"invalid rank for ticker {ticker}: {rank_value}") from exc
            members.append(UniverseMember(rank=rank, ticker=ticker, name=(row.get("name") or row.get("Name") or "").strip()))

    validate_top50_members(members)
    return FrozenUniverse(path=universe_path, members=tuple(members))


def validate_top50_members(members: list[UniverseMember]) -> None:
    if len(members) != EXPECTED_TOP50_COUNT:
        raise UniverseError(f"expected {EXPECTED_TOP50_COUNT} tickers, found {len(members)}")
    tickers = [member.ticker for member in members]
    duplicates = sorted({ticker for ticker in tickers if tickers.count(ticker) > 1})
    if duplicates:
        raise UniverseError(f"duplicate tickers in universe: {duplicates}")
    if "SPY" in tickers:
        raise UniverseError("SPY must not be part of the approved top-50 universe rows")
    if "BRK.B" not in tickers:
        raise UniverseError("dotted ticker BRK.B must be preserved in canonical universe")
