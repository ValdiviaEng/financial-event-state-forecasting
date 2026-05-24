from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import cast

import pandas as pd
from pydantic import SecretStr

from src.data.company_kb_pipeline import CompanyKbPipeline
from src.data.sec_edgar_client import SecEdgarClient, SecRequestMetadata
from src.data.universe_builder import UniverseSnapshot, enrich_universe_snapshot
from src.utils.config_loader import EnvironmentSettings, ResolvedSettings
from src.utils.paths import build_project_paths


class FakeSecClient:
    def __init__(self, payloads: dict[str, dict]) -> None:
        self.payloads = payloads

    @staticmethod
    def normalize_cik(cik: str | int) -> str:
        return str(cik).zfill(10)

    def get_submissions(self, cik: str | int):
        normalized = self.normalize_cik(cik)
        payload = self.payloads[normalized]
        metadata = SecRequestMetadata(
            endpoint=f"submissions/CIK{normalized}.json",
            cik=normalized,
            requested_at_utc=datetime.now(UTC),
            request_url=f"https://example.test/{normalized}",
            response_status=200,
            response_headers={},
        )
        return payload, metadata

    @staticmethod
    def extract_company_metadata(payload: dict, source_name: str = "sec_edgar") -> dict:
        return SecEdgarClient(user_agent="Name email@example.com Project").extract_company_metadata(
            payload, source_name=source_name
        )

    @staticmethod
    def extract_ticker_cik_mappings(payload: dict, source_name: str = "sec_edgar") -> list[dict]:
        return SecEdgarClient(user_agent="Name email@example.com Project").extract_ticker_cik_mappings(
            payload, source_name=source_name
        )


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
            "data_sources": {"company_kb": {}},
            "dataset_build": {"outputs": {"raw_kb_subdir": "sec"}},
        },
    )


def _sample_payload() -> dict:
    return {
        "cik": "320193",
        "tickers": ["AAPL"],
        "exchanges": ["Nasdaq"],
        "name": "Apple Inc.",
        "formerNames": [
            {"name": "Apple Computer, Inc.", "from": "1977-01-03", "to": "2007-01-09"}
        ],
        "sic": "3571",
        "sicDescription": "Electronic Computers",
        "addresses": {
            "business": {
                "street1": "One Apple Park Way",
                "city": "Cupertino",
                "stateOrCountry": "CA",
                "zipCode": "95014",
            }
        },
    }


def test_company_kb_pipeline_writes_kb_mapping_alias_and_manifest(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    fake_client = FakeSecClient({"0000320193": _sample_payload()})
    pipeline = CompanyKbPipeline(settings=settings, client=cast(SecEdgarClient, fake_client))

    summary = pipeline.build_from_ciks(["320193"], run_label="stage7test")

    company_kb_path = Path(summary["company_kb_path"])
    mapping_path = Path(summary["ticker_mappings_path"])
    alias_path = Path(summary["alias_path"])
    quality_path = Path(summary["quality_report_path"])
    manifest_path = Path(summary["manifest_path"])

    assert company_kb_path.exists()
    assert mapping_path.exists()
    assert alias_path.exists()
    assert quality_path.exists()
    assert manifest_path.exists()

    company_df = pd.read_parquet(company_kb_path)
    mapping_df = pd.read_parquet(mapping_path)
    alias_df = pd.read_parquet(alias_path)

    assert list(company_df["ticker"]) == ["AAPL"]
    assert list(mapping_df["cik"]) == ["0000320193"]
    assert set(alias_df["alias_type"]) == {"current_name", "former_name"}

    quality = json.loads(quality_path.read_text(encoding="utf-8"))
    assert quality["company_row_count"] == 1
    assert quality["mapping_row_count"] == 1


def test_enrich_universe_snapshot_adds_cik_and_exchange_fields() -> None:
    snapshot = UniverseSnapshot(
        records=(
            {"ticker": "AAPL", "name": "Apple"},
            {"ticker": "MSFT", "name": "Microsoft"},
        ),
        source_path=Path("universe.csv"),
        ticker_column="ticker",
    )

    enriched = enrich_universe_snapshot(
        snapshot,
        [
            {"ticker": "AAPL", "cik": "0000320193", "exchange": "Nasdaq"},
            {"ticker": "MSFT", "cik": "0000789019", "exchange": "Nasdaq"},
        ],
        fields_to_copy=("cik", "exchange"),
    )

    assert enriched.records[0]["cik"] == "0000320193"
    assert enriched.records[1]["exchange"] == "Nasdaq"
    assert enriched.warnings
