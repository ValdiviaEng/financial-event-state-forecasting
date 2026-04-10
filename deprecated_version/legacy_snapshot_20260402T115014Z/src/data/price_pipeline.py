"""Market-price ingestion and normalization pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import importlib
from pathlib import Path
from collections.abc import Sequence
from typing import Any

from src.data.data_contracts import SCHEMA_VERSION, validate_manifest, validate_records
from src.data.incremental_updates import (
    MarketUpdateWindow,
    build_market_update_plan,
    latest_dates_by_ticker,
)
from src.data.corporate_actions import apply_split_adjustments
from src.data.split_events_client import SplitEvent
from src.data.quality_checks import assert_no_blocking_issues, run_price_quality_checks
from src.data.twelve_data_client import TwelveDataClient, TwelveDataRequestMetadata
from src.utils.config_loader import ResolvedSettings
from src.utils.io_utils import read_parquet, write_json, write_manifest, write_parquet


@dataclass(frozen=True, slots=True)
class MarketIngestionResult:
    """Result summary for one ticker ingestion run."""

    ticker: str
    raw_path: Path
    interim_path: Path
    quality_report_path: Path
    rows_written: int
    latest_date: str | None
    request_metadata: TwelveDataRequestMetadata

    def as_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "raw_path": str(self.raw_path),
            "interim_path": str(self.interim_path),
            "quality_report_path": str(self.quality_report_path),
            "rows_written": self.rows_written,
            "latest_date": self.latest_date,
            "request_metadata": self.request_metadata.as_ledger_record(raw_path=str(self.raw_path)),
        }


class MarketPricePipeline:
    """Pipeline for raw Twelve Data download, normalization, and interim storage."""

    def __init__(
        self,
        *,
        settings: ResolvedSettings,
        client: TwelveDataClient,
    ) -> None:
        self.settings = settings
        self.client = client
        self.dataset_build_config = settings.get_config("dataset_build")
        self.data_sources_config = settings.data_sources_config.get("market_data", {})

    @classmethod
    def from_settings(
        cls,
        settings: ResolvedSettings,
        client: TwelveDataClient | None = None,
    ) -> "MarketPricePipeline":
        return cls(settings=settings, client=client or TwelveDataClient.from_settings(settings))

    def price_file_path(self, ticker: str) -> Path:
        return self.settings.project_paths.data_interim_dir / "prices_daily" / f"{ticker}.parquet"

    def quality_report_path(self, ticker: str) -> Path:
        return self.settings.project_paths.data_interim_dir / "prices_daily_quality" / f"{ticker}.json"

    def adjusted_price_file_path(self, ticker: str) -> Path:
        return self.settings.project_paths.data_interim_dir / "adjusted_prices_daily" / f"{ticker}.parquet"

    def adjustment_report_path(self, ticker: str) -> Path:
        return self.settings.project_paths.data_interim_dir / "adjusted_prices_daily_quality" / f"{ticker}.json"

    def raw_payload_path(self, ticker: str, start_date: str, end_date: str) -> Path:
        raw_subdir = self.dataset_build_config.get("outputs", {}).get("raw_market_subdir", "twelvedata")
        return (
            self.settings.project_paths.raw_provider_dir(raw_subdir)
            / ticker
            / f"time_series__{start_date}__{end_date}.json"
        )

    def ledger_path(self) -> Path:
        raw_subdir = self.dataset_build_config.get("outputs", {}).get("raw_market_subdir", "twelvedata")
        return self.settings.project_paths.raw_provider_dir(raw_subdir) / "market_data_request_ledger.parquet"

    def manifest_path(self, run_label: str | None = None) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        suffix = f"_{run_label}" if run_label else ""
        return self.settings.project_paths.data_manifests_dir / f"market_data_manifest{suffix}_{timestamp}.json"

    def get_latest_dates(self, tickers: list[str] | tuple[str, ...]) -> dict[str, Any]:
        price_files = {ticker: self.price_file_path(ticker) for ticker in tickers}
        return latest_dates_by_ticker(price_files)

    def plan_updates(
        self,
        tickers: list[str] | tuple[str, ...],
        *,
        start_date: str,
        end_date: str,
        max_symbols: int | None = None,
        force_refresh: bool = False,
    ) -> list[MarketUpdateWindow]:
        if force_refresh:
            return [
                MarketUpdateWindow(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    reason="forced_refresh",
                    latest_local_date=None,
                )
                for ticker in (tickers[:max_symbols] if max_symbols else tickers)
            ]

        latest_dates = self.get_latest_dates(tickers)
        return build_market_update_plan(
            list(tickers),
            latest_dates=latest_dates,
            start_date=start_date,
            end_date=end_date,
            max_symbols=max_symbols,
        )

    def ingest_update_window(self, window: MarketUpdateWindow) -> MarketIngestionResult:
        payload, metadata = self.client.get_time_series(
            symbol=window.ticker,
            interval=self.data_sources_config.get("interval", self.settings.environment.twelve_data_interval),
            outputsize=self.data_sources_config.get("outputsize", self.settings.environment.twelve_data_outputsize),
            start_date=window.start_date,
            end_date=window.end_date,
            order=self.data_sources_config.get("order", "ASC"),
            timezone=self.data_sources_config.get("timezone", "UTC"),
        )

        raw_path = self.raw_payload_path(window.ticker, window.start_date, window.end_date)
        write_json(payload, raw_path)

        parsed_rows = self.client.parse_time_series(payload, symbol=window.ticker)
        ingest_ts = metadata.requested_at_utc
        for row in parsed_rows:
            row["ingest_ts"] = ingest_ts

        merged_rows = self._merge_price_rows(window.ticker, parsed_rows)
        validate_records("prices_daily", merged_rows)

        quality_report = run_price_quality_checks(merged_rows, expected_ticker=window.ticker)
        assert_no_blocking_issues(quality_report)

        interim_path = self.price_file_path(window.ticker)
        pandas_module = importlib.import_module("pandas")
        write_parquet(pandas_module.DataFrame(merged_rows), interim_path, index=False)

        quality_path = self.quality_report_path(window.ticker)
        write_json(quality_report, quality_path)

        self._append_ledger_record(metadata, raw_path=raw_path)

        latest_date = max((row["date"] for row in merged_rows), default=None)
        latest_date_text = latest_date.isoformat() if latest_date is not None else None

        return MarketIngestionResult(
            ticker=window.ticker,
            raw_path=raw_path,
            interim_path=interim_path,
            quality_report_path=quality_path,
            rows_written=len(merged_rows),
            latest_date=latest_date_text,
            request_metadata=metadata,
        )

    def run(
        self,
        tickers: list[str] | tuple[str, ...],
        *,
        start_date: str,
        end_date: str,
        max_symbols: int | None = None,
        force_refresh: bool = False,
        dry_run: bool = False,
        run_label: str | None = None,
    ) -> dict[str, Any]:
        plan = self.plan_updates(
            list(tickers),
            start_date=start_date,
            end_date=end_date,
            max_symbols=max_symbols,
            force_refresh=force_refresh,
        )

        summary: dict[str, Any] = {
            "stage": "market_data_build",
            "schema_version": SCHEMA_VERSION,
            "start_date": start_date,
            "end_date": end_date,
            "dry_run": dry_run,
            "planned_updates": [window.as_dict() for window in plan],
            "results": [],
        }

        if dry_run:
            return summary

        results = [self.ingest_update_window(window) for window in plan]
        summary["results"] = [result.as_dict() for result in results]
        manifest_path = self.write_manifest(summary=summary, run_label=run_label)
        summary["manifest_path"] = str(manifest_path)
        return summary

    def write_manifest(self, *, summary: dict[str, Any], run_label: str | None = None) -> Path:
        manifest_payload = {
            "manifest_version": "1",
            "dataset_name": "market_data_interim",
            "dataset_version": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "source_tables": ["market_data_request_ledger", "prices_daily"],
            "summary": summary,
        }
        validate_manifest(manifest_payload)
        path = self.manifest_path(run_label=run_label)
        write_manifest(manifest_payload, path)
        return path

    def build_adjusted_prices_for_ticker(
        self,
        ticker: str,
        *,
        split_events: Sequence[SplitEvent | dict[str, Any]],
        adjustment_source: str = "split_events",
        missing_split_policy: str = "warn_return_raw",
    ) -> dict[str, Any]:
        """Build and persist a split-adjusted price history for one ticker."""

        raw_price_path = self.price_file_path(ticker)
        if not raw_price_path.exists():
            raise FileNotFoundError(f"Raw interim price file not found for ticker '{ticker}': {raw_price_path}")

        raw_table = read_parquet(raw_price_path, backend="pandas")
        raw_rows = [_normalize_loaded_row(row) for row in raw_table.to_dict(orient="records")]

        adjustment_result = apply_split_adjustments(
            raw_rows,
            split_events,
            adjustment_source=adjustment_source,
            missing_split_policy=missing_split_policy,
        )
        validate_records("adjusted_prices_daily", adjustment_result.adjusted_rows)

        pandas_module = importlib.import_module("pandas")
        adjusted_path = self.adjusted_price_file_path(ticker)
        write_parquet(pandas_module.DataFrame(adjustment_result.adjusted_rows), adjusted_path, index=False)

        report_path = self.adjustment_report_path(ticker)
        write_json(adjustment_result.diagnostics, report_path)

        return {
            "ticker": ticker,
            "raw_price_path": str(raw_price_path),
            "adjusted_price_path": str(adjusted_path),
            "adjustment_report_path": str(report_path),
            "rows_written": len(adjustment_result.adjusted_rows),
            "diagnostics": adjustment_result.diagnostics,
        }

    def _append_ledger_record(self, metadata: TwelveDataRequestMetadata, *, raw_path: Path) -> None:
        ledger_record = metadata.as_ledger_record(raw_path=str(raw_path))
        ledger_records: list[dict[str, Any]] = []
        ledger_path = self.ledger_path()
        if ledger_path.exists():
            existing = read_parquet(ledger_path, backend="pandas")
            ledger_records = existing.to_dict(orient="records")
        ledger_records.append(ledger_record)
        pandas_module = importlib.import_module("pandas")
        write_parquet(pandas_module.DataFrame(ledger_records), ledger_path, index=False)

    def _merge_price_rows(self, ticker: str, new_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        existing_rows: list[dict[str, Any]] = []
        price_path = self.price_file_path(ticker)
        if price_path.exists():
            existing = read_parquet(price_path, backend="pandas")
            existing_rows = [_normalize_loaded_row(row) for row in existing.to_dict(orient="records")]

        merged: dict[tuple[str, Any], dict[str, Any]] = {}
        combined = existing_rows + new_rows
        for row in sorted(combined, key=lambda item: (_coerce_ingest_ts(item.get("ingest_ts")), _coerce_key_date(item.get("date")))):
            normalized_row = dict(row)
            normalized_row["date"] = _coerce_key_date(normalized_row.get("date"))
            merged[(normalized_row["ticker"], normalized_row["date"])] = normalized_row
        return sorted(merged.values(), key=lambda row: row["date"])


def _coerce_ingest_ts(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _coerce_key_date(value: Any) -> Any:
    if hasattr(value, "date") and not isinstance(value, str):
        try:
            return value.date() if hasattr(value, "hour") else value
        except TypeError:
            return value
    return value


def _normalize_loaded_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    normalized["date"] = _coerce_key_date(normalized.get("date"))
    return normalized
