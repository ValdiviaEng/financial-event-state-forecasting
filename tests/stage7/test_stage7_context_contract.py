from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.stage7.context import Stage7ContextError, drop_current_stage6_lockbox_rows, validate_no_current_lockbox_design_rows  # noqa: E402


def test_stage7_context_blocks_current_lockbox_rows_for_design() -> None:
    frame = pd.DataFrame({"as_of_date": ["2025-10-01"]})

    with pytest.raises(Stage7ContextError, match="lockbox rows"):
        validate_no_current_lockbox_design_rows(frame)


def test_stage7_context_allows_development_rows_before_lockbox() -> None:
    frame = pd.DataFrame({"as_of_date": ["2025-09-29"]})

    validate_no_current_lockbox_design_rows(frame)


def test_stage7_context_filters_current_lockbox_from_development_rows() -> None:
    frame = pd.DataFrame({"as_of_date": ["2025-09-29", "2025-10-01", "2026-02-17"]})

    filtered = drop_current_stage6_lockbox_rows(frame)

    assert filtered["as_of_date"].tolist() == ["2025-09-29", "2026-02-17"]
