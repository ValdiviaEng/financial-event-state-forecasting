"""Install the historical v0p9 package layout under its original import name."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def install_v0p9_event_state_package(project_root: Path) -> Path:
    deprecated_src = project_root / "deprecated" / "v0p9" / "src"
    existing = sys.modules.get("event_state_forecasting")
    if existing is not None:
        existing_paths = [Path(value).resolve() for value in getattr(existing, "__path__", [])]
        if deprecated_src.resolve() in existing_paths:
            return deprecated_src
        raise RuntimeError("event_state_forecasting is already imported from a non-v0p9 source tree")

    spec = importlib.util.spec_from_file_location(
        "event_state_forecasting",
        deprecated_src / "__init__.py",
        submodule_search_locations=[str(deprecated_src)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load deprecated package alias from {deprecated_src}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["event_state_forecasting"] = module
    spec.loader.exec_module(module)
    return deprecated_src
