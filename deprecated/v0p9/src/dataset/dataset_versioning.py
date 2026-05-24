"""Stable dataset version and source hashing helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def file_sha256(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def source_digest(paths: Iterable[Path | str], *, root: Path | str | None = None) -> str:
    root_path = Path(root).resolve() if root is not None else None
    payload = []
    for path_value in paths:
        path = Path(path_value)
        path_id = str(path)
        if root_path is not None:
            try:
                path_id = path.resolve().relative_to(root_path).as_posix()
            except ValueError:
                path_id = str(path)
        if path.exists() and path.is_file():
            payload.append({"path": path_id, "sha256": file_sha256(path)})
        else:
            payload.append({"path": path_id, "sha256": None})
    return stable_json_digest(payload)


def build_dataset_version(*, clean_window_id: str, source_hash: str, row_hash: str) -> str:
    return f"phase1_top50__stage2_dataset_v1__{clean_window_id}__src_{source_hash[:12]}__rows_{row_hash[:12]}"
