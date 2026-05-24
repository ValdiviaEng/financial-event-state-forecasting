from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import cast

import pandas as pd
from pydantic import SecretStr

from src.data.incremental_updates import build_market_update_plan, build_repair_window
from src.data.price_pipeline import MarketPricePipeline
from src.data.twelve_data_client import TwelveDataClient
from src.data.twelve_data_client import TwelveDataRequestMetadata
from src.utils.config_loader import EnvironmentSettings, ResolvedSettings
from src.utils.paths import build_project_paths


class FakeTwelveDataClient:
    def __init__(self, payloads: dict[tuple[str, str, str], dict]) -> None:
        self.payloads = payloads

    def get_time_series(
        self,
        symbol: str,
        interval: str = "1day",
        outputsize: int = 5000,
        start_date: str | None = None,
        end_date: str | None = None,
        order: str = "ASC",
        timezone: str = "UTC",
    ):
        key = (symbol, start_date or "", end_date or "")
        payload = self.payloads[key]
        metadata = TwelveDataRequestMetadata(
            endpoint="time_series",
            symbol=symbol,
            requested_at_utc=datetime.now(UTC),
            request_url=f"https://example.test/{symbol}",
            request_params={
                "interval": interval,
                "outputsize": outputsize,
                "start_date": start_date,
                "end_date": end_date,
                "order": order,
                "timezone": timezone,
            },
            response_status=200,
            response_headers={"api-credits-used": "1", "api-credits-left": "799"},
            is_empty=False,
        )
        return payload, metadata

    @staticmethod
    def parse_time_series(payload: dict, symbol: str, source_name: str = "twelve_data") -> list[dict]:
        rows = []
        for item in payload["values"]:
            rows.append(
                {
                    "date": datetime.fromisoformat(item["datetime"]).date(),
                    "ticker": symbol,
                    "open": float(item["open"]),
                    "high": float(item["high"]),
                    "low": float(item["low"]),
                    "close": float(item["close"]),
                    "volume": int(item["volume"]),
                    "source": source_name,
                }
            )
        return rows


def _build_test_settings(tmp_path: Path) -> ResolvedSettings:
    environment = EnvironmentSettings(
        twelve_data_api_key=SecretStr("test-twelve-key"),
        finnhub_api_key=SecretStr("test-finnhub-key"),
        sec_user_agent="Test User test@example.com EventStateForecasting",
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        data_raw_dir=tmp_path / "data" / "raw",
        data_interim_dir=tmp_path / "data" / "interim",
        data_final_dir=tmp_path / "data" / "final",
        data_embeddings_dir=tmp_path / "data" / "embeddings",
        data_kb_dir=tmp_path / "data" / "kb",
        data_manifests_dir=tmp_path / "data" / "manifests",
        artifacts_dir=tmp_path / "artifacts",
        checkpoints_dir=tmp_path / "artifacts" / "checkpoints",
        figures_dir=tmp_path / "artifacts" / "figures",
        tables_dir=tmp_path / "artifacts" / "tables",
        runs_dir=tmp_path / "runs",
        reports_dir=tmp_path / "reports",
        notebooks_dir=tmp_path / "notebooks",
        logs_dir=tmp_path / "runs" / "logs",
    )
    paths = build_project_paths(tmp_path)
    paths.ensure_base_directories()
    return ResolvedSettings(
        environment=environment,
        project_paths=paths,
        config_dir=tmp_path / "configs",
        env_file=None,
        configs={
            "project": {"runtime": {"create_base_directories_on_load": True}},
            "data_sources": {
                "market_data": {
                    "interval": "1day",
                    "outputsize": 5000,
                    "order": "ASC",
                    "timezone": "UTC",
                }
            },
            "dataset_build": {
                "outputs": {"raw_market_subdir": "twelvedata"},
                "dates": {"start_date": "2024-01-01", "end_date": "2024-01-02"},
                "incremental_updates": {"max_symbols_per_run": 10},
            },
        },
    )


def test_incremental_plan_and_repair_window_helpers() -> None:
    plan = build_market_update_plan(
        ["AAPL", "MSFT"],
        latest_dates={"AAPL": datetime(2024, 1, 3).date(), "MSFT": None},
        start_date="2024-01-01",
        end_date="2024-01-05",
        max_symbols=5,
    )

    assert plan[0].ticker == "AAPL"
    assert plan[0].start_date == "2024-01-04"
    assert plan[1].reason == "initial_backfill"

    repair = build_repair_window("AAPL", anchor_date="2024-01-10", window_days=2)
    assert repair.start_date == "2024-01-08"
    assert repair.end_date == "2024-01-12"


def test_market_price_pipeline_writes_raw_interim_quality_and_manifest(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    fake_client = FakeTwelveDataClient(
        {
            ("BRK.B", "2024-01-01", "2024-01-02"): {
                "values": [
                    {
                        "datetime": "2024-01-01",
                        "open": "100.0",
                        "high": "101.0",
                        "low": "99.0",
                        "close": "100.5",
                        "volume": "1000",
                    },
                    {
                        "datetime": "2024-01-02",
                        "open": "101.0",
                        "high": "102.0",
                        "low": "100.0",
                        "close": "101.5",
                        "volume": "1100",
                    },
                ]
            }
        }
    )
    pipeline = MarketPricePipeline(settings=settings, client=cast(TwelveDataClient, fake_client))

    summary = pipeline.run(
        tickers=["BRK.B"],
        start_date="2024-01-01",
        end_date="2024-01-02",
        force_refresh=True,
        dry_run=False,
        run_label="stage4test",
    )

    assert len(summary["results"]) == 1
    manifest_path = Path(summary["manifest_path"])
    raw_path = Path(summary["results"][0]["raw_path"])
    interim_path = Path(summary["results"][0]["interim_path"])
    quality_path = Path(summary["results"][0]["quality_report_path"])
    ledger_path = pipeline.ledger_path()

    assert manifest_path.exists()
    assert raw_path.exists()
    assert interim_path.exists()
    assert quality_path.exists()
    assert ledger_path.exists()

    saved_rows = pd.read_parquet(interim_path)
    assert list(saved_rows["ticker"]) == ["BRK.B", "BRK.B"]

    quality_report = json.loads(quality_path.read_text(encoding="utf-8"))
    assert quality_report["has_blocking_issues"] is False

    ledger_rows = pd.read_parquet(ledger_path)
    assert len(ledger_rows) == 1


def test_market_price_pipeline_force_refresh_rerun_does_not_duplicate_rows(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    fake_client = FakeTwelveDataClient(
        {
            ("AAPL", "2024-01-01", "2024-01-02"): {
                "values": [
                    {
                        "datetime": "2024-01-01",
                        "open": "10.0",
                        "high": "11.0",
                        "low": "9.5",
                        "close": "10.5",
                        "volume": "500",
                    },
                    {
                        "datetime": "2024-01-02",
                        "open": "10.5",
                        "high": "11.2",
                        "low": "10.3",
                        "close": "11.0",
                        "volume": "550",
                    },
                ]
            }
        }
    )
    pipeline = MarketPricePipeline(settings=settings, client=cast(TwelveDataClient, fake_client))

    pipeline.run(
        tickers=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-01-02",
        force_refresh=True,
    )
    pipeline.run(
        tickers=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-01-02",
        force_refresh=True,
    )

    price_path = pipeline.price_file_path("AAPL")
    saved_rows = pd.read_parquet(price_path)

    assert len(saved_rows) == 2
    assert saved_rows.duplicated(subset=["ticker", "date"]).sum() == 0
