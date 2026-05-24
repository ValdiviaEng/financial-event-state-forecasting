"""Final-panel feature selection, dataset, and dataloader helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_METADATA_COLUMNS = {
    "ticker",
    "date",
    "dataset_version",
    "split_adjusted_prices_used",
    "market_feature_version",
    "label_version",
    "event_state_version",
    "company_feature_version",
}

DEFAULT_EVENT_STATE_COLUMNS = {
    "state_vector",
    "news_count",
    "density",
    "novelty",
    "conflict",
    "lookback_days",
    "decay_half_life_days",
}


@dataclass(frozen=True, slots=True)
class MultimodalPanelBatch:
    """Batch container returned by the multimodal panel dataset."""

    market_features: Any
    event_state_features: Any | None
    event_state_mask: Any | None
    company_features: Any | None
    company_mask: Any | None
    targets: Any
    row_ids: list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class MarketPanelBatch:
    """Batch container returned by the market-only panel dataset."""

    features: Any
    targets: Any
    row_ids: list[dict[str, Any]]


class MarketPanelDataset:
    """Torch-compatible dataset wrapper around a final modeling panel."""

    def __init__(
        self,
        panel: pd.DataFrame,
        *,
        feature_columns: list[str],
        target_columns: list[str],
        id_columns: tuple[str, ...] = ("ticker", "date"),
    ) -> None:
        self.panel = panel.reset_index(drop=True).copy()
        self.feature_columns = feature_columns
        self.target_columns = target_columns
        self.id_columns = id_columns

        for column in (*feature_columns, *target_columns, *id_columns):
            if column not in self.panel.columns:
                raise ValueError(f"Column '{column}' is missing from the panel dataset.")

        self.features = self.panel[feature_columns].astype(float).to_numpy(dtype=np.float32)
        self.targets = self.panel[target_columns].astype(float).to_numpy(dtype=np.float32)
        self.row_ids = [
            {column: self.panel.iloc[index][column] for column in id_columns}
            for index in range(len(self.panel))
        ]

    def __len__(self) -> int:
        return int(len(self.panel))

    def __getitem__(self, index: int) -> dict[str, Any]:
        return {
            "features": self.features[index],
            "targets": self.targets[index],
            "row_id": self.row_ids[index],
        }


class MultimodalPanelDataset:
    """Torch-compatible dataset wrapper for market + event-state inputs."""

    def __init__(
        self,
        panel: pd.DataFrame,
        *,
        market_feature_columns: list[str],
        target_columns: list[str],
        event_scalar_columns: list[str] | None = None,
        event_vector_column: str | None = "state_vector",
        company_feature_columns: list[str] | None = None,
        id_columns: tuple[str, ...] = ("ticker", "date"),
    ) -> None:
        self.panel = panel.reset_index(drop=True).copy()
        self.market_feature_columns = market_feature_columns
        self.target_columns = target_columns
        self.event_scalar_columns = event_scalar_columns or []
        self.event_vector_column = event_vector_column if event_vector_column in self.panel.columns else None
        self.company_feature_columns = company_feature_columns or []
        self.id_columns = id_columns

        for column in (*market_feature_columns, *target_columns, *id_columns):
            if column not in self.panel.columns:
                raise ValueError(f"Column '{column}' is missing from the multimodal panel dataset.")

        self.market_features = self.panel[market_feature_columns].astype(float).to_numpy(dtype=np.float32)
        self.targets = self.panel[target_columns].astype(float).to_numpy(dtype=np.float32)
        self.row_ids = [
            {column: self.panel.iloc[index][column] for column in id_columns}
            for index in range(len(self.panel))
        ]

        self.event_state_features, self.event_state_mask = self._prepare_event_state_features()
        self.company_features, self.company_mask = self._prepare_company_features()

    def __len__(self) -> int:
        return int(len(self.panel))

    def __getitem__(self, index: int) -> dict[str, Any]:
        return {
            "market_features": self.market_features[index],
            "event_state_features": None if self.event_state_features is None else self.event_state_features[index],
            "event_state_mask": None if self.event_state_mask is None else self.event_state_mask[index],
            "company_features": None if self.company_features is None else self.company_features[index],
            "company_mask": None if self.company_mask is None else self.company_mask[index],
            "targets": self.targets[index],
            "row_id": self.row_ids[index],
        }

    def _prepare_event_state_features(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        if self.event_vector_column is None and not self.event_scalar_columns:
            return None, None

        rows: list[np.ndarray] = []
        masks: list[float] = []
        for _, row in self.panel.iterrows():
            vector_values: list[float] = []
            has_signal = False
            if self.event_vector_column is not None:
                raw_vector = row[self.event_vector_column]
                if isinstance(raw_vector, (list, tuple, np.ndarray)):
                    vector_values.extend(float(value) for value in raw_vector)
                    has_signal = True
                elif raw_vector is None or (isinstance(raw_vector, float) and np.isnan(raw_vector)):
                    vector_values.extend([])
                else:
                    raise ValueError(
                        f"Event vector column '{self.event_vector_column}' must contain lists or nulls."
                    )
            for column in self.event_scalar_columns:
                value = row[column]
                if pd.isna(value):
                    vector_values.append(0.0)
                else:
                    vector_values.append(float(value))
                    has_signal = True
            rows.append(np.asarray(vector_values, dtype=np.float32))
            masks.append(1.0 if has_signal else 0.0)

        max_dim = max((len(row) for row in rows), default=0)
        if max_dim == 0:
            return None, None
        padded = [np.pad(row, (0, max_dim - len(row)), constant_values=0.0) for row in rows]
        return np.vstack(padded).astype(np.float32), np.asarray(masks, dtype=np.float32)

    def _prepare_company_features(self) -> tuple[np.ndarray | None, np.ndarray | None]:
        if not self.company_feature_columns:
            return None, None
        features = self.panel[self.company_feature_columns].astype(float).fillna(0.0).to_numpy(dtype=np.float32)
        mask = (~self.panel[self.company_feature_columns].isna().all(axis=1)).astype(float).to_numpy(dtype=np.float32)
        return features, mask


def select_market_feature_columns(panel: pd.DataFrame) -> list[str]:
    """Select numeric market-only feature columns from a final panel."""

    excluded_prefixes = ("y_",)
    excluded_columns = set(DEFAULT_METADATA_COLUMNS) | set(DEFAULT_EVENT_STATE_COLUMNS)
    selected: list[str] = []
    for column in panel.columns:
        if column in excluded_columns:
            continue
        if column.startswith("company_"):
            continue
        if any(column.startswith(prefix) for prefix in excluded_prefixes):
            continue
        if pd.api.types.is_numeric_dtype(panel[column]):
            selected.append(column)
    return selected


def select_target_columns(
    panel: pd.DataFrame,
    *,
    horizons: list[int] | tuple[int, ...],
    target_prefix: str = "y_excess_ret",
) -> list[str]:
    """Select target columns from a final panel for the requested horizons."""

    targets = [f"{target_prefix}_{horizon}" for horizon in horizons if f"{target_prefix}_{horizon}" in panel.columns]
    if not targets:
        raise ValueError(
            f"No target columns were found for prefix '{target_prefix}' and horizons {list(horizons)}."
        )
    return targets


def select_event_state_scalar_columns(panel: pd.DataFrame) -> list[str]:
    """Select scalar event-state columns from a final panel."""

    selected: list[str] = []
    for column in sorted(DEFAULT_EVENT_STATE_COLUMNS - {"state_vector"}):
        if column in panel.columns and pd.api.types.is_numeric_dtype(panel[column]):
            selected.append(column)
    return selected


def select_company_feature_columns(panel: pd.DataFrame) -> list[str]:
    """Select optional numeric company-feature columns from a final panel."""

    excluded = set(DEFAULT_METADATA_COLUMNS) | set(DEFAULT_EVENT_STATE_COLUMNS)
    excluded.update(column for column in panel.columns if column.startswith("y_"))
    selected: list[str] = []
    for column in panel.columns:
        if column in excluded:
            continue
        if pd.api.types.is_numeric_dtype(panel[column]) and column.startswith("company_"):
            selected.append(column)
    return selected


def filter_rows_with_complete_targets(panel: pd.DataFrame, *, target_columns: list[str]) -> pd.DataFrame:
    """Filter panel rows to those with complete target availability."""

    return panel.dropna(subset=target_columns).reset_index(drop=True)


def create_market_dataloader(
    dataset: MarketPanelDataset,
    *,
    batch_size: int,
    shuffle: bool,
    num_workers: int = 0,
    pin_memory: bool = False,
) -> Any:
    """Create a PyTorch DataLoader lazily from a market panel dataset."""

    import importlib

    try:
        torch_utils_data = importlib.import_module("torch.utils.data")
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyTorch is required to create a market dataloader.") from exc

    return torch_utils_data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        collate_fn=_collate_market_batch,
    )


def create_multimodal_dataloader(
    dataset: MultimodalPanelDataset,
    *,
    batch_size: int,
    shuffle: bool,
    num_workers: int = 0,
    pin_memory: bool = False,
) -> Any:
    """Create a PyTorch DataLoader lazily from a multimodal panel dataset."""

    import importlib

    try:
        torch_utils_data = importlib.import_module("torch.utils.data")
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyTorch is required to create a multimodal dataloader.") from exc

    return torch_utils_data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        collate_fn=_collate_multimodal_batch,
    )


def _collate_market_batch(items: list[dict[str, Any]]) -> MarketPanelBatch:
    import importlib

    torch = importlib.import_module("torch")
    features = torch.tensor(np.stack([item["features"] for item in items]), dtype=torch.float32)
    targets = torch.tensor(np.stack([item["targets"] for item in items]), dtype=torch.float32)
    row_ids = [item["row_id"] for item in items]
    return MarketPanelBatch(features=features, targets=targets, row_ids=row_ids)


def _collate_multimodal_batch(items: list[dict[str, Any]]) -> MultimodalPanelBatch:
    import importlib

    torch = importlib.import_module("torch")
    market_features = torch.tensor(np.stack([item["market_features"] for item in items]), dtype=torch.float32)
    targets = torch.tensor(np.stack([item["targets"] for item in items]), dtype=torch.float32)
    row_ids = [item["row_id"] for item in items]

    event_state_features = None
    event_state_mask = None
    if items[0]["event_state_features"] is not None:
        event_state_features = torch.tensor(
            np.stack([item["event_state_features"] for item in items]), dtype=torch.float32
        )
        event_state_mask = torch.tensor(
            np.stack([item["event_state_mask"] for item in items]), dtype=torch.float32
        )

    company_features = None
    company_mask = None
    if items[0]["company_features"] is not None:
        company_features = torch.tensor(
            np.stack([item["company_features"] for item in items]), dtype=torch.float32
        )
        company_mask = torch.tensor(
            np.stack([item["company_mask"] for item in items]), dtype=torch.float32
        )

    return MultimodalPanelBatch(
        market_features=market_features,
        event_state_features=event_state_features,
        event_state_mask=event_state_mask,
        company_features=company_features,
        company_mask=company_mask,
        targets=targets,
        row_ids=row_ids,
    )
