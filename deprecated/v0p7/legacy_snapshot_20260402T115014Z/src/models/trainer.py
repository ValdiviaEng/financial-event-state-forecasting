"""Training helpers for market-only baseline models."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.models.baseline_models import BaselineModelError, SklearnRegressorWrapper, build_baseline_model, is_torch_available
from src.models.dataloaders import (
    MarketPanelDataset,
    MultimodalPanelDataset,
    create_market_dataloader,
    create_multimodal_dataloader,
    filter_rows_with_complete_targets,
    select_company_feature_columns,
    select_event_state_scalar_columns,
    select_market_feature_columns,
    select_target_columns,
)
from src.models.inference import predict_sklearn_model, predict_torch_model, predict_torch_multimodal_model
from src.models.loss_functions import compute_regression_loss, compute_torch_regression_loss
from src.models.multimodal_models import build_multimodal_regressor
from src.utils.io_utils import write_json, write_parquet
from src.utils.reproducibility import build_run_metadata, save_run_metadata, seed_everything


@dataclass(frozen=True, slots=True)
class BaselineFoldResult:
    """Summary of one baseline-training fold."""

    model_name: str
    split_id: int
    checkpoint_path: Path
    predictions_path: Path
    metrics_path: Path
    train_row_count: int
    validation_row_count: int
    test_row_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "split_id": self.split_id,
            "checkpoint_path": str(self.checkpoint_path),
            "predictions_path": str(self.predictions_path),
            "metrics_path": str(self.metrics_path),
            "train_row_count": self.train_row_count,
            "validation_row_count": self.validation_row_count,
            "test_row_count": self.test_row_count,
        }


@dataclass(frozen=True, slots=True)
class MultimodalFoldResult:
    """Summary of one multimodal-training fold."""

    model_name: str
    split_id: int
    checkpoint_path: Path
    predictions_path: Path
    metrics_path: Path
    train_row_count: int
    validation_row_count: int
    test_row_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "split_id": self.split_id,
            "checkpoint_path": str(self.checkpoint_path),
            "predictions_path": str(self.predictions_path),
            "metrics_path": str(self.metrics_path),
            "train_row_count": self.train_row_count,
            "validation_row_count": self.validation_row_count,
            "test_row_count": self.test_row_count,
        }


def train_market_baseline_fold(
    *,
    panel: pd.DataFrame,
    train_dates: tuple[Any, ...],
    validation_dates: tuple[Any, ...],
    test_dates: tuple[Any, ...],
    model_name: str,
    split_id: int,
    run_dir: str | Path,
    horizons: list[int] | tuple[int, ...],
    target_prefix: str = "y_excess_ret",
    seed: int = 42,
    training_config: dict[str, Any] | None = None,
    model_config: dict[str, Any] | None = None,
) -> BaselineFoldResult:
    """Train one market-only baseline fold and persist its artifacts."""

    training_cfg = training_config or {}
    model_cfg = model_config or {}
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    prepared = panel.copy()
    prepared["date"] = pd.to_datetime(prepared["date"]).dt.date
    target_columns = select_target_columns(prepared, horizons=list(horizons), target_prefix=target_prefix)
    feature_columns = select_market_feature_columns(prepared)

    train_df = filter_rows_with_complete_targets(prepared[prepared["date"].isin(train_dates)], target_columns=target_columns)
    validation_df = filter_rows_with_complete_targets(prepared[prepared["date"].isin(validation_dates)], target_columns=target_columns)
    test_df = filter_rows_with_complete_targets(prepared[prepared["date"].isin(test_dates)], target_columns=target_columns)

    if train_df.empty:
        raise ValueError("Training fold has no rows after target filtering.")

    feature_columns = _filter_all_nan_feature_columns(train_df, feature_columns, frame_name="market baseline")

    seed_everything(seed, deterministic_torch=bool(training_cfg.get("deterministic_torch", False)))

    if model_name in {"ridge", "elastic_net"}:
        model = build_baseline_model(
            model_name,
            alpha=float(model_cfg.get("alpha", 1.0)),
            l1_ratio=float(model_cfg.get("l1_ratio", 0.5)),
        )
        assert isinstance(model, SklearnRegressorWrapper)
        model.fit(train_df[feature_columns].to_numpy(dtype=float), train_df[target_columns].to_numpy(dtype=float))
        checkpoint_path = run_path / "checkpoints" / f"split_{split_id}__{model_name}.joblib"
        model.save(checkpoint_path)
        predictions = _collect_sklearn_predictions(
            model,
            feature_columns=feature_columns,
            target_columns=target_columns,
            split_id=split_id,
            model_name=model_name,
            train_df=train_df,
            validation_df=validation_df,
            test_df=test_df,
        )
    elif model_name == "market_mlp":
        checkpoint_path, predictions = _train_torch_market_mlp(
            panel=prepared,
            train_df=train_df,
            validation_df=validation_df,
            test_df=test_df,
            feature_columns=feature_columns,
            target_columns=target_columns,
            split_id=split_id,
            run_dir=run_path,
            seed=seed,
            training_config=training_cfg,
            model_config=model_cfg,
        )
    else:
        raise BaselineModelError(f"Unsupported market baseline model '{model_name}'.")

    metrics = _compute_fold_metrics(predictions, prepared, target_columns=target_columns)
    predictions_path = run_path / "predictions" / f"split_{split_id}__{model_name}.parquet"
    metrics_path = run_path / "metrics" / f"split_{split_id}__{model_name}.json"
    write_parquet(predictions, predictions_path, index=False)
    write_json(metrics, metrics_path)

    metadata_path = run_path / "run_metadata" / f"split_{split_id}__{model_name}.json"
    save_run_metadata(
        build_run_metadata(
            run_id=f"split_{split_id}__{model_name}",
            random_seed=seed,
            deterministic_torch=bool(training_cfg.get("deterministic_torch", False)),
            extra={
                "feature_columns": feature_columns,
                "target_columns": target_columns,
                "train_row_count": len(train_df),
                "validation_row_count": len(validation_df),
                "test_row_count": len(test_df),
            },
        ),
        metadata_path,
    )

    return BaselineFoldResult(
        model_name=model_name,
        split_id=split_id,
        checkpoint_path=checkpoint_path,
        predictions_path=predictions_path,
        metrics_path=metrics_path,
        train_row_count=int(len(train_df)),
        validation_row_count=int(len(validation_df)),
        test_row_count=int(len(test_df)),
    )


def _collect_sklearn_predictions(
    model: SklearnRegressorWrapper,
    *,
    feature_columns: list[str],
    target_columns: list[str],
    split_id: int,
    model_name: str,
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not train_df.empty:
        frames.append(
            predict_sklearn_model(
                model,
                train_df[feature_columns],
                row_ids=train_df[["ticker", "date"]].to_dict(orient="records"),
                target_columns=target_columns,
                model_name=model_name,
                split_id=split_id,
                partition="train",
            )
        )
    if not validation_df.empty:
        frames.append(
            predict_sklearn_model(
                model,
                validation_df[feature_columns],
                row_ids=validation_df[["ticker", "date"]].to_dict(orient="records"),
                target_columns=target_columns,
                model_name=model_name,
                split_id=split_id,
                partition="validation",
            )
        )
    if not test_df.empty:
        frames.append(
            predict_sklearn_model(
                model,
                test_df[feature_columns],
                row_ids=test_df[["ticker", "date"]].to_dict(orient="records"),
                target_columns=target_columns,
                model_name=model_name,
                split_id=split_id,
                partition="test",
            )
        )
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _train_torch_market_mlp(
    *,
    panel: pd.DataFrame,
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_columns: list[str],
    target_columns: list[str],
    split_id: int,
    run_dir: Path,
    seed: int,
    training_config: dict[str, Any],
    model_config: dict[str, Any],
) -> tuple[Path, pd.DataFrame]:
    if not is_torch_available():
        raise BaselineModelError("market_mlp requires PyTorch, which is not installed.")

    torch = importlib.import_module("torch")
    device = str(training_config.get("device", "cpu"))
    model = build_baseline_model(
        "market_mlp",
        input_dim=len(feature_columns),
        output_dim=len(target_columns),
        hidden_dims=tuple(model_config.get("hidden_dims", (64, 32))),
        dropout=float(model_config.get("dropout", 0.0)),
    )
    model.to(device)

    optimizer_name = str(training_config.get("optimizer", "adamw")).lower()
    learning_rate = float(training_config.get("learning_rate", 1e-3))
    weight_decay = float(training_config.get("weight_decay", 1e-4))
    optimizer = _build_optimizer(torch, model.parameters(), optimizer_name, learning_rate, weight_decay)

    train_dataset = MarketPanelDataset(train_df, feature_columns=feature_columns, target_columns=target_columns)
    validation_dataset = MarketPanelDataset(validation_df, feature_columns=feature_columns, target_columns=target_columns) if not validation_df.empty else None
    test_dataset = MarketPanelDataset(test_df, feature_columns=feature_columns, target_columns=target_columns) if not test_df.empty else None

    feature_scaler = _fit_impute_standard_scaler(train_dataset.features)
    train_dataset.features = _apply_impute_standard_scaler(train_dataset.features, feature_scaler)
    if validation_dataset is not None:
        validation_dataset.features = _apply_impute_standard_scaler(validation_dataset.features, feature_scaler)
    if test_dataset is not None:
        test_dataset.features = _apply_impute_standard_scaler(test_dataset.features, feature_scaler)

    train_loader = create_market_dataloader(
        train_dataset,
        batch_size=int(training_config.get("train_batch_size", 256)),
        shuffle=True,
        num_workers=int(training_config.get("num_workers", 0)),
        pin_memory=bool(training_config.get("pin_memory", False)),
    )
    validation_loader = (
        create_market_dataloader(
            validation_dataset,
            batch_size=int(training_config.get("eval_batch_size", 512)),
            shuffle=False,
            num_workers=0,
            pin_memory=False,
        )
        if validation_dataset is not None
        else None
    )

    max_epochs = int(training_config.get("max_epochs", 10))
    patience = int(training_config.get("early_stopping_patience", 5))
    best_state = None
    best_loss = float("inf")
    epochs_without_improvement = 0

    for _epoch in range(max_epochs):
        model.train()
        for batch in train_loader:
            batch = batch
            optimizer.zero_grad()
            predictions = model(batch.features.to(device))
            loss = compute_torch_regression_loss(
                predictions,
                batch.targets.to(device),
                loss_name=str(training_config.get("loss_name", "mse")),
            )
            loss.backward()
            optimizer.step()

        validation_loss = _evaluate_torch_loss(
            model,
            validation_loader if validation_loader is not None else train_loader,
            device=device,
            loss_name=str(training_config.get("loss_name", "mse")),
        )
        if validation_loss < best_loss:
            best_loss = validation_loss
            best_state = {key: value.detach().cpu() for key, value in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    checkpoint_path = run_dir / "checkpoints" / f"split_{split_id}__market_mlp.pt"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_name": "market_mlp",
            "state_dict": model.state_dict(),
            "feature_columns": feature_columns,
            "target_columns": target_columns,
            "seed": seed,
        },
        checkpoint_path,
    )

    frames: list[pd.DataFrame] = []
    frames.append(
        predict_torch_model(
            model,
            train_dataset,
            target_columns=target_columns,
            model_name="market_mlp",
            split_id=split_id,
            partition="train",
            device=device,
            batch_size=int(training_config.get("eval_batch_size", 512)),
        )
    )
    if validation_dataset is not None:
        frames.append(
            predict_torch_model(
                model,
                validation_dataset,
                target_columns=target_columns,
                model_name="market_mlp",
                split_id=split_id,
                partition="validation",
                device=device,
                batch_size=int(training_config.get("eval_batch_size", 512)),
            )
        )
    if test_dataset is not None:
        frames.append(
            predict_torch_model(
                model,
                test_dataset,
                target_columns=target_columns,
                model_name="market_mlp",
                split_id=split_id,
                partition="test",
                device=device,
                batch_size=int(training_config.get("eval_batch_size", 512)),
            )
        )
    predictions = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return checkpoint_path, predictions


def train_multimodal_fold(
    *,
    panel: pd.DataFrame,
    train_dates: tuple[Any, ...],
    validation_dates: tuple[Any, ...],
    test_dates: tuple[Any, ...],
    split_id: int,
    run_dir: str | Path,
    horizons: list[int] | tuple[int, ...],
    target_prefix: str = "y_excess_ret",
    seed: int = 42,
    training_config: dict[str, Any] | None = None,
    model_config: dict[str, Any] | None = None,
) -> MultimodalFoldResult:
    """Train one multimodal market + event-state fold and persist its artifacts."""

    if not is_torch_available():
        raise BaselineModelError("Multimodal training requires PyTorch, which is not installed.")

    training_cfg = training_config or {}
    model_cfg = model_config or {}
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    prepared = panel.copy()
    prepared["date"] = pd.to_datetime(prepared["date"]).dt.date
    target_columns = select_target_columns(prepared, horizons=list(horizons), target_prefix=target_prefix)
    market_feature_columns = select_market_feature_columns(prepared)
    event_scalar_columns = select_event_state_scalar_columns(prepared)
    company_feature_columns = select_company_feature_columns(prepared)

    use_event_state = bool(model_cfg.get("branches", {}).get("event_state", True))
    use_company_profile = bool(model_cfg.get("branches", {}).get("company_profile", False))
    if use_event_state and ("state_vector" not in prepared.columns and not event_scalar_columns):
        raise BaselineModelError("Event-state branch requested, but no event-state features exist in the panel.")

    train_df = filter_rows_with_complete_targets(prepared[prepared["date"].isin(train_dates)].copy(), target_columns=target_columns)
    validation_df = filter_rows_with_complete_targets(prepared[prepared["date"].isin(validation_dates)].copy(), target_columns=target_columns)
    test_df = filter_rows_with_complete_targets(prepared[prepared["date"].isin(test_dates)].copy(), target_columns=target_columns)

    if train_df.empty:
        raise ValueError("Training fold has no rows after target filtering.")

    market_feature_columns = _filter_all_nan_feature_columns(
        train_df,
        market_feature_columns,
        frame_name="multimodal market branch",
    )
    company_feature_columns = _filter_all_nan_feature_columns(
        train_df,
        company_feature_columns,
        frame_name="multimodal company branch",
        allow_empty=True,
    )
    event_scalar_columns = _filter_all_nan_feature_columns(
        train_df,
        event_scalar_columns,
        frame_name="multimodal event scalar branch",
        allow_empty=True,
    )

    seed_everything(seed, deterministic_torch=bool(training_cfg.get("deterministic_torch", False)))
    torch = importlib.import_module("torch")
    device = str(training_cfg.get("device", "cpu"))

    train_dataset = MultimodalPanelDataset(
        train_df,
        market_feature_columns=market_feature_columns,
        target_columns=target_columns,
        event_scalar_columns=event_scalar_columns,
        event_vector_column="state_vector" if use_event_state else None,
        company_feature_columns=company_feature_columns if use_company_profile else [],
    )
    validation_dataset = (
        MultimodalPanelDataset(
            validation_df,
            market_feature_columns=market_feature_columns,
            target_columns=target_columns,
            event_scalar_columns=event_scalar_columns,
            event_vector_column="state_vector" if use_event_state else None,
            company_feature_columns=company_feature_columns if use_company_profile else [],
        )
        if not validation_df.empty
        else None
    )
    test_dataset = (
        MultimodalPanelDataset(
            test_df,
            market_feature_columns=market_feature_columns,
            target_columns=target_columns,
            event_scalar_columns=event_scalar_columns,
            event_vector_column="state_vector" if use_event_state else None,
            company_feature_columns=company_feature_columns if use_company_profile else [],
        )
        if not test_df.empty
        else None
    )

    scalers = _fit_multimodal_feature_scalers(train_dataset)
    _apply_multimodal_feature_scalers(train_dataset, scalers)
    if validation_dataset is not None:
        _apply_multimodal_feature_scalers(validation_dataset, scalers)
    if test_dataset is not None:
        _apply_multimodal_feature_scalers(test_dataset, scalers)

    event_input_dim = 0 if train_dataset.event_state_features is None else int(train_dataset.event_state_features.shape[1])
    company_input_dim = 0 if train_dataset.company_features is None else int(train_dataset.company_features.shape[1])
    model = build_multimodal_regressor(
        market_input_dim=len(market_feature_columns),
        output_dim=len(target_columns),
        event_state_input_dim=event_input_dim,
        company_input_dim=company_input_dim,
        market_hidden_dim=int(model_cfg.get("market_hidden_dim", 64)),
        event_hidden_dim=int(model_cfg.get("event_hidden_dim", 32)),
        company_hidden_dim=int(model_cfg.get("company_hidden_dim", 16)),
        fusion_hidden_dim=int(model_cfg.get("fusion_hidden_dim", 64)),
        dropout=float(model_cfg.get("dropout", 0.0)),
        use_event_state=use_event_state,
        use_company_profile=use_company_profile,
    )
    model.to(device)

    optimizer_name = str(training_cfg.get("optimizer", "adamw")).lower()
    learning_rate = float(training_cfg.get("learning_rate", 1e-3))
    weight_decay = float(training_cfg.get("weight_decay", 1e-4))
    optimizer = _build_optimizer(torch, model.parameters(), optimizer_name, learning_rate, weight_decay)

    train_loader = create_multimodal_dataloader(
        train_dataset,
        batch_size=int(training_cfg.get("train_batch_size", 256)),
        shuffle=True,
        num_workers=int(training_cfg.get("num_workers", 0)),
        pin_memory=bool(training_cfg.get("pin_memory", False)),
    )
    validation_loader = (
        create_multimodal_dataloader(
            validation_dataset,
            batch_size=int(training_cfg.get("eval_batch_size", 512)),
            shuffle=False,
            num_workers=0,
            pin_memory=False,
        )
        if validation_dataset is not None
        else None
    )

    max_epochs = int(training_cfg.get("max_epochs", 10))
    patience = int(training_cfg.get("early_stopping_patience", 5))
    best_state = None
    best_loss = float("inf")
    epochs_without_improvement = 0
    loss_name = str(training_cfg.get("loss_name", "mse"))

    for _epoch in range(max_epochs):
        model.train()
        for batch in train_loader:
            optimizer.zero_grad()
            predictions = model(
                batch.market_features.to(device),
                event_state_features=None if batch.event_state_features is None else batch.event_state_features.to(device),
                company_features=None if batch.company_features is None else batch.company_features.to(device),
                event_state_mask=None if batch.event_state_mask is None else batch.event_state_mask.to(device),
                company_mask=None if batch.company_mask is None else batch.company_mask.to(device),
            )
            loss = compute_torch_regression_loss(predictions, batch.targets.to(device), loss_name=loss_name)
            loss.backward()
            optimizer.step()

        validation_loss = _evaluate_multimodal_torch_loss(
            model,
            validation_loader if validation_loader is not None else train_loader,
            device=device,
            loss_name=loss_name,
        )
        if validation_loss < best_loss:
            best_loss = validation_loss
            best_state = {key: value.detach().cpu() for key, value in model.state_dict().items()}
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    checkpoint_path = run_path / "checkpoints" / f"split_{split_id}__multimodal_event_state.pt"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_name": "multimodal_event_state",
            "state_dict": model.state_dict(),
            "market_feature_columns": market_feature_columns,
            "target_columns": target_columns,
            "event_scalar_columns": event_scalar_columns,
            "company_feature_columns": company_feature_columns,
            "use_event_state": use_event_state,
            "use_company_profile": use_company_profile,
            "seed": seed,
            "model_config": model_cfg,
        },
        checkpoint_path,
    )

    frames: list[pd.DataFrame] = []
    frames.append(
        predict_torch_multimodal_model(
            model,
            train_dataset,
            target_columns=target_columns,
            model_name="multimodal_event_state",
            split_id=split_id,
            partition="train",
            device=device,
            batch_size=int(training_cfg.get("eval_batch_size", 512)),
        )
    )
    if validation_dataset is not None:
        frames.append(
            predict_torch_multimodal_model(
                model,
                validation_dataset,
                target_columns=target_columns,
                model_name="multimodal_event_state",
                split_id=split_id,
                partition="validation",
                device=device,
                batch_size=int(training_cfg.get("eval_batch_size", 512)),
            )
        )
    if test_dataset is not None:
        frames.append(
            predict_torch_multimodal_model(
                model,
                test_dataset,
                target_columns=target_columns,
                model_name="multimodal_event_state",
                split_id=split_id,
                partition="test",
                device=device,
                batch_size=int(training_cfg.get("eval_batch_size", 512)),
            )
        )
    predictions = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    metrics = _compute_fold_metrics(predictions, prepared, target_columns=target_columns)
    predictions_path = run_path / "predictions" / f"split_{split_id}__multimodal_event_state.parquet"
    metrics_path = run_path / "metrics" / f"split_{split_id}__multimodal_event_state.json"
    write_parquet(predictions, predictions_path, index=False)
    write_json(metrics, metrics_path)

    metadata_path = run_path / "run_metadata" / f"split_{split_id}__multimodal_event_state.json"
    save_run_metadata(
        build_run_metadata(
            run_id=f"split_{split_id}__multimodal_event_state",
            random_seed=seed,
            deterministic_torch=bool(training_cfg.get("deterministic_torch", False)),
            extra={
                "market_feature_columns": market_feature_columns,
                "target_columns": target_columns,
                "event_scalar_columns": event_scalar_columns,
                "company_feature_columns": company_feature_columns,
                "train_row_count": len(train_df),
                "validation_row_count": len(validation_df),
                "test_row_count": len(test_df),
            },
        ),
        metadata_path,
    )

    return MultimodalFoldResult(
        model_name="multimodal_event_state",
        split_id=split_id,
        checkpoint_path=checkpoint_path,
        predictions_path=predictions_path,
        metrics_path=metrics_path,
        train_row_count=int(len(train_df)),
        validation_row_count=int(len(validation_df)),
        test_row_count=int(len(test_df)),
    )


def _evaluate_torch_loss(model: Any, dataloader: Any, *, device: str, loss_name: str) -> float:
    torch = importlib.import_module("torch")
    model.eval()
    losses: list[float] = []
    with torch.no_grad():
        for batch in dataloader:
            predictions = model(batch.features.to(device))
            loss = compute_torch_regression_loss(predictions, batch.targets.to(device), loss_name=loss_name)
            losses.append(float(loss.detach().cpu()))
    return float(np.mean(losses)) if losses else float("inf")


def _evaluate_multimodal_torch_loss(model: Any, dataloader: Any, *, device: str, loss_name: str) -> float:
    torch = importlib.import_module("torch")
    model.eval()
    losses: list[float] = []
    with torch.no_grad():
        for batch in dataloader:
            predictions = model(
                batch.market_features.to(device),
                event_state_features=None if batch.event_state_features is None else batch.event_state_features.to(device),
                company_features=None if batch.company_features is None else batch.company_features.to(device),
                event_state_mask=None if batch.event_state_mask is None else batch.event_state_mask.to(device),
                company_mask=None if batch.company_mask is None else batch.company_mask.to(device),
            )
            loss = compute_torch_regression_loss(predictions, batch.targets.to(device), loss_name=loss_name)
            losses.append(float(loss.detach().cpu()))
    return float(np.mean(losses)) if losses else float("inf")


def _fit_multimodal_feature_scalers(dataset: MultimodalPanelDataset) -> dict[str, tuple[np.ndarray, np.ndarray] | None]:
    scalers: dict[str, tuple[np.ndarray, np.ndarray] | None] = {
        "market": _fit_impute_standard_scaler(dataset.market_features),
        "event_state": _fit_impute_standard_scaler(dataset.event_state_features),
        "company": _fit_impute_standard_scaler(dataset.company_features),
    }
    return scalers


def _apply_multimodal_feature_scalers(
    dataset: MultimodalPanelDataset,
    scalers: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray] | None],
) -> None:
    market_scaler = scalers.get("market")
    if market_scaler is not None:
        dataset.market_features = _apply_impute_standard_scaler(dataset.market_features, market_scaler)
    event_scaler = scalers.get("event_state")
    if event_scaler is not None and dataset.event_state_features is not None:
        dataset.event_state_features = _apply_impute_standard_scaler(dataset.event_state_features, event_scaler)
    company_scaler = scalers.get("company")
    if company_scaler is not None and dataset.company_features is not None:
        dataset.company_features = _apply_impute_standard_scaler(dataset.company_features, company_scaler)


def _fit_impute_standard_scaler(values: np.ndarray | None) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    if values is None:
        return None
    medians = np.nanmedian(values, axis=0)
    medians = np.where(np.isnan(medians), 0.0, medians)
    imputed = np.where(np.isnan(values), medians, values)
    mean = imputed.mean(axis=0)
    std = imputed.std(axis=0)
    std = np.where(std == 0.0, 1.0, std)
    return medians.astype(np.float32), mean.astype(np.float32), std.astype(np.float32)


def _apply_impute_standard_scaler(
    values: np.ndarray,
    scaler: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> np.ndarray:
    medians, mean, std = scaler
    imputed = np.where(np.isnan(values), medians, values)
    return ((imputed - mean) / std).astype(np.float32)


def _build_optimizer(torch_module: Any, parameters: Any, optimizer_name: str, learning_rate: float, weight_decay: float) -> Any:
    optimizer_name = optimizer_name.lower()
    if optimizer_name == "adamw":
        return torch_module.optim.AdamW(parameters, lr=learning_rate, weight_decay=weight_decay)
    if optimizer_name == "adam":
        return torch_module.optim.Adam(parameters, lr=learning_rate, weight_decay=weight_decay)
    raise BaselineModelError(f"Unsupported optimizer '{optimizer_name}' for market_mlp.")


def _filter_all_nan_feature_columns(
    frame: pd.DataFrame,
    columns: list[str],
    *,
    frame_name: str,
    allow_empty: bool = False,
) -> list[str]:
    filtered = [column for column in columns if column in frame.columns and not frame[column].isna().all()]
    if not filtered and columns and not allow_empty:
        raise ValueError(f"All selected feature columns for {frame_name} are entirely NaN in the training fold.")
    return filtered


def _compute_fold_metrics(predictions: pd.DataFrame, panel: pd.DataFrame, *, target_columns: list[str]) -> dict[str, Any]:
    if predictions.empty:
        return {"row_count": 0, "metrics": {}}

    joined = predictions.merge(panel[["ticker", "date", *target_columns]], how="left", on=["ticker", "date"])
    metrics: dict[str, Any] = {}
    for partition, partition_df in joined.groupby("partition", sort=True):
        partition_metrics: dict[str, Any] = {}
        for target_column in target_columns:
            pred_column = f"pred_{target_column}"
            valid = partition_df[[target_column, pred_column]].dropna()
            if valid.empty:
                continue
            y_true = valid[target_column].to_numpy(dtype=float)
            y_pred = valid[pred_column].to_numpy(dtype=float)
            partition_metrics[target_column] = {
                "mae": float(np.mean(np.abs(y_pred - y_true))),
                "rmse": float(np.sqrt(np.mean((y_pred - y_true) ** 2))),
                "r2": _safe_r2(y_true, y_pred),
                "weighted_loss": compute_regression_loss(y_pred, y_true, loss_name="mse"),
            }
        metrics[partition] = partition_metrics
    return {"row_count": int(len(joined)), "metrics": metrics}


def _safe_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    sklearn_metrics = importlib.import_module("sklearn.metrics")
    return float(sklearn_metrics.r2_score(y_true, y_pred))
