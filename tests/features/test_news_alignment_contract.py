from __future__ import annotations

import sys
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.features.news_alignment import align_news_as_of_close  # noqa: E402


def test_align_news_rolls_after_close_and_non_trading_days_forward() -> None:
    trading_dates = [date(2024, 4, 1), date(2024, 4, 2), date(2024, 4, 3)]
    records = [
        _article("a1", "20240401T120000"),
        _article("a2", "20240401T180000"),
        _article("a3", "20240330T100000"),
    ]

    aligned, summary = align_news_as_of_close(records, trading_dates)

    by_id = {record.article_id: record for record in aligned}
    assert by_id["a1"].aligned_as_of_date == "2024-04-01"
    assert by_id["a1"].roll_forward_reason == "same_trading_day_at_or_before_close"
    assert by_id["a2"].aligned_as_of_date == "2024-04-02"
    assert by_id["a2"].roll_forward_reason == "after_close_roll_forward"
    assert by_id["a3"].aligned_as_of_date == "2024-04-01"
    assert by_id["a3"].roll_forward_reason == "non_trading_day_roll_forward"
    assert summary["aligned_record_count"] == 3


def _article(article_id: str, published: str) -> dict[str, str]:
    return {"article_id": article_id, "ticker": "AAPL", "time_published": published, "title": article_id, "summary": "", "url": "", "text_hash": article_id}
