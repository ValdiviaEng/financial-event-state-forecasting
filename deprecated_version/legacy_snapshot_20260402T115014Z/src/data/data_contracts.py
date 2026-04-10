"""Canonical schema and dataset contracts.

This module is the single source of truth for canonical table names, required
columns, nullable rules, uniqueness constraints, and dataset manifest fields.
It provides lightweight validation helpers that can be used before any pipeline
stage writes data to disk or passes a table to a downstream stage.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


SCHEMA_VERSION = "0.1.0"
MANIFEST_REQUIRED_FIELDS = (
    "manifest_version",
    "dataset_name",
    "dataset_version",
    "schema_version",
    "created_at_utc",
    "source_tables",
)


class DataContractError(ValueError):
    """Raised when a dataset does not satisfy a declared table contract."""


@dataclass(frozen=True, slots=True)
class ColumnContract:
    """Schema contract for a single column."""

    name: str
    dtype: str
    nullable: bool = False
    description: str = ""


@dataclass(frozen=True, slots=True)
class TableContract:
    """Schema contract for a logical table in the project."""

    name: str
    layer: str
    description: str
    required_columns: tuple[ColumnContract, ...]
    optional_columns: tuple[ColumnContract, ...] = ()
    key_columns: tuple[str, ...] = ()
    unique_constraints: tuple[tuple[str, ...], ...] = ()
    partition_columns: tuple[str, ...] = ()
    file_format: str = "parquet"
    allow_additional_columns: bool = True

    @property
    def required_column_names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.required_columns)

    @property
    def optional_column_names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.optional_columns)

    @property
    def all_column_names(self) -> tuple[str, ...]:
        return self.required_column_names + self.optional_column_names

    @property
    def column_map(self) -> dict[str, ColumnContract]:
        return {column.name: column for column in (*self.required_columns, *self.optional_columns)}


def _col(name: str, dtype: str, *, nullable: bool = False, description: str = "") -> ColumnContract:
    return ColumnContract(name=name, dtype=dtype, nullable=nullable, description=description)


TABLE_CONTRACTS: dict[str, TableContract] = {
    "market_data_request_ledger": TableContract(
        name="market_data_request_ledger",
        layer="raw",
        description="Ledger of raw Twelve Data requests used to preserve market-ingestion auditability.",
        required_columns=(
            _col("request_id", "string"),
            _col("provider", "string"),
            _col("endpoint", "string"),
            _col("ticker", "string"),
            _col("requested_at_utc", "datetime_utc"),
            _col("response_status", "int"),
            _col("success", "bool"),
            _col("raw_path", "string"),
        ),
        optional_columns=(
            _col("interval", "string", nullable=True),
            _col("outputsize", "int", nullable=True),
            _col("start_date", "date", nullable=True),
            _col("end_date", "date", nullable=True),
            _col("credits_used", "int", nullable=True),
            _col("credits_left", "int", nullable=True),
            _col("request_url", "string", nullable=True),
            _col("error_message", "string", nullable=True),
        ),
        key_columns=("request_id",),
        unique_constraints=(("request_id",),),
        partition_columns=("ticker",),
        file_format="parquet",
        allow_additional_columns=False,
    ),
    "prices_daily": TableContract(
        name="prices_daily",
        layer="interim",
        description="Canonical unadjusted daily OHLCV history normalized from market provider payloads.",
        required_columns=(
            _col("date", "date"),
            _col("ticker", "string"),
            _col("open", "float"),
            _col("high", "float"),
            _col("low", "float"),
            _col("close", "float"),
            _col("volume", "int", nullable=True),
            _col("source", "string"),
            _col("ingest_ts", "datetime_utc"),
        ),
        key_columns=("ticker", "date"),
        unique_constraints=(("ticker", "date"),),
        partition_columns=("ticker",),
    ),
    "adjusted_prices_daily": TableContract(
        name="adjusted_prices_daily",
        layer="interim",
        description="Split-adjusted daily OHLCV history derived from canonical raw prices and split events.",
        required_columns=(
            _col("date", "date"),
            _col("ticker", "string"),
            _col("open", "float"),
            _col("high", "float"),
            _col("low", "float"),
            _col("close", "float"),
            _col("volume", "int", nullable=True),
            _col("source", "string"),
            _col("ingest_ts", "datetime_utc"),
            _col("adjustment_source", "string"),
        ),
        optional_columns=(
            _col("cumulative_split_factor", "float", nullable=True),
            _col("adjustment_applied_ts", "datetime_utc", nullable=True),
        ),
        key_columns=("ticker", "date"),
        unique_constraints=(("ticker", "date"),),
        partition_columns=("ticker",),
    ),
    "news_articles": TableContract(
        name="news_articles",
        layer="interim",
        description="Canonical article table normalized from ticker-scoped news provider payloads.",
        required_columns=(
            _col("article_id", "string"),
            _col("ticker", "string"),
            _col("published_ts_utc", "datetime_utc", nullable=True),
            _col("headline", "string", nullable=True),
            _col("source", "string", nullable=True),
            _col("url", "string", nullable=True),
            _col("provider_id", "string", nullable=True),
            _col("provider", "string"),
        ),
        optional_columns=(
            _col("summary", "string", nullable=True),
            _col("image", "string", nullable=True),
            _col("category", "string", nullable=True),
            _col("related", "string", nullable=True),
            _col("published_date_utc", "date", nullable=True),
            _col("asof_trade_date", "date", nullable=True),
            _col("after_market_close", "bool", nullable=True),
            _col("canonical_text", "string", nullable=True),
            _col("text_variant", "string", nullable=True),
            _col("text_hash", "string", nullable=True),
            _col("ingest_ts", "datetime_utc", nullable=True),
        ),
        key_columns=("ticker", "article_id"),
        unique_constraints=(("ticker", "article_id"),),
        partition_columns=("ticker",),
    ),
    "split_events": TableContract(
        name="split_events",
        layer="interim",
        description="Canonical split-event table used for local back-adjustment of raw OHLCV histories.",
        required_columns=(
            _col("ticker", "string"),
            _col("split_date", "date"),
            _col("split_factor", "float"),
            _col("source", "string"),
            _col("ingest_ts", "datetime_utc"),
        ),
        optional_columns=(
            _col("raw_factor_text", "string", nullable=True),
            _col("provider_event_id", "string", nullable=True),
        ),
        key_columns=("ticker", "split_date"),
        unique_constraints=(("ticker", "split_date"),),
        partition_columns=("ticker",),
    ),
    "article_embeddings": TableContract(
        name="article_embeddings",
        layer="embeddings",
        description="Offline article embedding cache with model metadata and text hashes.",
        required_columns=(
            _col("article_id", "string"),
            _col("model_id", "string"),
            _col("embedding_dim", "int"),
            _col("embedding", "vector[float]"),
            _col("text_hash", "string"),
            _col("embed_ts", "datetime_utc"),
        ),
        key_columns=("article_id", "model_id"),
        unique_constraints=(("article_id", "model_id"),),
        partition_columns=("model_id",),
    ),
    "event_states_daily": TableContract(
        name="event_states_daily",
        layer="final",
        description="Daily event-state vectors and scalar event regime features by ticker and date.",
        required_columns=(
            _col("ticker", "string"),
            _col("date", "date"),
            _col("state_vector", "vector[float]"),
            _col("news_count", "int"),
            _col("lookback_days", "int"),
            _col("decay_half_life_days", "int"),
        ),
        optional_columns=(
            _col("novelty", "float", nullable=True),
            _col("conflict", "float", nullable=True),
            _col("density", "float", nullable=True),
        ),
        key_columns=("ticker", "date"),
        unique_constraints=(("ticker", "date"),),
        partition_columns=("ticker",),
    ),
    "company_kb": TableContract(
        name="company_kb",
        layer="kb",
        description="Canonical company identity and metadata table built from SEC EDGAR submissions data.",
        required_columns=(
            _col("ticker", "string"),
            _col("cik", "string"),
            _col("name_current", "string", nullable=True),
            _col("former_names", "json", nullable=True),
            _col("exchanges", "json", nullable=True),
            _col("sic", "string", nullable=True),
            _col("sic_description", "string", nullable=True),
            _col("business_address", "json", nullable=True),
            _col("mailing_address", "json", nullable=True),
            _col("effective_date", "date", nullable=True),
            _col("source", "string"),
        ),
        optional_columns=(
            _col("entity_type", "string", nullable=True),
            _col("phone", "string", nullable=True),
            _col("website", "string", nullable=True),
            _col("investor_website", "string", nullable=True),
        ),
        key_columns=("ticker", "effective_date"),
        unique_constraints=(("ticker", "effective_date"),),
        partition_columns=("ticker",),
    ),
    "company_ticker_mappings": TableContract(
        name="company_ticker_mappings",
        layer="kb",
        description="Ticker-to-CIK and exchange mapping table derived from SEC metadata.",
        required_columns=(
            _col("ticker", "string"),
            _col("cik", "string"),
            _col("exchange", "string", nullable=True),
            _col("source", "string"),
            _col("effective_date", "date", nullable=True),
        ),
        key_columns=("ticker", "cik", "effective_date"),
        unique_constraints=(("ticker", "cik", "effective_date"),),
        partition_columns=("ticker",),
    ),
    "company_aliases": TableContract(
        name="company_aliases",
        layer="kb",
        description="Canonical company alias table for current and former names.",
        required_columns=(
            _col("ticker", "string"),
            _col("cik", "string"),
            _col("alias_name", "string"),
            _col("alias_type", "string"),
            _col("source", "string"),
        ),
        optional_columns=(
            _col("valid_from", "date", nullable=True),
            _col("valid_to", "date", nullable=True),
            _col("effective_date", "date", nullable=True),
        ),
        key_columns=("ticker", "cik", "alias_name", "alias_type"),
        unique_constraints=(("ticker", "cik", "alias_name", "alias_type"),),
        partition_columns=("ticker",),
    ),
    "labels_multi_horizon": TableContract(
        name="labels_multi_horizon",
        layer="final",
        description="Wide multi-horizon label table containing regression and classification targets.",
        required_columns=(
            _col("ticker", "string"),
            _col("date", "date"),
            _col("y_excess_ret_1", "float", nullable=True),
            _col("y_excess_ret_5", "float", nullable=True),
            _col("y_excess_ret_20", "float", nullable=True),
            _col("y_excess_ret_60", "float", nullable=True),
        ),
        optional_columns=(
            _col("y_ret_1", "float", nullable=True),
            _col("y_ret_5", "float", nullable=True),
            _col("y_ret_20", "float", nullable=True),
            _col("y_ret_60", "float", nullable=True),
            _col("y_dir_1", "bool", nullable=True),
            _col("y_dir_5", "bool", nullable=True),
            _col("y_dir_20", "bool", nullable=True),
            _col("y_dir_60", "bool", nullable=True),
            _col("y_downside_1", "bool", nullable=True),
            _col("y_downside_5", "bool", nullable=True),
            _col("y_downside_20", "bool", nullable=True),
            _col("y_downside_60", "bool", nullable=True),
        ),
        key_columns=("ticker", "date"),
        unique_constraints=(("ticker", "date"),),
        partition_columns=("ticker",),
    ),
    "modeling_panel": TableContract(
        name="modeling_panel",
        layer="final",
        description="Final model-ready panel keyed by ticker and date, allowing additional feature columns.",
        required_columns=(
            _col("ticker", "string"),
            _col("date", "date"),
            _col("split_adjusted_prices_used", "bool"),
            _col("dataset_version", "string"),
        ),
        optional_columns=(
            _col("market_feature_version", "string", nullable=True),
            _col("event_state_version", "string", nullable=True),
            _col("company_feature_version", "string", nullable=True),
            _col("label_version", "string", nullable=True),
        ),
        key_columns=("ticker", "date"),
        unique_constraints=(("ticker", "date"),),
        partition_columns=("date",),
        allow_additional_columns=True,
    ),
}


def list_table_contracts(layer: str | None = None) -> dict[str, TableContract]:
    """Return all known table contracts, optionally filtered by storage layer."""

    if layer is None:
        return dict(TABLE_CONTRACTS)
    return {name: contract for name, contract in TABLE_CONTRACTS.items() if contract.layer == layer}


def get_table_contract(table_name: str) -> TableContract:
    """Return a named table contract or raise a readable error if it does not exist."""

    try:
        return TABLE_CONTRACTS[table_name]
    except KeyError as exc:
        known_tables = ", ".join(sorted(TABLE_CONTRACTS))
        raise DataContractError(
            f"Unknown table contract '{table_name}'. Known table names: {known_tables}"
        ) from exc


def validate_columns(
    table_name: str,
    columns_or_data: Any,
    *,
    allow_additional_columns: bool | None = None,
) -> tuple[str, ...]:
    """Validate column presence for a table contract.

    Parameters
    ----------
    table_name:
        Canonical table contract name.
    columns_or_data:
        Either an explicit list of column names or tabular data from which column
        names can be inferred.
    allow_additional_columns:
        Override the table contract's default behavior for extra columns.
    """

    contract = get_table_contract(table_name)
    observed_columns = extract_column_names(columns_or_data)
    observed_set = set(observed_columns)

    missing = [column for column in contract.required_column_names if column not in observed_set]
    if missing:
        raise DataContractError(
            f"Table '{table_name}' is missing required columns: {', '.join(sorted(missing))}"
        )

    allow_extras = contract.allow_additional_columns
    if allow_additional_columns is not None:
        allow_extras = allow_additional_columns

    if not allow_extras:
        extras = sorted(observed_set.difference(contract.all_column_names))
        if extras:
            raise DataContractError(
                f"Table '{table_name}' contains unexpected columns: {', '.join(extras)}"
            )

    return observed_columns


def validate_records(
    table_name: str,
    records: Any,
    *,
    allow_additional_columns: bool | None = None,
    enforce_unique_constraints: bool = True,
) -> list[dict[str, Any]]:
    """Validate a row-oriented dataset against the declared table contract."""

    contract = get_table_contract(table_name)
    normalized_records = _coerce_records(records)
    validate_columns(
        table_name,
        normalized_records,
        allow_additional_columns=allow_additional_columns,
    )

    allow_extras = contract.allow_additional_columns
    if allow_additional_columns is not None:
        allow_extras = allow_additional_columns

    for row_index, row in enumerate(normalized_records):
        row_keys = set(row)
        missing = [column for column in contract.required_column_names if column not in row_keys]
        if missing:
            raise DataContractError(
                f"Row {row_index} in table '{table_name}' is missing required keys: "
                f"{', '.join(sorted(missing))}"
            )

        if not allow_extras:
            extras = sorted(row_keys.difference(contract.all_column_names))
            if extras:
                raise DataContractError(
                    f"Row {row_index} in table '{table_name}' contains unexpected keys: "
                    f"{', '.join(extras)}"
                )

        for column_name, column_contract in contract.column_map.items():
            if column_name in row and row[column_name] is None and not column_contract.nullable:
                raise DataContractError(
                    f"Row {row_index} in table '{table_name}' has null value for non-nullable "
                    f"column '{column_name}'."
                )

    if enforce_unique_constraints:
        for unique_constraint in contract.unique_constraints:
            _validate_unique_constraint(table_name, normalized_records, unique_constraint)

    return normalized_records


def validate_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a dataset manifest mapping."""

    missing = [field for field in MANIFEST_REQUIRED_FIELDS if field not in manifest]
    if missing:
        raise DataContractError(
            "Dataset manifest is missing required fields: " + ", ".join(sorted(missing))
        )

    if not isinstance(manifest["source_tables"], list):
        raise DataContractError("Dataset manifest field 'source_tables' must be a list.")

    if not str(manifest["schema_version"]):
        raise DataContractError("Dataset manifest field 'schema_version' must be non-empty.")

    return dict(manifest)


def coerce_record_types(table_name: str, record: Mapping[str, Any]) -> dict[str, Any]:
    """Coerce a single record using limited primitive conversions.

    This helper is intentionally conservative. It only coerces a subset of common
    primitive types and leaves complex values unchanged.
    """

    contract = get_table_contract(table_name)
    coerced: dict[str, Any] = {}
    for key, value in record.items():
        column_contract = contract.column_map.get(key)
        if column_contract is None or value is None:
            coerced[key] = value
            continue
        coerced[key] = _coerce_primitive_value(value, column_contract.dtype)
    return coerced


def extract_column_names(columns_or_data: Any) -> tuple[str, ...]:
    """Extract column names from common tabular structures."""

    if hasattr(columns_or_data, "columns"):
        columns = getattr(columns_or_data, "columns")
        return tuple(str(column) for column in columns)

    if isinstance(columns_or_data, Mapping):
        return tuple(str(key) for key in columns_or_data.keys())

    if isinstance(columns_or_data, Sequence) and not isinstance(columns_or_data, (str, bytes)):
        if not columns_or_data:
            return tuple()

        first_item = columns_or_data[0]
        if isinstance(first_item, str):
            return tuple(str(item) for item in columns_or_data)

        if isinstance(first_item, Mapping):
            ordered_keys: dict[str, None] = {}
            for row in columns_or_data:
                if not isinstance(row, Mapping):
                    raise DataContractError("Mixed row types found while extracting column names.")
                for key in row.keys():
                    ordered_keys[str(key)] = None
            return tuple(ordered_keys.keys())

    raise DataContractError(
        f"Could not extract column names from object of type {type(columns_or_data).__name__}."
    )


def _coerce_records(records: Any) -> list[dict[str, Any]]:
    """Coerce supported tabular data structures into a list of row dictionaries."""

    if hasattr(records, "to_dict") and hasattr(records, "columns"):
        return [dict(row) for row in records.to_dict(orient="records")]

    if isinstance(records, Sequence) and not isinstance(records, (str, bytes)):
        normalized: list[dict[str, Any]] = []
        for row in records:
            if not isinstance(row, Mapping):
                raise DataContractError(
                    f"Expected row mappings while validating records, got {type(row).__name__}."
                )
            normalized.append({str(key): value for key, value in row.items()})
        return normalized

    raise DataContractError(
        f"Unsupported record container type {type(records).__name__}; expected a row sequence "
        "or a DataFrame-like object."
    )


def _validate_unique_constraint(
    table_name: str,
    records: Iterable[Mapping[str, Any]],
    unique_constraint: tuple[str, ...],
) -> None:
    seen: set[tuple[Any, ...]] = set()
    for row_index, row in enumerate(records):
        key = tuple(row.get(column) for column in unique_constraint)
        if any(value is None for value in key):
            columns_text = ", ".join(unique_constraint)
            raise DataContractError(
                f"Row {row_index} in table '{table_name}' has null value inside uniqueness "
                f"constraint ({columns_text})."
            )
        if key in seen:
            columns_text = ", ".join(unique_constraint)
            raise DataContractError(
                f"Duplicate key detected in table '{table_name}' for uniqueness constraint "
                f"({columns_text}): {key}"
            )
        seen.add(key)


def _coerce_primitive_value(value: Any, dtype: str) -> Any:
    if dtype == "string":
        return str(value)
    if dtype == "float":
        return float(value)
    if dtype == "int":
        return int(value)
    if dtype == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes"}:
                return True
            if normalized in {"false", "0", "no"}:
                return False
        return bool(value)
    return value
