"""Universe loading, validation, S&P 500 snapshot build, and pilot-subset helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import UTC, datetime
from io import StringIO
import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests


class UniverseBuilderError(ValueError):
    """Raised when a universe snapshot is malformed or inconsistent."""


COMMON_TICKER_COLUMNS = ("ticker", "symbol", "Ticker", "Symbol")
SP500_WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
DEFAULT_UNIVERSE_SOURCE_NAME = "wikipedia_sp500_components"
DEFAULT_PILOT_TICKERS = (
    "AAPL",
    "AMZN",
    "BF.B",
    "BRK.B",
    "GOOGL",
    "JPM",
    "MSFT",
    "NVDA",
    "UNH",
    "XOM",
)


@dataclass(frozen=True, slots=True)
class UniverseBuildResult:
    """Paths and metadata produced by a universe snapshot build."""

    snapshot: UniverseSnapshot
    raw_html_path: Path
    dated_snapshot_path: Path
    latest_snapshot_path: Path
    dated_manifest_path: Path
    pilot_snapshot_path: Path | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "row_count": self.snapshot.row_count,
            "raw_html_path": str(self.raw_html_path),
            "dated_snapshot_path": str(self.dated_snapshot_path),
            "latest_snapshot_path": str(self.latest_snapshot_path),
            "dated_manifest_path": str(self.dated_manifest_path),
            "pilot_snapshot_path": str(self.pilot_snapshot_path) if self.pilot_snapshot_path else None,
            "metadata": self.snapshot.as_metadata(),
        }


@dataclass(frozen=True, slots=True)
class UniverseSnapshot:
    """In-memory representation of a frozen universe snapshot."""

    records: tuple[dict[str, Any], ...]
    source_path: str | Path
    ticker_column: str
    source_name: str | None = None
    snapshot_date: str | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def tickers(self) -> tuple[str, ...]:
        return tuple(record[self.ticker_column] for record in self.records)

    @property
    def row_count(self) -> int:
        return len(self.records)

    def as_metadata(self) -> dict[str, Any]:
        """Return a serializable summary of the universe snapshot."""

        return {
            "source_path": str(self.source_path),
            "ticker_column": self.ticker_column,
            "source_name": self.source_name,
            "snapshot_date": self.snapshot_date,
            "row_count": self.row_count,
            "warnings": list(self.warnings),
        }


def normalize_ticker(ticker: str) -> str:
    """Normalize ticker formatting without breaking dot tickers."""

    normalized = ticker.strip().upper()
    if not normalized:
        raise UniverseBuilderError("Ticker values must be non-empty after normalization.")
    return normalized


def infer_ticker_column(field_names: list[str] | tuple[str, ...]) -> str:
    """Infer the ticker column from common field-name conventions."""

    for candidate in COMMON_TICKER_COLUMNS:
        if candidate in field_names:
            return candidate
    available = ", ".join(field_names)
    raise UniverseBuilderError(
        "Could not infer ticker column from snapshot. Expected one of "
        f"{', '.join(COMMON_TICKER_COLUMNS)}. Available columns: {available}"
    )


def load_universe_snapshot(
    file_path: str | Path,
    *,
    ticker_column: str | None = None,
    source_name: str | None = None,
    snapshot_date: str | None = None,
    treat_as_latest_snapshot: bool = True,
) -> UniverseSnapshot:
    """Load and validate a frozen universe CSV snapshot."""

    path = Path(file_path)
    if not path.exists():
        raise UniverseBuilderError(f"Universe snapshot file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise UniverseBuilderError(f"Universe snapshot file has no header row: {path}")

        resolved_ticker_column = ticker_column or infer_ticker_column(tuple(reader.fieldnames))
        records = [normalize_universe_record(row, resolved_ticker_column) for row in reader]

    if not records:
        raise UniverseBuilderError(f"Universe snapshot file is empty: {path}")

    validate_unique_tickers(records, ticker_column=resolved_ticker_column)

    warnings: list[str] = []
    if treat_as_latest_snapshot:
        warnings.append(
            "Potential survivorship bias: latest snapshot may be used historically unless historical "
            "constituents are introduced."
        )

    return UniverseSnapshot(
        records=tuple(records),
        source_path=path.resolve(),
        ticker_column=resolved_ticker_column,
        source_name=source_name,
        snapshot_date=snapshot_date,
        warnings=tuple(warnings),
    )


def normalize_universe_record(record: dict[str, Any], ticker_column: str) -> dict[str, Any]:
    """Normalize one universe record while preserving all original columns."""

    if ticker_column not in record:
        raise UniverseBuilderError(
            f"Universe record is missing expected ticker column '{ticker_column}'."
        )

    normalized = {str(key): _normalize_optional_string(value) for key, value in record.items()}
    normalized[ticker_column] = normalize_ticker(str(record[ticker_column]))
    return normalized


def validate_unique_tickers(records: list[dict[str, Any]], *, ticker_column: str) -> None:
    """Validate that normalized tickers are unique within a universe snapshot."""

    seen: set[str] = set()
    duplicates: list[str] = []
    for record in records:
        ticker = record[ticker_column]
        if ticker in seen and ticker not in duplicates:
            duplicates.append(ticker)
        seen.add(ticker)

    if duplicates:
        raise UniverseBuilderError(
            "Universe snapshot contains duplicate tickers after normalization: "
            + ", ".join(sorted(duplicates))
        )


def build_pilot_subset(snapshot: UniverseSnapshot, tickers: list[str] | tuple[str, ...]) -> UniverseSnapshot:
    """Create a deterministic pilot subset from a larger universe snapshot."""

    requested = {normalize_ticker(ticker) for ticker in tickers}
    selected = [record for record in snapshot.records if record[snapshot.ticker_column] in requested]
    found = {record[snapshot.ticker_column] for record in selected}
    missing = sorted(requested.difference(found))
    if missing:
        raise UniverseBuilderError(
            "Pilot subset requested tickers that do not exist in the snapshot: " + ", ".join(missing)
        )

    ordered_records = sorted(selected, key=lambda record: tickers.index(record[snapshot.ticker_column]))
    warnings = list(snapshot.warnings)
    warnings.append(f"Pilot subset contains {len(ordered_records)} explicitly selected tickers.")

    return UniverseSnapshot(
        records=tuple(ordered_records),
        source_path=snapshot.source_path,
        ticker_column=snapshot.ticker_column,
        source_name=snapshot.source_name,
        snapshot_date=snapshot.snapshot_date,
        warnings=tuple(warnings),
    )


def write_universe_snapshot(snapshot: UniverseSnapshot, file_path: str | Path) -> Path:
    """Write a universe snapshot to CSV while preserving column order as much as possible."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    first_record = snapshot.records[0]
    field_names = list(first_record.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=field_names)
        writer.writeheader()
        for record in snapshot.records:
            writer.writerow(record)

    return path


def fetch_sp500_source_html(
    *,
    source_url: str = SP500_WIKIPEDIA_URL,
    timeout_seconds: int = 30,
    session: requests.Session | None = None,
) -> str:
    """Fetch the current S&P 500 source page HTML.

    Current implementation uses the publicly available Wikipedia constituents table.
    Uncertain, verify manually: if the page structure changes, parsing may need updating.
    """

    requester = session or requests.Session()
    response = requester.get(
        source_url,
        timeout=timeout_seconds,
        headers={
            "User-Agent": "Mozilla/5.0 EventStateForecastingResearch/0.1 (+local build script)",
        },
    )
    response.raise_for_status()
    return response.text


def parse_sp500_wikipedia_snapshot(
    html: str,
    *,
    source_name: str = DEFAULT_UNIVERSE_SOURCE_NAME,
    snapshot_date: str | None = None,
    source_url: str = SP500_WIKIPEDIA_URL,
) -> UniverseSnapshot:
    """Parse the S&P 500 constituents table from HTML into a canonical snapshot."""

    tables = pd.read_html(StringIO(html))
    target_frame: pd.DataFrame | None = None
    for table in tables:
        columns = {str(column) for column in table.columns}
        if {"Symbol", "Security", "GICS Sector"}.issubset(columns):
            target_frame = table
            break

    if target_frame is None:
        raise UniverseBuilderError(
            "Could not locate the S&P 500 constituents table in the source HTML."
        )

    renamed = target_frame.rename(
        columns={
            "Symbol": "ticker",
            "Security": "security",
            "GICS Sector": "gics_sector",
            "GICS Sub-Industry": "gics_sub_industry",
            "Headquarters Location": "headquarters_location",
            "Date added": "date_added",
            "CIK": "cik",
            "Founded": "founded",
        }
    )
    renamed["ticker"] = renamed["ticker"].astype(str).map(normalize_ticker)
    renamed["source_name"] = source_name
    renamed["source_url"] = source_url
    renamed["snapshot_date"] = snapshot_date or datetime.now(UTC).date().isoformat()
    records = [normalize_universe_record(record, "ticker") for record in renamed.to_dict(orient="records")]
    validate_unique_tickers(records, ticker_column="ticker")
    warnings = (
        "Potential survivorship bias: current S&P 500 snapshot may not represent historical constituents.",
    )
    return UniverseSnapshot(
        records=tuple(records),
        source_path=source_url,
        ticker_column="ticker",
        source_name=source_name,
        snapshot_date=snapshot_date or datetime.now(UTC).date().isoformat(),
        warnings=warnings,
    )


def build_and_save_sp500_universe_snapshot(
    output_dir: str | Path,
    *,
    source_url: str = SP500_WIKIPEDIA_URL,
    source_name: str = DEFAULT_UNIVERSE_SOURCE_NAME,
    snapshot_date: str | None = None,
    timeout_seconds: int = 30,
    include_pilot_subset: bool = True,
    pilot_tickers: tuple[str, ...] = DEFAULT_PILOT_TICKERS,
    session: requests.Session | None = None,
) -> UniverseBuildResult:
    """Fetch, parse, and save a frozen S&P 500 universe snapshot plus `latest` alias."""

    normalized_date = snapshot_date or datetime.now(UTC).date().isoformat()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    html = fetch_sp500_source_html(source_url=source_url, timeout_seconds=timeout_seconds, session=session)
    raw_html_path = output_path / f"sp500_snapshot_{normalized_date}.html"
    raw_html_path.write_text(html, encoding="utf-8")

    snapshot = parse_sp500_wikipedia_snapshot(
        html,
        source_name=source_name,
        snapshot_date=normalized_date,
        source_url=source_url,
    )
    dated_snapshot_path = write_universe_snapshot(snapshot, output_path / f"sp500_snapshot_{normalized_date}.csv")
    latest_snapshot_path = write_universe_snapshot(snapshot, output_path / "latest_universe_snapshot.csv")

    manifest_payload = {
        "snapshot_date": normalized_date,
        "source_name": source_name,
        "source_url": source_url,
        "row_count": snapshot.row_count,
        "ticker_column": snapshot.ticker_column,
        "warnings": list(snapshot.warnings),
    }
    dated_manifest_path = output_path / f"sp500_snapshot_{normalized_date}.json"
    dated_manifest_path.write_text(
        json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    pilot_snapshot_path: Path | None = None
    if include_pilot_subset:
        pilot_snapshot = build_pilot_subset(snapshot, list(pilot_tickers))
        pilot_snapshot_path = write_universe_snapshot(pilot_snapshot, output_path / "pilot10.csv")

    return UniverseBuildResult(
        snapshot=snapshot,
        raw_html_path=raw_html_path,
        dated_snapshot_path=dated_snapshot_path,
        latest_snapshot_path=latest_snapshot_path,
        dated_manifest_path=dated_manifest_path,
        pilot_snapshot_path=pilot_snapshot_path,
    )


def enrich_universe_snapshot(
    snapshot: UniverseSnapshot,
    enrichment_rows: list[dict[str, Any]],
    *,
    join_key: str = "ticker",
    fields_to_copy: list[str] | tuple[str, ...] | None = None,
) -> UniverseSnapshot:
    """Return a universe snapshot enriched with optional metadata rows.

    This helper is intentionally generic so Stage 7 can attach fields such as
    `cik`, `exchange`, or `sector` without hard-coding one provider-specific
    schema into the universe module.
    """

    if not enrichment_rows:
        return snapshot

    selected_fields = tuple(fields_to_copy or ())
    enrichment_index: dict[str, dict[str, Any]] = {}
    for row in enrichment_rows:
        if join_key not in row or row[join_key] in (None, ""):
            continue
        enrichment_index[normalize_ticker(str(row[join_key]))] = dict(row)

    enriched_records: list[dict[str, Any]] = []
    for record in snapshot.records:
        enriched = dict(record)
        lookup_key = normalize_ticker(str(record[snapshot.ticker_column]))
        enrichment = enrichment_index.get(lookup_key)
        if enrichment is not None:
            if selected_fields:
                for field in selected_fields:
                    if field in enrichment:
                        enriched[field] = enrichment[field]
            else:
                for key, value in enrichment.items():
                    if key == join_key:
                        continue
                    enriched[key] = value
        enriched_records.append(enriched)

    warnings = list(snapshot.warnings)
    warnings.append(
        f"Universe snapshot enriched using join_key='{join_key}' with {len(enrichment_index)} external records."
    )
    return UniverseSnapshot(
        records=tuple(enriched_records),
        source_path=snapshot.source_path,
        ticker_column=snapshot.ticker_column,
        source_name=snapshot.source_name,
        snapshot_date=snapshot.snapshot_date,
        warnings=tuple(warnings),
    )


def _normalize_optional_string(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped != "" else None
    return value
