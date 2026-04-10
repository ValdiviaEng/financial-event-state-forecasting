from __future__ import annotations

from pathlib import Path

import pandas as pd
from pydantic import SecretStr

from src.data.split_events_pipeline import SplitEventsPipeline
from src.utils.config_loader import EnvironmentSettings, ResolvedSettings
from src.utils.paths import build_project_paths


class FakeSplitPipeline(SplitEventsPipeline):
    def __init__(self, *, settings: ResolvedSettings, payloads: dict[str, tuple[str, list[dict]]]) -> None:
        super().__init__(settings=settings)
        self.payloads = payloads

    def fetch_split_events_for_ticker(self, ticker: str, *, preferred_provider: str = "auto") -> dict[str, object]:
        provider, events = self.payloads.get(ticker, ("yfinance", []))
        from datetime import UTC, datetime

        requested_at = datetime.now(UTC)
        return {
            "ticker": ticker,
            "provider": provider,
            "events": [self.split_client.normalize_event(event, symbol=ticker, source_name=provider) for event in events],
            "raw_payload": {"ticker": ticker, "provider": provider, "splits": events},
            "requested_at_utc": requested_at,
            "ledger_record": {
                "request_id": f"split_events:{provider}:{ticker}:{requested_at.isoformat()}",
                "provider": provider,
                "endpoint": "splits",
                "ticker": ticker,
                "requested_at_utc": requested_at,
                "response_status": 200,
                "success": True,
                "raw_path": str(self.raw_event_path(provider, ticker)),
                "error_message": None,
            },
        }


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
            "data_sources": {"market_data": {"base_url": "https://api.twelvedata.com"}, "split_events": {"provider": "auto"}},
            "dataset_build": {},
        },
    )


def test_split_events_pipeline_writes_split_table_and_manifest(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    pipeline = FakeSplitPipeline(
        settings=settings,
        payloads={
            "AAPL": (
                "yfinance",
                [{"date": "2020-08-31", "split_factor": 4.0}],
            ),
            "MSFT": ("yfinance", []),
        },
    )

    summary = pipeline.build(["AAPL", "MSFT"], run_label="test")
    split_path = Path(summary["split_events_path"])
    quality_path = Path(summary["quality_report_path"])
    manifest_path = Path(summary["manifest_path"])
    ledger_path = Path(summary["ledger_path"])

    assert split_path.exists()
    assert quality_path.exists()
    assert manifest_path.exists()
    assert ledger_path.exists()

    df = pd.read_parquet(split_path)
    assert len(df) == 1
    assert df.iloc[0]["ticker"] == "AAPL"
    assert str(df.iloc[0]["split_date"])[:10] == "2020-08-31"


def test_split_events_pipeline_provider_order_validation(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    pipeline = SplitEventsPipeline.from_settings(settings)
    assert pipeline._provider_order("auto") == ["twelve_data", "yfinance"]
    assert pipeline._provider_order("yfinance") == ["yfinance"]
