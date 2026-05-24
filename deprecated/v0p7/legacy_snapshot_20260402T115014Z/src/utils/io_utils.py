"""I/O helpers for JSON, Parquet, and manifest persistence."""

from __future__ import annotations

import json
import os
import importlib
import logging
from pathlib import Path
import tempfile
from typing import Any


logger = logging.getLogger(__name__)


def ensure_parent_dir(file_path: str | Path) -> Path:
    """Create the parent directory for a file path if it does not exist."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_json(file_path: str | Path) -> Any:
    """Read a JSON file from disk."""

    path = Path(file_path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(
    payload: Any,
    file_path: str | Path,
    *,
    indent: int = 2,
    sort_keys: bool = True,
    atomic: bool = True,
) -> Path:
    """Write JSON to disk, optionally using atomic replacement."""

    path = ensure_parent_dir(file_path)
    if atomic:
        with _temporary_path(path) as temp_path:
            temp_path.write_text(
                json.dumps(
                    payload,
                    indent=indent,
                    sort_keys=sort_keys,
                    ensure_ascii=True,
                    default=_json_default,
                )
                + "\n",
                encoding="utf-8",
            )
            temp_path.replace(path)
    else:
        path.write_text(
            json.dumps(
                payload,
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=True,
                default=_json_default,
            )
            + "\n",
            encoding="utf-8",
        )

    logger.info("Wrote JSON file to %s", path)
    return path


def read_text(file_path: str | Path) -> str:
    """Read a UTF-8 text file from disk."""

    path = Path(file_path)
    return path.read_text(encoding="utf-8")


def write_text(text: str, file_path: str | Path, *, atomic: bool = True) -> Path:
    """Write UTF-8 text to disk, optionally using atomic replacement."""

    path = ensure_parent_dir(file_path)
    if atomic:
        with _temporary_path(path) as temp_path:
            temp_path.write_text(text, encoding="utf-8")
            temp_path.replace(path)
    else:
        path.write_text(text, encoding="utf-8")

    logger.info("Wrote text file to %s", path)
    return path


def read_parquet(
    file_path: str | Path,
    *,
    columns: list[str] | None = None,
    backend: str = "pandas",
    **kwargs: Any,
) -> Any:
    """Read a Parquet file using the requested backend."""

    path = Path(file_path)
    normalized_backend = backend.strip().lower()

    if normalized_backend == "pandas":
        pd = importlib.import_module("pandas")

        return pd.read_parquet(path, columns=columns, **kwargs)

    if normalized_backend == "pyarrow":
        pq = importlib.import_module("pyarrow.parquet")

        return pq.read_table(path, columns=columns, **kwargs)

    raise ValueError(f"Unsupported parquet backend: {backend}")


def write_parquet(
    data: Any,
    file_path: str | Path,
    *,
    index: bool = False,
    compression: str = "zstd",
    atomic: bool = True,
    **kwargs: Any,
) -> Path:
    """Write a Parquet file using a DataFrame-like object's `to_parquet` method."""

    path = ensure_parent_dir(file_path)
    parquet_kwargs = {"compression": compression, **kwargs}
    parquet_data = _coerce_parquet_input(data)

    if atomic:
        with _temporary_path(path) as temp_path:
            parquet_data.to_parquet(temp_path, index=index, **parquet_kwargs)
            temp_path.replace(path)
    else:
        parquet_data.to_parquet(path, index=index, **parquet_kwargs)

    logger.info("Wrote Parquet file to %s", path)
    return path


def write_manifest(manifest: dict[str, Any], file_path: str | Path) -> Path:
    """Write a manifest as JSON."""

    return write_json(manifest, file_path, indent=2, sort_keys=True, atomic=True)


def read_manifest(file_path: str | Path) -> dict[str, Any]:
    """Read a manifest JSON file."""

    payload = read_json(file_path)
    if not isinstance(payload, dict):
        raise TypeError(f"Manifest at {file_path} must be a JSON object.")
    return payload


def write_checkpoint_metadata(metadata: dict[str, Any], file_path: str | Path) -> Path:
    """Write checkpoint metadata as JSON."""

    return write_json(metadata, file_path, indent=2, sort_keys=True, atomic=True)


def _coerce_parquet_input(data: Any) -> Any:
    if hasattr(data, "to_parquet"):
        return data

    pd = importlib.import_module("pandas")

    return pd.DataFrame(data)


class _temporary_path:
    """Context manager that yields a temporary path in the destination directory."""

    def __init__(self, destination: Path) -> None:
        self.destination = destination
        self.path: Path | None = None

    def __enter__(self) -> Path:
        file_descriptor, temporary_name = tempfile.mkstemp(
            dir=self.destination.parent,
            prefix=f".{self.destination.name}.",
            suffix=".tmp",
        )
        os.close(file_descriptor)
        self.path = Path(temporary_name)
        return self.path

    def __exit__(self, exc_type: Any, exc: Any, exc_tb: Any) -> None:
        if self.path is not None and self.path.exists():
            try:
                self.path.unlink(missing_ok=True)
            except OSError:
                logger.warning("Could not clean up temporary file %s", self.path)


def _json_default(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
