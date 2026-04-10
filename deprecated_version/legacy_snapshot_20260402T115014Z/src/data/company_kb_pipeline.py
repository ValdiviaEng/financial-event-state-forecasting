"""SEC company knowledge-base ingestion and canonical storage pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import importlib
from pathlib import Path
from typing import Any

from src.data.data_contracts import SCHEMA_VERSION, validate_manifest, validate_records
from src.data.sec_edgar_client import SecEdgarClient
from src.utils.config_loader import ResolvedSettings
from src.utils.io_utils import read_parquet, write_json, write_manifest, write_parquet


@dataclass(frozen=True, slots=True)
class CompanyKbBuildResult:
    """Summary of one KB build run."""

    requested_ciks: tuple[str, ...]
    company_kb_path: Path
    ticker_mappings_path: Path
    alias_path: Path
    quality_report_path: Path
    manifest_path: Path
    raw_paths: tuple[Path, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_ciks": list(self.requested_ciks),
            "company_kb_path": str(self.company_kb_path),
            "ticker_mappings_path": str(self.ticker_mappings_path),
            "alias_path": str(self.alias_path),
            "quality_report_path": str(self.quality_report_path),
            "manifest_path": str(self.manifest_path),
            "raw_paths": [str(path) for path in self.raw_paths],
        }


class CompanyKbPipeline:
    """Pipeline for SEC metadata ingestion and KB table generation."""

    def __init__(self, *, settings: ResolvedSettings, client: SecEdgarClient) -> None:
        self.settings = settings
        self.client = client
        self.dataset_build_config = settings.get_config("dataset_build")

    @classmethod
    def from_settings(
        cls,
        settings: ResolvedSettings,
        client: SecEdgarClient | None = None,
    ) -> "CompanyKbPipeline":
        return cls(settings=settings, client=client or SecEdgarClient.from_settings(settings))

    def raw_payload_path(self, cik: str) -> Path:
        raw_subdir = self.dataset_build_config.get("outputs", {}).get("raw_kb_subdir", "sec")
        return self.settings.project_paths.raw_provider_dir(raw_subdir) / "submissions" / f"CIK{cik}.json"

    def ledger_path(self) -> Path:
        raw_subdir = self.dataset_build_config.get("outputs", {}).get("raw_kb_subdir", "sec")
        return self.settings.project_paths.raw_provider_dir(raw_subdir) / "sec_request_ledger.parquet"

    def company_kb_path(self) -> Path:
        return self.settings.project_paths.data_kb_dir / "company_kb.parquet"

    def ticker_mappings_path(self) -> Path:
        return self.settings.project_paths.data_kb_dir / "company_ticker_mappings.parquet"

    def alias_path(self) -> Path:
        return self.settings.project_paths.data_kb_dir / "company_aliases.parquet"

    def quality_report_path(self) -> Path:
        return self.settings.project_paths.data_kb_dir / "company_kb_quality.json"

    def manifest_path(self, run_label: str | None = None) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        suffix = f"_{run_label}" if run_label else ""
        return self.settings.project_paths.data_manifests_dir / f"company_kb_manifest{suffix}_{timestamp}.json"

    def build_from_ciks(
        self,
        ciks: list[str] | tuple[str, ...],
        *,
        run_label: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        normalized_ciks = [self.client.normalize_cik(cik) for cik in ciks]
        summary: dict[str, Any] = {
            "stage": "company_kb_build",
            "schema_version": SCHEMA_VERSION,
            "requested_ciks": normalized_ciks,
            "dry_run": dry_run,
        }
        if dry_run:
            return summary

        raw_paths: list[Path] = []
        ledger_records: list[dict[str, Any]] = []
        company_rows: list[dict[str, Any]] = []
        mapping_rows: list[dict[str, Any]] = []
        alias_rows: list[dict[str, Any]] = []
        effective_date = datetime.now(UTC).date()

        for cik in normalized_ciks:
            payload, metadata = self.client.get_submissions(cik)
            raw_path = self.raw_payload_path(cik)
            write_json(payload, raw_path)
            raw_paths.append(raw_path)
            ledger_records.append(metadata.as_ledger_record(raw_path=str(raw_path)))

            company_row = self._prepare_company_row(
                self.client.extract_company_metadata(payload),
                effective_date=effective_date,
            )
            company_rows.append(company_row)
            mapping_rows.extend(
                self._prepare_mapping_rows(
                    self.client.extract_ticker_cik_mappings(payload),
                    effective_date=effective_date,
                )
            )
            alias_rows.extend(self._build_alias_rows(company_row))

        company_rows = self._merge_rows("company_kb", self.company_kb_path(), company_rows)
        mapping_rows = self._merge_rows("company_ticker_mappings", self.ticker_mappings_path(), mapping_rows)
        alias_rows = self._merge_rows("company_aliases", self.alias_path(), alias_rows)

        validate_records("company_kb", company_rows)
        validate_records("company_ticker_mappings", mapping_rows)
        validate_records("company_aliases", alias_rows)

        pandas_module = importlib.import_module("pandas")
        write_parquet(pandas_module.DataFrame(company_rows), self.company_kb_path(), index=False)
        write_parquet(pandas_module.DataFrame(mapping_rows), self.ticker_mappings_path(), index=False)
        write_parquet(pandas_module.DataFrame(alias_rows), self.alias_path(), index=False)
        self._append_ledger_records(ledger_records)

        quality_report = self._build_quality_report(
            company_rows=company_rows,
            mapping_rows=mapping_rows,
            alias_rows=alias_rows,
        )
        write_json(quality_report, self.quality_report_path())

        manifest_payload = {
            "manifest_version": "1",
            "dataset_name": "company_kb",
            "dataset_version": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "source_tables": ["company_kb", "company_ticker_mappings", "company_aliases"],
            "summary": quality_report,
        }
        validate_manifest(manifest_payload)
        manifest_path = self.manifest_path(run_label=run_label)
        write_manifest(manifest_payload, manifest_path)

        result = CompanyKbBuildResult(
            requested_ciks=tuple(normalized_ciks),
            company_kb_path=self.company_kb_path(),
            ticker_mappings_path=self.ticker_mappings_path(),
            alias_path=self.alias_path(),
            quality_report_path=self.quality_report_path(),
            manifest_path=manifest_path,
            raw_paths=tuple(raw_paths),
        )
        summary.update(result.as_dict())
        return summary

    def _prepare_company_row(self, row: dict[str, Any], *, effective_date) -> dict[str, Any]:
        prepared = dict(row)
        prepared["effective_date"] = effective_date
        return prepared

    def _prepare_mapping_rows(self, rows: list[dict[str, Any]], *, effective_date) -> list[dict[str, Any]]:
        prepared: list[dict[str, Any]] = []
        for row in rows:
            prepared.append(
                {
                    "ticker": row.get("ticker"),
                    "cik": row.get("cik"),
                    "exchange": row.get("exchange"),
                    "source": row.get("source", "sec_edgar"),
                    "effective_date": effective_date,
                }
            )
        return prepared

    def _build_alias_rows(self, company_row: dict[str, Any]) -> list[dict[str, Any]]:
        ticker = company_row.get("ticker")
        cik = company_row.get("cik")
        source = company_row.get("source", "sec_edgar")
        aliases: list[dict[str, Any]] = []

        current_name = company_row.get("name_current")
        if current_name:
            aliases.append(
                {
                    "ticker": ticker,
                    "cik": cik,
                    "alias_name": current_name,
                    "alias_type": "current_name",
                    "source": source,
                    "valid_from": None,
                    "valid_to": None,
                    "effective_date": company_row.get("effective_date"),
                }
            )

        for former_name in company_row.get("former_names") or []:
            name = former_name.get("name") if isinstance(former_name, dict) else None
            if not name:
                continue
            aliases.append(
                {
                    "ticker": ticker,
                    "cik": cik,
                    "alias_name": name,
                    "alias_type": "former_name",
                    "source": source,
                    "valid_from": former_name.get("from") if isinstance(former_name, dict) else None,
                    "valid_to": former_name.get("to") if isinstance(former_name, dict) else None,
                    "effective_date": company_row.get("effective_date"),
                }
            )
        return aliases

    def _append_ledger_records(self, new_records: list[dict[str, Any]]) -> None:
        ledger_path = self.ledger_path()
        ledger_records: list[dict[str, Any]] = []
        if ledger_path.exists():
            existing = read_parquet(ledger_path, backend="pandas")
            ledger_records = existing.to_dict(orient="records")
        ledger_records.extend(new_records)
        pandas_module = importlib.import_module("pandas")
        write_parquet(pandas_module.DataFrame(ledger_records), ledger_path, index=False)

    def _merge_rows(self, table_name: str, path: Path, new_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        existing_rows: list[dict[str, Any]] = []
        if path.exists():
            existing = read_parquet(path, backend="pandas")
            existing_rows = existing.to_dict(orient="records")

        merged: dict[tuple[Any, ...], dict[str, Any]] = {}
        combined = existing_rows + new_rows
        def company_key(row: dict[str, Any]) -> tuple[Any, ...]:
            return (row.get("ticker"), row.get("effective_date"))

        def mapping_key(row: dict[str, Any]) -> tuple[Any, ...]:
            return (row.get("ticker"), row.get("cik"), row.get("effective_date"))

        def alias_key(row: dict[str, Any]) -> tuple[Any, ...]:
            return (
                row.get("ticker"),
                row.get("cik"),
                row.get("alias_name"),
                row.get("alias_type"),
            )

        if table_name == "company_kb":
            key_fn = company_key
        elif table_name == "company_ticker_mappings":
            key_fn = mapping_key
        else:
            key_fn = alias_key

        for row in combined:
            merged[key_fn(row)] = row
        return list(merged.values())

    def _build_quality_report(
        self,
        *,
        company_rows: list[dict[str, Any]],
        mapping_rows: list[dict[str, Any]],
        alias_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        tickers = sorted({str(row.get("ticker")) for row in mapping_rows if row.get("ticker") is not None})
        ciks = sorted({str(row.get("cik")) for row in company_rows if row.get("cik") is not None})
        return {
            "company_row_count": len(company_rows),
            "mapping_row_count": len(mapping_rows),
            "alias_row_count": len(alias_rows),
            "tickers": tickers,
            "ciks": ciks,
            "missing_current_name_count": sum(1 for row in company_rows if not row.get("name_current")),
            "missing_sic_count": sum(1 for row in company_rows if not row.get("sic")),
        }
