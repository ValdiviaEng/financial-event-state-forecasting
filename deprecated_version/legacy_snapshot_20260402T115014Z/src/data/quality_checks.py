"""Data-quality checks for normalized market-price rows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True, slots=True)
class QualityIssue:
    """One data-quality issue discovered during validation."""

    severity: str
    code: str
    message: str
    ticker: str | None = None
    row_index: int | None = None
    date: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "ticker": self.ticker,
            "row_index": self.row_index,
            "date": self.date,
        }


def run_price_quality_checks(
    rows: list[dict[str, Any]],
    *,
    expected_ticker: str | None = None,
    spike_return_threshold: float = 0.5,
) -> dict[str, Any]:
    """Run a set of early quality checks on canonical daily price rows."""

    issues: list[QualityIssue] = []
    sorted_rows = sorted(rows, key=lambda row: (_coerce_date(row["date"]), row.get("ticker", "")))
    seen_keys: set[tuple[str, date]] = set()

    for index, row in enumerate(sorted_rows):
        ticker = row.get("ticker")
        row_date = _coerce_date(row["date"]).isoformat() if row.get("date") is not None else None

        if expected_ticker is not None and ticker != expected_ticker:
            issues.append(
                QualityIssue(
                    severity="error",
                    code="unexpected_ticker",
                    message=f"Expected ticker '{expected_ticker}' but found '{ticker}'.",
                    ticker=ticker,
                    row_index=index,
                    date=row_date,
                )
            )

        key = (str(ticker), _coerce_date(row["date"]))
        if key in seen_keys:
            issues.append(
                QualityIssue(
                    severity="error",
                    code="duplicate_key",
                    message="Duplicate `(ticker, date)` row detected.",
                    ticker=str(ticker),
                    row_index=index,
                    date=row_date,
                )
            )
        seen_keys.add(key)

        for field_name in ("open", "high", "low", "close"):
            if row.get(field_name) in (None, ""):
                issues.append(
                    QualityIssue(
                        severity="error",
                        code="missing_price_value",
                        message=f"Missing required price field '{field_name}'.",
                        ticker=str(ticker),
                        row_index=index,
                        date=row_date,
                    )
                )

        open_value = row.get("open")
        if open_value is not None and float(open_value) <= 0:
            issues.append(
                QualityIssue(
                    severity="error",
                    code="non_positive_open",
                    message="Open price must be positive.",
                    ticker=str(ticker),
                    row_index=index,
                    date=row_date,
                )
            )

        high_value = row.get("high")
        low_value = row.get("low")
        if high_value is not None and low_value is not None and float(high_value) < float(low_value):
            issues.append(
                QualityIssue(
                    severity="error",
                    code="high_below_low",
                    message="High price is below low price.",
                    ticker=str(ticker),
                    row_index=index,
                    date=row_date,
                )
            )

        volume_value = row.get("volume")
        if volume_value is not None and int(volume_value) < 0:
            issues.append(
                QualityIssue(
                    severity="error",
                    code="negative_volume",
                    message="Volume must not be negative.",
                    ticker=str(ticker),
                    row_index=index,
                    date=row_date,
                )
            )

    issues.extend(_detect_sorting_issues(rows))
    issues.extend(_detect_gap_issues(sorted_rows))
    issues.extend(_detect_return_spikes(sorted_rows, spike_return_threshold=spike_return_threshold))

    coverage = build_price_coverage_summary(sorted_rows)
    return {
        "row_count": len(sorted_rows),
        "coverage": coverage,
        "issues": [issue.as_dict() for issue in issues],
        "has_blocking_issues": any(issue.severity == "error" for issue in issues),
    }


def build_price_coverage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a small coverage summary from canonical price rows."""

    if not rows:
        return {
            "ticker_count": 0,
            "tickers": [],
            "start_date": None,
            "end_date": None,
            "row_count": 0,
        }

    dates = sorted(_coerce_date(row["date"]) for row in rows)
    tickers = sorted({str(row.get("ticker")) for row in rows if row.get("ticker") is not None})
    return {
        "ticker_count": len(tickers),
        "tickers": tickers,
        "start_date": dates[0].isoformat(),
        "end_date": dates[-1].isoformat(),
        "row_count": len(rows),
    }


def build_news_quality_report(
    *,
    ticker: str,
    raw_article_count: int,
    deduplicated_articles: list[dict[str, Any]],
    duplicate_url_count: int,
    duplicate_fallback_count: int,
) -> dict[str, Any]:
    """Build a quality report for normalized company-news articles."""

    article_dates = sorted(
        {
            article.get("published_date_utc").isoformat()
            for article in deduplicated_articles
            if article.get("published_date_utc") is not None
        }
    )
    missing_summary_count = sum(1 for article in deduplicated_articles if article.get("summary") is None)
    missing_url_count = sum(1 for article in deduplicated_articles if article.get("url") is None)

    return {
        "ticker": ticker,
        "raw_article_count": raw_article_count,
        "deduplicated_article_count": len(deduplicated_articles),
        "duplicate_url_count": duplicate_url_count,
        "duplicate_fallback_count": duplicate_fallback_count,
        "missing_summary_count": missing_summary_count,
        "missing_url_count": missing_url_count,
        "date_span": {
            "start_date": article_dates[0] if article_dates else None,
            "end_date": article_dates[-1] if article_dates else None,
        },
    }


def assert_no_blocking_issues(report: dict[str, Any]) -> None:
    """Raise an error if a quality report contains blocking issues."""

    if report.get("has_blocking_issues"):
        issues = report.get("issues", [])
        summary = "; ".join(issue.get("message", "unknown issue") for issue in issues[:5])
        raise ValueError(f"Blocking data-quality issues detected: {summary}")


def _detect_sorting_issues(rows: list[dict[str, Any]]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    observed_dates = [_coerce_date(row["date"]) for row in rows]
    if observed_dates != sorted(observed_dates):
        issues.append(
            QualityIssue(
                severity="warning",
                code="rows_not_sorted",
                message="Input rows were not sorted by date prior to validation.",
            )
        )
    return issues


def _detect_gap_issues(rows: list[dict[str, Any]]) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    if len(rows) < 2:
        return issues

    grouped: dict[str, list[date]] = {}
    for row in rows:
        grouped.setdefault(str(row["ticker"]), []).append(_coerce_date(row["date"]))

    for ticker, dates in grouped.items():
        sorted_dates = sorted(dates)
        for previous, current in zip(sorted_dates, sorted_dates[1:], strict=False):
            gap_days = (current - previous).days
            if gap_days > 7:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        code="large_gap",
                        message=f"Large date gap detected ({gap_days} days).",
                        ticker=ticker,
                        date=current.isoformat(),
                    )
                )
    return issues


def _detect_return_spikes(rows: list[dict[str, Any]], *, spike_return_threshold: float) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["ticker"]), []).append(row)

    for ticker, ticker_rows in grouped.items():
        ordered = sorted(ticker_rows, key=lambda row: _coerce_date(row["date"]))
        previous_close: float | None = None
        for row in ordered:
            current_close = row.get("close")
            if previous_close not in (None, 0) and current_close not in (None, ""):
                absolute_return = abs((float(current_close) / float(previous_close)) - 1.0)
                if absolute_return > spike_return_threshold:
                    issues.append(
                        QualityIssue(
                            severity="warning",
                            code="suspicious_return_spike",
                            message=f"Suspicious daily return spike detected: {absolute_return:.2%}",
                            ticker=ticker,
                            date=_coerce_date(row["date"]).isoformat(),
                        )
                    )
            if current_close not in (None, ""):
                previous_close = float(current_close)
    return issues


def _coerce_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])
