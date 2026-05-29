"""Active package surface for local artifact-driven forecasting experiments."""

from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEPRECATED_V0P9_SRC = _PROJECT_ROOT / "deprecated" / "v0p9" / "src"
if _DEPRECATED_V0P9_SRC.exists():
    __path__.append(str(_DEPRECATED_V0P9_SRC))

__all__ = ["v1p0"]
