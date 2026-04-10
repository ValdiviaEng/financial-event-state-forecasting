"""Path helpers for the project.

This module provides a small, concrete path layer that all future pipeline code
can share. The main goal is to centralize directory naming and resolution so the
rest of the codebase does not hard-code storage locations in multiple places.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ProjectPaths:
    """Resolved absolute paths used across the project."""

    project_root: Path
    data_dir: Path
    data_raw_dir: Path
    data_interim_dir: Path
    data_final_dir: Path
    data_embeddings_dir: Path
    data_kb_dir: Path
    data_manifests_dir: Path
    artifacts_dir: Path
    checkpoints_dir: Path
    figures_dir: Path
    tables_dir: Path
    runs_dir: Path
    reports_dir: Path
    notebooks_dir: Path
    logs_dir: Path

    def as_dict(self) -> dict[str, str]:
        """Return a JSON-serializable mapping of path names to strings."""

        return {key: str(value) for key, value in asdict(self).items()}

    def ensure_base_directories(self) -> None:
        """Create the core directory tree if it does not already exist."""

        for directory in (
            self.data_dir,
            self.data_raw_dir,
            self.data_interim_dir,
            self.data_final_dir,
            self.data_embeddings_dir,
            self.data_kb_dir,
            self.data_manifests_dir,
            self.artifacts_dir,
            self.checkpoints_dir,
            self.figures_dir,
            self.tables_dir,
            self.runs_dir,
            self.reports_dir,
            self.notebooks_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def raw_provider_dir(self, provider_name: str) -> Path:
        """Return the directory used for a raw data provider."""

        return self.data_raw_dir / provider_name

    def run_dir(self, run_id: str) -> Path:
        """Return the directory for a specific run identifier."""

        return self.runs_dir / run_id


def find_project_root(start_path: str | Path | None = None) -> Path:
    """Locate the project root by walking upward from a starting path.

    The root is identified by the presence of `pyproject.toml`.
    """

    start = Path(start_path) if start_path is not None else Path.cwd()
    start = start.resolve()

    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate

    raise FileNotFoundError(
        "Could not locate project root. Expected to find 'pyproject.toml' in the current "
        "directory or one of its parents."
    )


def build_project_paths(
    project_root: str | Path,
    overrides: Mapping[str, str | Path] | None = None,
) -> ProjectPaths:
    """Build a :class:`ProjectPaths` object from a root and optional overrides."""

    root = Path(project_root).resolve()
    values = dict(overrides or {})

    def resolve_path(key: str, default: str) -> Path:
        value = Path(values.get(key, default))
        return value.resolve() if value.is_absolute() else (root / value).resolve()

    return ProjectPaths(
        project_root=root,
        data_dir=resolve_path("data_dir", "data"),
        data_raw_dir=resolve_path("data_raw_dir", "data/raw"),
        data_interim_dir=resolve_path("data_interim_dir", "data/interim"),
        data_final_dir=resolve_path("data_final_dir", "data/final"),
        data_embeddings_dir=resolve_path("data_embeddings_dir", "data/embeddings"),
        data_kb_dir=resolve_path("data_kb_dir", "data/kb"),
        data_manifests_dir=resolve_path("data_manifests_dir", "data/manifests"),
        artifacts_dir=resolve_path("artifacts_dir", "artifacts"),
        checkpoints_dir=resolve_path("checkpoints_dir", "artifacts/checkpoints"),
        figures_dir=resolve_path("figures_dir", "artifacts/figures"),
        tables_dir=resolve_path("tables_dir", "artifacts/tables"),
        runs_dir=resolve_path("runs_dir", "runs"),
        reports_dir=resolve_path("reports_dir", "reports"),
        notebooks_dir=resolve_path("notebooks_dir", "notebooks"),
        logs_dir=resolve_path("logs_dir", "runs/logs"),
    )
