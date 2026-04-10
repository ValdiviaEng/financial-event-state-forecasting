"""Final modeling-dataset assembly and persistence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.data_contracts import SCHEMA_VERSION, validate_manifest, validate_records
from src.features.event_state import summarize_event_state_coverage
from src.features.labels import DEFAULT_LABEL_HORIZONS, build_multi_horizon_labels, summarize_label_availability
from src.features.market_features import (
    DEFAULT_MOMENTUM_WINDOWS,
    DEFAULT_RETURN_WINDOWS,
    DEFAULT_VOLATILITY_WINDOWS,
    DEFAULT_VOLUME_WINDOWS,
    build_market_features,
    summarize_market_feature_coverage,
)
from src.utils.config_loader import ResolvedSettings
from src.utils.io_utils import read_parquet, write_manifest, write_parquet


class ModelingDatasetError(RuntimeError):
    """Raised when final modeling-dataset assembly fails."""


@dataclass(frozen=True, slots=True)
class ModelingDatasetResult:
    """Summary of one final modeling-dataset build."""

    panel_path: Path
    manifest_path: Path
    dataset_version: str
    row_count: int
    column_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "panel_path": str(self.panel_path),
            "manifest_path": str(self.manifest_path),
            "dataset_version": self.dataset_version,
            "row_count": self.row_count,
            "column_count": self.column_count,
        }


class ModelingDatasetBuilder:
    """Builder for frozen, model-ready `(ticker, date)` panels."""

    def __init__(self, *, settings: ResolvedSettings) -> None:
        self.settings = settings
        self.features_config = settings.get_config("features")
        self.labels_config = settings.get_config("labels")

    @classmethod
    def from_settings(cls, settings: ResolvedSettings) -> "ModelingDatasetBuilder":
        return cls(settings=settings)

    def panel_path(self, dataset_version: str) -> Path:
        return self.settings.project_paths.data_final_dir / f"modeling_panel__{dataset_version}.parquet"

    def manifest_path(self, dataset_version: str) -> Path:
        return self.settings.project_paths.data_manifests_dir / f"modeling_panel__{dataset_version}.json"

    def build_panel(
        self,
        *,
        adjusted_price_rows: list[dict[str, Any]] | pd.DataFrame,
        benchmark_rows: list[dict[str, Any]] | pd.DataFrame | None = None,
        event_state_rows: list[dict[str, Any]] | pd.DataFrame | None = None,
        company_feature_rows: list[dict[str, Any]] | pd.DataFrame | None = None,
        market_feature_version: str = "v1",
        label_version: str = "v1",
        event_state_version: str | None = None,
        company_feature_version: str | None = None,
        dataset_version: str = "panel_v1",
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Build the final model-ready panel and a manifest payload.

        This stage computes market features and labels from adjusted prices and
        then left-joins optional event-state and company-feature branches.
        """

        adjusted_price_df = _coerce_frame(adjusted_price_rows)
        adjusted_price_df = _prepare_base_frame(adjusted_price_df)

        benchmark_rows_normalized = None if benchmark_rows is None else _coerce_frame(benchmark_rows).to_dict(orient="records")
        adjusted_rows_normalized = adjusted_price_df.to_dict(orient="records")

        market_feature_cfg = self.features_config.get("market_features", {})
        market_features = build_market_features(
            adjusted_rows_normalized,
            benchmark_rows=benchmark_rows_normalized,
            return_windows=tuple(market_feature_cfg.get("return_windows", DEFAULT_RETURN_WINDOWS)),
            volatility_windows=tuple(market_feature_cfg.get("volatility_windows", DEFAULT_VOLATILITY_WINDOWS)),
            momentum_windows=tuple(market_feature_cfg.get("momentum_windows", DEFAULT_MOMENTUM_WINDOWS)),
            volume_windows=tuple(market_feature_cfg.get("volume_windows", DEFAULT_VOLUME_WINDOWS)),
        )

        horizons = tuple(self.labels_config.get("horizons", DEFAULT_LABEL_HORIZONS))
        labels = build_multi_horizon_labels(
            adjusted_rows_normalized,
            benchmark_rows=benchmark_rows_normalized,
            horizons=horizons,
        )

        base_panel = adjusted_price_df.copy()
        base_panel["split_adjusted_prices_used"] = True
        base_panel["dataset_version"] = dataset_version
        base_panel["market_feature_version"] = market_feature_version
        base_panel["label_version"] = label_version
        base_panel["event_state_version"] = event_state_version
        base_panel["company_feature_version"] = company_feature_version

        panel = _safe_left_merge(base_panel, market_features, name="market_features")
        panel = _safe_left_merge(panel, labels, name="labels")

        if event_state_rows is not None:
            event_state_df = _prepare_optional_frame(event_state_rows, required_columns=("ticker", "date"), frame_name="event_states")
            event_state_version = event_state_version or "v1"
            panel["event_state_version"] = event_state_version
            panel = _safe_left_merge(panel, event_state_df, name="event_states")

        if company_feature_rows is not None:
            company_df = _coerce_frame(company_feature_rows)
            if "ticker" not in company_df.columns:
                raise ModelingDatasetError("Company feature rows must include 'ticker'.")
            if "date" in company_df.columns:
                company_df = _prepare_optional_frame(company_df, required_columns=("ticker", "date"), frame_name="company_features")
                panel = _safe_left_merge(panel, company_df, name="company_features")
            else:
                company_df = company_df.copy()
                _ensure_unique(company_df, key_columns=("ticker",), frame_name="company_features")
                panel = panel.merge(company_df, how="left", on="ticker")
            if company_feature_version is None:
                panel["company_feature_version"] = "v1"

        panel = panel.sort_values(["ticker", "date"], kind="stable").reset_index(drop=True)
        _ensure_unique(panel, key_columns=("ticker", "date"), frame_name="modeling_panel")
        validate_records("modeling_panel", panel.to_dict(orient="records"))

        manifest_payload = self._build_manifest(
            panel=panel,
            dataset_version=dataset_version,
            market_features=market_features,
            labels=labels,
            event_state_rows=event_state_rows,
            company_feature_rows=company_feature_rows,
            benchmark_rows=benchmark_rows_normalized,
            horizons=horizons,
        )
        validate_manifest(manifest_payload)
        return panel, manifest_payload

    def write_panel_and_manifest(
        self,
        *,
        panel: pd.DataFrame,
        manifest_payload: dict[str, Any],
        dataset_version: str,
    ) -> ModelingDatasetResult:
        panel_path = self.panel_path(dataset_version)
        manifest_path = self.manifest_path(dataset_version)
        write_parquet(panel, panel_path, index=False)
        write_manifest(manifest_payload, manifest_path)
        return ModelingDatasetResult(
            panel_path=panel_path,
            manifest_path=manifest_path,
            dataset_version=dataset_version,
            row_count=int(len(panel)),
            column_count=int(len(panel.columns)),
        )

    def build_from_files(
        self,
        *,
        adjusted_price_path: str | Path,
        benchmark_path: str | Path | None = None,
        event_state_path: str | Path | None = None,
        company_feature_path: str | Path | None = None,
        dataset_version: str = "panel_v1",
        market_feature_version: str = "v1",
        label_version: str = "v1",
        event_state_version: str | None = None,
        company_feature_version: str | None = None,
    ) -> ModelingDatasetResult:
        adjusted_price_df = read_parquet(adjusted_price_path, backend="pandas")
        benchmark_df = read_parquet(benchmark_path, backend="pandas") if benchmark_path is not None else None
        event_state_df = read_parquet(event_state_path, backend="pandas") if event_state_path is not None else None
        company_df = read_parquet(company_feature_path, backend="pandas") if company_feature_path is not None else None

        panel, manifest_payload = self.build_panel(
            adjusted_price_rows=adjusted_price_df,
            benchmark_rows=benchmark_df,
            event_state_rows=event_state_df,
            company_feature_rows=company_df,
            market_feature_version=market_feature_version,
            label_version=label_version,
            event_state_version=event_state_version,
            company_feature_version=company_feature_version,
            dataset_version=dataset_version,
        )
        return self.write_panel_and_manifest(
            panel=panel,
            manifest_payload=manifest_payload,
            dataset_version=dataset_version,
        )

    def _build_manifest(
        self,
        *,
        panel: pd.DataFrame,
        dataset_version: str,
        market_features: pd.DataFrame,
        labels: pd.DataFrame,
        event_state_rows: list[dict[str, Any]] | pd.DataFrame | None,
        company_feature_rows: list[dict[str, Any]] | pd.DataFrame | None,
        benchmark_rows: list[dict[str, Any]] | None,
        horizons: tuple[int, ...],
    ) -> dict[str, Any]:
        source_tables = ["adjusted_prices_daily", "labels_multi_horizon", "modeling_panel"]
        if event_state_rows is not None:
            source_tables.append("event_states_daily")
        if company_feature_rows is not None:
            source_tables.append("company_kb")
        if benchmark_rows is not None:
            source_tables.append("benchmark_prices")

        event_state_summary = None
        if event_state_rows is not None:
            event_state_df = _coerce_frame(event_state_rows)
            event_state_summary = summarize_event_state_coverage(event_state_df)

        return {
            "manifest_version": "1",
            "dataset_name": "modeling_panel",
            "dataset_version": dataset_version,
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "source_tables": source_tables,
            "summary": {
                "row_count": int(len(panel)),
                "column_count": int(len(panel.columns)),
                "market_feature_coverage": summarize_market_feature_coverage(market_features),
                "label_coverage": summarize_label_availability(labels, horizons=horizons),
                "event_state_coverage": event_state_summary,
                "split_adjusted_prices_used": True,
            },
        }


def _coerce_frame(value: list[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        return value.copy()
    return pd.DataFrame(list(value))


def _prepare_base_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        raise ModelingDatasetError("Adjusted price frame is empty; cannot build a final modeling panel.")
    required = {"ticker", "date"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ModelingDatasetError(
            "Adjusted price frame is missing required columns: " + ", ".join(missing)
        )
    prepared = frame.copy()
    prepared["date"] = pd.to_datetime(prepared["date"]).dt.date
    _ensure_unique(prepared, key_columns=("ticker", "date"), frame_name="adjusted_prices")
    return prepared.sort_values(["ticker", "date"], kind="stable").reset_index(drop=True)


def _prepare_optional_frame(
    value: list[dict[str, Any]] | pd.DataFrame,
    *,
    required_columns: tuple[str, ...],
    frame_name: str,
) -> pd.DataFrame:
    frame = _coerce_frame(value)
    missing = sorted(set(required_columns).difference(frame.columns))
    if missing:
        raise ModelingDatasetError(
            f"{frame_name} is missing required columns: {', '.join(missing)}"
        )
    prepared = frame.copy()
    if "date" in prepared.columns:
        prepared["date"] = pd.to_datetime(prepared["date"]).dt.date
    _ensure_unique(prepared, key_columns=required_columns, frame_name=frame_name)
    return prepared


def _safe_left_merge(base: pd.DataFrame, other: pd.DataFrame, *, name: str) -> pd.DataFrame:
    other = other.copy()
    overlap = [column for column in other.columns if column in base.columns and column not in {"ticker", "date"}]
    if overlap:
        raise ModelingDatasetError(
            f"Cannot merge {name}; overlapping non-key columns detected: {', '.join(sorted(overlap))}"
        )
    if set(["ticker", "date"]).issubset(other.columns):
        return base.merge(other, how="left", on=["ticker", "date"])
    raise ModelingDatasetError(f"{name} must include 'ticker' and 'date' columns for final-panel merging.")


def _ensure_unique(frame: pd.DataFrame, *, key_columns: tuple[str, ...], frame_name: str) -> None:
    duplicated = frame.duplicated(subset=list(key_columns), keep=False)
    if duplicated.any():
        raise ModelingDatasetError(
            f"{frame_name} contains duplicate rows for keys {key_columns}."
        )
