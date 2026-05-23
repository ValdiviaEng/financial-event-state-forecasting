"""Explicit no-news state helpers for Stage 3 event-state features."""

from __future__ import annotations

import pandas as pd


class NoNewsStateError(ValueError):
    """Raised when no-news state fields are inconsistent."""


def build_no_news_states(event_state: pd.DataFrame) -> pd.DataFrame:
    """Attach explicit no-news and empty-event-state flags from aligned counts."""

    if "stage3_aligned_news_count" not in event_state.columns:
        raise NoNewsStateError("stage3_aligned_news_count is required")
    output = event_state.copy()
    output["no_news_flag"] = output["stage3_aligned_news_count"] == 0
    output["empty_event_state_flag"] = output["no_news_flag"]
    return output


def validate_no_news_rows_preserved(frame: pd.DataFrame) -> None:
    required = ["stage3_aligned_news_count", "no_news_flag", "empty_event_state_flag"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise NoNewsStateError(f"missing no-news fields: {missing}")
    expected = frame["stage3_aligned_news_count"] == 0
    if not (frame["no_news_flag"] == expected).all():
        raise NoNewsStateError("no_news_flag does not match aligned news counts")
    if not (frame["empty_event_state_flag"] == expected).all():
        raise NoNewsStateError("empty_event_state_flag does not match aligned news counts")
