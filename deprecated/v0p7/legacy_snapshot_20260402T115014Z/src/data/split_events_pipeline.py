"""Split-event fetching, normalization, persistence, and manifest helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import importlib
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from src.data.data_contracts import SCHEMA_VERSION, validate_manifest, validate_records
from src.data.split_events_client import SplitEvent, SplitEventsClient
from src.utils.config_loader import ResolvedSettings
from src.utils.io_utils import read_parquet, write_json, write_manifest, write_parquet


class SplitEventsPipelineError(RuntimeError):
    """Raised when split-event fetching or persistence fails."""


@dataclass(frozen=True, slots=True)
class SplitEventsBuildResult:
    """Summary of one split-event build run."""

    split_events_path: Path
    quality_report_path: Path
    manifest_path: Path
    ledger_path: Path
    raw_paths: tuple[Path, ...]
    tickers_requested: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "split_events_path": str(self.split_events_path),
            "quality_report_path": str(self.quality_report_path),
            "manifest_path": str(self.manifest_path),
            "ledger_path": str(self.ledger_path),
            "raw_paths": [str(path) for path in self.raw_paths],
            "tickers_requested": list(self.tickers_requested),
        }


class SplitEventsPipeline:
    """Fetch split events using Twelve Data when available and yfinance as fallback."""

    def __init__(self, *, settings: ResolvedSettings) -> None:
        self.settings = settings
        provider_name = settings.data_sources_config.get("split_events", {}).get("provider", "external_or_upgrade_path")
        normalizer_provider = provider_name if provider_name != "auto" else "external_or_upgrade_path"
        self.split_client = SplitEventsClient(provider_name=normalizer_provider)
        self.market_base_url = settings.data_sources_config.get("market_data", {}).get(
            "base_url", "https://api.twelvedata.com"
        )

    @classmethod
    def from_settings(cls, settings: ResolvedSettings) -> "SplitEventsPipeline":
        return cls(settings=settings)

    def split_events_path(self) -> Path:
        return self.settings.project_paths.data_interim_dir / "split_events" / "split_events.parquet"

    def quality_report_path(self) -> Path:
        return self.settings.project_paths.data_interim_dir / "split_events" / "split_events_quality.json"

    def ledger_path(self) -> Path:
        return self.settings.project_paths.data_raw_dir / "split_events" / "split_event_request_ledger.parquet"

    def raw_event_path(self, provider_name: str, ticker: str) -> Path:
        return self.settings.project_paths.data_raw_dir / "split_events" / provider_name / f"{ticker}.json"

    def manifest_path(self, run_label: str | None = None) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        suffix = f"_{run_label}" if run_label else ""
        return self.settings.project_paths.data_manifests_dir / f"split_events_manifest{suffix}_{timestamp}.json"

    def build(
        self,
        tickers: list[str] | tuple[str, ...],
        *,
        preferred_provider: str = "auto",
        run_label: str | None = None,
    ) -> dict[str, Any]:
        raw_paths: list[Path] = []
        ledger_records: list[dict[str, Any]] = []
        normalized_events: list[dict[str, Any]] = []
        provider_summary: dict[str, str] = {}

        for ticker in tickers:
            fetch_result = self.fetch_split_events_for_ticker(ticker, preferred_provider=preferred_provider)
            provider_name = fetch_result["provider"]
            raw_path = self.raw_event_path(provider_name, ticker)
            write_json(fetch_result["raw_payload"], raw_path)
            raw_paths.append(raw_path)
            ledger_records.append(fetch_result["ledger_record"])
            normalized_events.extend([event.as_dict() | {"ingest_ts": fetch_result["requested_at_utc"]} for event in fetch_result["events"]])
            provider_summary[ticker] = provider_name

        split_events_df = self._merge_split_events(normalized_events)
        validate_records("split_events", split_events_df.to_dict(orient="records"))
        write_parquet(split_events_df, self.split_events_path(), index=False)

        quality_report = self._build_quality_report(split_events_df, provider_summary)
        write_json(quality_report, self.quality_report_path())
        self._append_ledger_records(ledger_records)

        manifest_payload = {
            "manifest_version": "1",
            "dataset_name": "split_events",
            "dataset_version": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "source_tables": ["split_events"],
            "summary": quality_report,
        }
        validate_manifest(manifest_payload)
        manifest_path = self.manifest_path(run_label=run_label)
        write_manifest(manifest_payload, manifest_path)

        result = SplitEventsBuildResult(
            split_events_path=self.split_events_path(),
            quality_report_path=self.quality_report_path(),
            manifest_path=manifest_path,
            ledger_path=self.ledger_path(),
            raw_paths=tuple(raw_paths),
            tickers_requested=tuple(tickers),
        )
        summary = result.as_dict()
        summary["provider_summary"] = provider_summary
        return summary

    def fetch_split_events_for_ticker(self, ticker: str, *, preferred_provider: str = "auto") -> dict[str, Any]:
        provider_order = self._provider_order(preferred_provider)
        last_error: Exception | None = None

        for provider_name in provider_order:
            try:
                if provider_name == "twelve_data":
                    raw_payload, events, requested_at = self._fetch_twelve_data_splits(ticker)
                elif provider_name == "yfinance":
                    raw_payload, events, requested_at = self._fetch_yfinance_splits(ticker)
                else:
                    raise SplitEventsPipelineError(f"Unsupported split provider '{provider_name}'.")

                return {
                    "ticker": ticker,
                    "provider": provider_name,
                    "events": events,
                    "raw_payload": raw_payload,
                    "requested_at_utc": requested_at,
                    "ledger_record": {
                        "request_id": f"split_events:{provider_name}:{ticker}:{requested_at.isoformat()}",
                        "provider": provider_name,
                        "endpoint": "splits",
                        "ticker": ticker,
                        "requested_at_utc": requested_at,
                        "response_status": 200,
                        "success": True,
                        "raw_path": str(self.raw_event_path(provider_name, ticker)),
                        "error_message": None,
                    },
                }
            except Exception as exc:  # noqa: BLE001 - want provider fallback behavior
                last_error = exc
                continue

        raise SplitEventsPipelineError(f"Could not fetch split events for ticker '{ticker}': {last_error}")

    def _fetch_twelve_data_splits(self, ticker: str) -> tuple[dict[str, Any], list[SplitEvent], datetime]:
        requested_at = datetime.now(UTC)
        api_key = self.settings.environment.twelve_data_api_key.get_secret_value()
        response = requests.get(
            f"{self.market_base_url}/splits",
            params={"symbol": ticker, "apikey": api_key},
            timeout=30,
        )
        payload = response.json()
        if not isinstance(payload, dict) or "splits" not in payload:
            raise SplitEventsPipelineError(
                f"Twelve Data splits unavailable for {ticker}: {payload.get('message', payload)}"
            )
        raw_records = []
        for item in payload.get("splits", []):
            ratio = item.get("ratio")
            if ratio not in (None, ""):
                # Twelve Data returns ratio in old/new style for AAPL example (0.25 for 4-for-1), so invert.
                item = dict(item)
                item["split_factor"] = 1 / float(ratio)
            raw_records.append(item)
        events = self.split_client.normalize_events(raw_records, symbol=ticker, source_name="twelve_data")
        return payload, events, requested_at

    def _fetch_yfinance_splits(self, ticker: str) -> tuple[dict[str, Any], list[SplitEvent], datetime]:
        requested_at = datetime.now(UTC)
        yfinance = importlib.import_module("yfinance")
        ticker_obj = yfinance.Ticker(ticker)
        splits = ticker_obj.splits
        raw_records: list[dict[str, Any]] = []
        if len(splits):
            for index, value in splits.items():
                split_date = index.date().isoformat() if hasattr(index, "date") else str(index)[:10]
                raw_records.append(
                    {
                        "date": split_date,
                        "split_factor": float(value),
                        "source": "yfinance",
                    }
                )
        events = self.split_client.normalize_events(raw_records, symbol=ticker, source_name="yfinance") if raw_records else []
        raw_payload = {
            "ticker": ticker,
            "provider": "yfinance",
            "split_count": len(raw_records),
            "splits": raw_records,
        }
        return raw_payload, events, requested_at

    def _merge_split_events(self, new_rows: list[dict[str, Any]]) -> pd.DataFrame:
        existing_rows: list[dict[str, Any]] = []
        path = self.split_events_path()
        if path.exists():
            existing = read_parquet(path, backend="pandas")
            existing_rows = existing.to_dict(orient="records")

        merged: dict[tuple[str, Any], dict[str, Any]] = {}
        for row in existing_rows + new_rows:
            key = (str(row["ticker"]), str(row["split_date"]))
            merged[key] = row
        return pd.DataFrame(list(merged.values())).sort_values(["ticker", "split_date"], kind="stable").reset_index(drop=True)

    def _append_ledger_records(self, new_records: list[dict[str, Any]]) -> None:
        ledger_path = self.ledger_path()
        existing_rows: list[dict[str, Any]] = []
        if ledger_path.exists():
            existing = read_parquet(ledger_path, backend="pandas")
            existing_rows = existing.to_dict(orient="records")
        frame = pd.DataFrame(existing_rows + new_records)
        write_parquet(frame, ledger_path, index=False)

    @staticmethod
    def _provider_order(preferred_provider: str) -> list[str]:
        normalized = preferred_provider.strip().lower()
        if normalized == "auto":
            return ["twelve_data", "yfinance"]
        if normalized == "twelve_data":
            return ["twelve_data"]
        if normalized == "yfinance":
            return ["yfinance"]
        raise SplitEventsPipelineError(f"Unsupported preferred_provider '{preferred_provider}'.")

    @staticmethod
    def _build_quality_report(split_events_df: pd.DataFrame, provider_summary: dict[str, str]) -> dict[str, Any]:
        if split_events_df.empty:
            return {
                "row_count": 0,
                "ticker_count": 0,
                "provider_summary": provider_summary,
                "tickers_with_splits": [],
            }
        tickers_with_splits = sorted(split_events_df["ticker"].astype(str).unique().tolist())
        return {
            "row_count": int(len(split_events_df)),
            "ticker_count": len(tickers_with_splits),
            "provider_summary": provider_summary,
            "tickers_with_splits": tickers_with_splits,
        }
