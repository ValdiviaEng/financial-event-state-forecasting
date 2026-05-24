"""Prediction export helpers for sklearn and torch baseline models."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.models.baseline_models import SklearnRegressorWrapper, load_baseline_checkpoint
from src.models.dataloaders import (
    MarketPanelBatch,
    MarketPanelDataset,
    MultimodalPanelBatch,
    MultimodalPanelDataset,
    create_market_dataloader,
    create_multimodal_dataloader,
)


def load_model_checkpoint(file_path: str | Path, *, model_name: str) -> Any:
    """Load a saved baseline checkpoint."""

    if model_name in {"ridge", "elastic_net"}:
        return load_baseline_checkpoint(file_path)
    if model_name in {"market_mlp", "multimodal_event_state"}:
        torch = importlib.import_module("torch")
        return torch.load(file_path, map_location="cpu")
    raise ValueError(f"Unsupported model_name '{model_name}'.")


def predict_sklearn_model(
    model: SklearnRegressorWrapper,
    features: pd.DataFrame | np.ndarray,
    *,
    row_ids: list[dict[str, Any]],
    target_columns: list[str],
    model_name: str,
    split_id: int,
    partition: str,
) -> pd.DataFrame:
    """Generate prediction DataFrame for a sklearn baseline."""

    feature_matrix = features.to_numpy(dtype=float) if isinstance(features, pd.DataFrame) else np.asarray(features, dtype=float)
    predictions = model.predict(feature_matrix)
    return build_prediction_frame(
        row_ids=row_ids,
        predictions=predictions,
        target_columns=target_columns,
        model_name=model_name,
        split_id=split_id,
        partition=partition,
    )


def predict_torch_model(
    model: Any,
    dataset: MarketPanelDataset,
    *,
    target_columns: list[str],
    model_name: str,
    split_id: int,
    partition: str,
    device: str = "cpu",
    batch_size: int = 256,
) -> pd.DataFrame:
    """Generate prediction DataFrame for a torch baseline."""

    torch = importlib.import_module("torch")
    dataloader = create_market_dataloader(dataset, batch_size=batch_size, shuffle=False, num_workers=0, pin_memory=False)
    model.eval()
    model.to(device)

    predictions: list[np.ndarray] = []
    row_ids: list[dict[str, Any]] = []
    with torch.no_grad():
        for batch in dataloader:
            assert isinstance(batch, MarketPanelBatch)
            outputs = model(batch.features.to(device))
            predictions.append(outputs.detach().cpu().numpy())
            row_ids.extend(batch.row_ids)

    prediction_matrix = np.vstack(predictions) if predictions else np.empty((0, len(target_columns)))
    return build_prediction_frame(
        row_ids=row_ids,
        predictions=prediction_matrix,
        target_columns=target_columns,
        model_name=model_name,
        split_id=split_id,
        partition=partition,
    )


def predict_torch_multimodal_model(
    model: Any,
    dataset: MultimodalPanelDataset,
    *,
    target_columns: list[str],
    model_name: str,
    split_id: int,
    partition: str,
    device: str = "cpu",
    batch_size: int = 256,
) -> pd.DataFrame:
    """Generate prediction DataFrame for a multimodal torch model."""

    torch = importlib.import_module("torch")
    dataloader = create_multimodal_dataloader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=False,
    )
    model.eval()
    model.to(device)

    predictions: list[np.ndarray] = []
    row_ids: list[dict[str, Any]] = []
    with torch.no_grad():
        for batch in dataloader:
            assert isinstance(batch, MultimodalPanelBatch)
            outputs = model(
                batch.market_features.to(device),
                event_state_features=None if batch.event_state_features is None else batch.event_state_features.to(device),
                company_features=None if batch.company_features is None else batch.company_features.to(device),
                event_state_mask=None if batch.event_state_mask is None else batch.event_state_mask.to(device),
                company_mask=None if batch.company_mask is None else batch.company_mask.to(device),
            )
            predictions.append(outputs.detach().cpu().numpy())
            row_ids.extend(batch.row_ids)

    prediction_matrix = np.vstack(predictions) if predictions else np.empty((0, len(target_columns)))
    return build_prediction_frame(
        row_ids=row_ids,
        predictions=prediction_matrix,
        target_columns=target_columns,
        model_name=model_name,
        split_id=split_id,
        partition=partition,
    )


def build_prediction_frame(
    *,
    row_ids: list[dict[str, Any]],
    predictions: np.ndarray,
    target_columns: list[str],
    model_name: str,
    split_id: int,
    partition: str,
) -> pd.DataFrame:
    """Build a joinable prediction table with row identifiers preserved."""

    prediction_array = np.asarray(predictions, dtype=float)
    if prediction_array.ndim == 1:
        prediction_array = prediction_array.reshape(-1, 1)
    if prediction_array.shape[0] != len(row_ids):
        raise ValueError(
            f"Prediction row count {prediction_array.shape[0]} does not match row_id count {len(row_ids)}."
        )

    prediction_columns = [f"pred_{column}" for column in target_columns]
    prediction_df = pd.DataFrame(prediction_array, columns=prediction_columns)
    row_id_df = pd.DataFrame(row_ids)
    output = pd.concat([row_id_df, prediction_df], axis=1)
    output["model_name"] = model_name
    output["split_id"] = split_id
    output["partition"] = partition
    return output
