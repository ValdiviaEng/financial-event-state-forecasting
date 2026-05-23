from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.features.no_news_state import build_no_news_states, validate_no_news_rows_preserved  # noqa: E402


def test_no_news_rows_get_explicit_empty_state_flags() -> None:
    frame = pd.DataFrame([{"stage3_aligned_news_count": 0}, {"stage3_aligned_news_count": 2}])

    output = build_no_news_states(frame)
    validate_no_news_rows_preserved(output)

    assert bool(output.loc[0, "no_news_flag"]) is True
    assert bool(output.loc[0, "empty_event_state_flag"]) is True
    assert bool(output.loc[1, "no_news_flag"]) is False
    assert bool(output.loc[1, "empty_event_state_flag"]) is False
