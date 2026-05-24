"""Thin client for Finnhub company-news access."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
import logging
import time
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests

from src.utils.config_loader import ResolvedSettings


logger = logging.getLogger(__name__)


class FinnhubClientError(RuntimeError):
    """Raised when Finnhub requests or payloads are invalid."""


@dataclass(frozen=True, slots=True)
class FinnhubRequestMetadata:
    """Request metadata useful for ledgers and debugging."""

    endpoint: str
    symbol: str
    requested_at_utc: datetime
    request_url: str
    request_params: dict[str, Any]
    response_status: int
    response_headers: dict[str, str]

    def as_ledger_record(self, *, raw_path: str, success: bool = True, error_message: str | None = None) -> dict[str, Any]:
        """Convert request metadata into a ledger-friendly dictionary."""

        return {
            "request_id": f"{self.endpoint}:{self.symbol}:{self.requested_at_utc.isoformat()}",
            "provider": "finnhub",
            "endpoint": self.endpoint,
            "ticker": self.symbol,
            "requested_at_utc": self.requested_at_utc,
            "response_status": self.response_status,
            "success": success,
            "raw_path": raw_path,
            "date_from": self.request_params.get("from"),
            "date_to": self.request_params.get("to"),
            "request_url": self.request_url,
            "error_message": error_message,
        }


class FinnhubClient:
    """Client for Finnhub company-news retrieval."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://finnhub.io/api/v1",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.session = session or requests.Session()

    @classmethod
    def from_settings(cls, settings: ResolvedSettings) -> "FinnhubClient":
        """Build a Finnhub client from validated project settings."""

        source_cfg = settings.data_sources_config.get("news_data", {})
        return cls(
            api_key=settings.environment.finnhub_api_key.get_secret_value(),
            base_url=source_cfg.get("base_url", "https://finnhub.io/api/v1"),
            timeout_seconds=source_cfg.get("timeout_seconds", 30),
            max_retries=source_cfg.get("max_retries", 3),
            backoff_seconds=source_cfg.get("backoff_seconds", 1.0),
        )

    def get_company_news(
        self,
        symbol: str,
        date_from: str,
        date_to: str,
    ) -> tuple[list[dict[str, Any]], FinnhubRequestMetadata]:
        """Fetch raw Finnhub company-news items for a symbol and date range."""

        normalized_symbol = self.normalize_symbol(symbol)
        params = {
            "symbol": normalized_symbol,
            "from": date_from,
            "to": date_to,
            "token": self.api_key,
        }

        payload, response, requested_at = self._request_json(endpoint="company-news", params=params)
        if not isinstance(payload, list):
            raise FinnhubClientError("Expected Finnhub company-news response payload to be a list.")

        metadata = FinnhubRequestMetadata(
            endpoint="company-news",
            symbol=normalized_symbol,
            requested_at_utc=requested_at,
            request_url=response.url,
            request_params={key: value for key, value in params.items() if key != "token"},
            response_status=response.status_code,
            response_headers=dict(response.headers),
        )
        return payload, metadata

    def normalize_company_news(
        self,
        payload: list[dict[str, Any]],
        symbol: str,
        source_name: str = "finnhub",
    ) -> list[dict[str, Any]]:
        """Convert raw Finnhub news items into canonical article records."""

        normalized_symbol = self.normalize_symbol(symbol)
        articles: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                raise FinnhubClientError("Expected each Finnhub company-news item to be a mapping.")

            published_ts = self._parse_unix_timestamp(item.get("datetime"))
            articles.append(
                {
                    "article_id": self._normalize_provider_id(item.get("id")),
                    "ticker": normalized_symbol,
                    "published_ts_utc": published_ts,
                    "published_date_utc": self.published_date_utc(published_ts),
                    "headline": self._normalize_text(item.get("headline")),
                    "summary": self._normalize_text(item.get("summary")),
                    "source": self._normalize_text(item.get("source")),
                    "url": self._normalize_url(item.get("url")),
                    "image": self._normalize_text(item.get("image")),
                    "category": self._normalize_text(item.get("category")),
                    "related": self._normalize_text(item.get("related")),
                    "provider_id": self._normalize_provider_id(item.get("id")),
                    "provider": source_name,
                }
            )

        return sorted(
            articles,
            key=lambda article: article["published_ts_utc"] or datetime.fromtimestamp(0, tz=UTC),
        )

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        normalized = symbol.strip().upper()
        if not normalized:
            raise FinnhubClientError("Ticker symbol must be non-empty.")
        return normalized

    @staticmethod
    def iter_date_chunks(
        start_date: str | date,
        end_date: str | date,
        *,
        chunk_days: int,
    ) -> list[tuple[str, str]]:
        """Return inclusive date chunks for reproducible historical news downloads."""

        if chunk_days <= 0:
            raise FinnhubClientError("chunk_days must be a positive integer.")

        start = start_date if isinstance(start_date, date) else date.fromisoformat(str(start_date))
        end = end_date if isinstance(end_date, date) else date.fromisoformat(str(end_date))
        if end < start:
            raise FinnhubClientError("end_date must be on or after start_date.")

        chunks: list[tuple[str, str]] = []
        current_start = start
        while current_start <= end:
            current_end = min(current_start + timedelta(days=chunk_days - 1), end)
            chunks.append((current_start.isoformat(), current_end.isoformat()))
            current_start = current_end + timedelta(days=1)
        return chunks

    @staticmethod
    def published_date_utc(timestamp: datetime | None) -> date | None:
        if timestamp is None:
            return None
        return timestamp.date()

    def _request_json(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> tuple[Any, requests.Response, datetime]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            requested_at = datetime.now(UTC)
            try:
                response = self.session.get(url, params=params, timeout=self.timeout_seconds)
                payload = response.json()

                if response.status_code == 429 and attempt < self.max_retries:
                    self._sleep_before_retry(attempt, reason="rate_limited")
                    continue

                if response.status_code >= 500 and attempt < self.max_retries:
                    self._sleep_before_retry(attempt, reason="server_error")
                    continue

                response.raise_for_status()

                if isinstance(payload, dict) and payload.get("error"):
                    raise FinnhubClientError(
                        f"Finnhub returned provider error for endpoint '{endpoint}': "
                        f"{payload.get('error')}"
                    )

                return payload, response, requested_at
            except (requests.RequestException, ValueError, FinnhubClientError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                self._sleep_before_retry(attempt, reason=exc.__class__.__name__)

        raise FinnhubClientError(f"Finnhub request failed after retries: {last_error}")

    def _sleep_before_retry(self, attempt: int, reason: str) -> None:
        delay = self.backoff_seconds * (2**attempt)
        logger.warning("Retrying Finnhub request after %s seconds due to %s", delay, reason)
        time.sleep(delay)

    @staticmethod
    def _parse_unix_timestamp(value: Any) -> datetime | None:
        if value in (None, ""):
            return None

        timestamp = int(value)
        if timestamp > 10_000_000_000:
            timestamp = timestamp // 1000
        return datetime.fromtimestamp(timestamp, tz=UTC)

    @staticmethod
    def _normalize_provider_id(value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value)

    @staticmethod
    def _normalize_text(value: Any) -> str | None:
        if value in (None, ""):
            return None
        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    def _normalize_url(value: Any) -> str | None:
        normalized = FinnhubClient._normalize_text(value)
        if normalized is None:
            return None

        split = urlsplit(normalized)
        if not split.scheme or not split.netloc:
            return normalized

        cleaned_path = split.path.rstrip("/") or split.path
        return urlunsplit((split.scheme.lower(), split.netloc.lower(), cleaned_path, split.query, ""))
