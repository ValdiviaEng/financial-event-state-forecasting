"""Reproducibility helpers for seeding and run metadata capture."""

from __future__ import annotations

from datetime import UTC, datetime
import importlib
import importlib.metadata
import logging
import os
import platform
from pathlib import Path
import random
import sys
from typing import Any, Iterable


logger = logging.getLogger(__name__)

DEFAULT_TRACKED_PACKAGES = (
    "numpy",
    "pandas",
    "polars",
    "pyarrow",
    "duckdb",
    "requests",
    "pydantic",
    "torch",
    "transformers",
    "sentence-transformers",
)


def seed_everything(seed: int, *, deterministic_torch: bool = False) -> None:
    """Seed Python, NumPy, and Torch when available."""

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)

    numpy_module = _optional_import("numpy")
    if numpy_module is not None:
        numpy_module.random.seed(seed)

    torch_module = _optional_import("torch")
    if torch_module is not None:
        torch_module.manual_seed(seed)
        if torch_module.cuda.is_available():
            torch_module.cuda.manual_seed_all(seed)
        if deterministic_torch:
            if hasattr(torch_module, "use_deterministic_algorithms"):
                torch_module.use_deterministic_algorithms(True, warn_only=True)
            if hasattr(torch_module.backends, "cudnn"):
                torch_module.backends.cudnn.deterministic = True
                torch_module.backends.cudnn.benchmark = False

    logger.info("Seeded runtime with seed=%s deterministic_torch=%s", seed, deterministic_torch)


def collect_runtime_metadata(
    *,
    tracked_packages: Iterable[str] = DEFAULT_TRACKED_PACKAGES,
) -> dict[str, Any]:
    """Collect a reproducibility-friendly runtime summary."""

    return {
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cwd": os.getcwd(),
        "environment": {
            "pythonhashseed": os.getenv("PYTHONHASHSEED"),
            "cuda_visible_devices": os.getenv("CUDA_VISIBLE_DEVICES"),
        },
        "packages": collect_package_versions(tracked_packages),
        "torch": collect_torch_metadata(),
    }


def collect_package_versions(package_names: Iterable[str]) -> dict[str, str | None]:
    """Return installed package versions for a selected set of package names."""

    versions: dict[str, str | None] = {}
    for package_name in package_names:
        try:
            versions[package_name] = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            versions[package_name] = None
    return versions


def collect_torch_metadata() -> dict[str, Any] | None:
    """Return Torch-specific metadata when Torch is available."""

    torch_module = _optional_import("torch")
    if torch_module is None:
        return None

    metadata: dict[str, Any] = {
        "version": getattr(torch_module, "__version__", None),
        "cuda_available": torch_module.cuda.is_available(),
        "mps_available": getattr(getattr(torch_module, "backends", None), "mps", None)
        is not None
        and torch_module.backends.mps.is_available(),
    }

    if torch_module.cuda.is_available():
        metadata.update(
            {
                "cuda_device_count": torch_module.cuda.device_count(),
                "cuda_version": getattr(torch_module.version, "cuda", None),
                "cudnn_version": torch_module.backends.cudnn.version()
                if hasattr(torch_module.backends, "cudnn")
                else None,
                "device_names": [
                    torch_module.cuda.get_device_name(index)
                    for index in range(torch_module.cuda.device_count())
                ],
            }
        )

    return metadata


def build_run_metadata(
    *,
    run_id: str | None = None,
    random_seed: int | None = None,
    deterministic_torch: bool = False,
    tracked_packages: Iterable[str] = DEFAULT_TRACKED_PACKAGES,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build run metadata for persistence next to run outputs."""

    metadata = collect_runtime_metadata(tracked_packages=tracked_packages)
    metadata["run_id"] = run_id
    metadata["random_seed"] = random_seed
    metadata["deterministic_torch"] = deterministic_torch
    if extra:
        metadata["extra"] = extra
    return metadata


def save_run_metadata(metadata: dict[str, Any], output_path: str | os.PathLike[str]) -> None:
    """Persist run metadata as JSON using the shared I/O helpers."""

    from src.utils.io_utils import write_json

    write_json(metadata, Path(output_path), indent=2, sort_keys=True, atomic=True)


def _optional_import(module_name: str) -> Any | None:
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None
