"""Thin client for Alpha Vantage news sentiment access."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
import time
from typing import Any

import requests


logger = logging.getLogger(__name__)


class AlphaVantageClientError(RuntimeError):
    """Raised when Alpha Vantage requests or payloads are invalid."""


class AlphaVantageRateLimitError(AlphaVantageClientError):
    """Raised when Alpha Vantage signals a rate or quota limit."""


@dataclass(frozen=True, slots=True)
class AlphaVantageRequestMetadata:
    """Request metadata useful for ledgers and debugging."""

    endpoint: str
    symbol: str
    requested_at_utc: datetime
    request_url: str
    request_params: dict[str, Any]
    response_status: int
    response_headers: dict[str, str]
    result_count: int

    def as_ledger_record(
        self,
        *,
        raw_path: str,
        success: bool = True,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        return {
            "request_id": f"{self.endpoint}:{self.symbol}:{self.requested_at_utc.isoformat()}",
            "provider": "alphavantage",
            "endpoint": self.endpoint,
            "ticker": self.symbol,
            "requested_at_utc": self.requested_at_utc,
            "response_status": self.response_status,
            "success": success,
            "raw_path": raw_path,
            "time_from": self.request_params.get("time_from"),
            "time_to": self.request_params.get("time_to"),
            "sort": self.request_params.get("sort"),
            "limit": self.request_params.get("limit"),
            "result_count": self.result_count,
            "request_url": self.request_url,
            "error_message": error_message,
        }


class AlphaVantageClient:
    """Client for Alpha Vantage NEWS_SENTIMENT retrieval."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://www.alphavantage.co/query",
        timeout_seconds: int = 60,
        max_retries: int = 2,
        backoff_seconds: float = 20.0,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.session = session or requests.Session()

    def get_news_sentiment(
        self,
        *,
        symbol: str,
        time_from: str,
        time_to: str,
        limit: int = 1000,
        sort: str = "LATEST",
    ) -> tuple[dict[str, Any], AlphaVantageRequestMetadata]:
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol.strip().upper(),
            "time_from": time_from,
            "time_to": time_to,
            "sort": sort,
            "limit": limit,
            "apikey": self.api_key,
        }

        payload, response, requested_at = self._request_json(params=params)
        if not isinstance(payload, dict):
            raise AlphaVantageClientError("Expected Alpha Vantage NEWS_SENTIMENT payload to be a JSON object.")

        if payload.get("Note"):
            raise AlphaVantageRateLimitError(str(payload["Note"]))
        if payload.get("Information"):
            raise AlphaVantageClientError(str(payload["Information"]))
        if payload.get("Error Message"):
            raise AlphaVantageClientError(str(payload["Error Message"]))

        feed = payload.get("feed", [])
        if not isinstance(feed, list):
            raise AlphaVantageClientError("Expected Alpha Vantage NEWS_SENTIMENT 'feed' field to be a list.")

        metadata = AlphaVantageRequestMetadata(
            endpoint="NEWS_SENTIMENT",
            symbol=params["tickers"],
            requested_at_utc=requested_at,
            request_url=response.url,
            request_params={key: value for key, value in params.items() if key != "apikey"},
            response_status=response.status_code,
            response_headers=dict(response.headers),
            result_count=len(feed),
        )
        return payload, metadata

    def _request_json(self, *, params: dict[str, Any]) -> tuple[Any, requests.Response, datetime]:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            requested_at = datetime.now(UTC)
            try:
                response = self.session.get(self.base_url, params=params, timeout=self.timeout_seconds)
                payload = response.json()

                if response.status_code >= 500 and attempt < self.max_retries:
                    self._sleep_before_retry(attempt, reason=f"http_{response.status_code}")
                    continue

                response.raise_for_status()
                return payload, response, requested_at
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                self._sleep_before_retry(attempt, reason=exc.__class__.__name__)

        raise AlphaVantageClientError(f"Alpha Vantage request failed after retries: {last_error}")

    def _sleep_before_retry(self, attempt: int, *, reason: str) -> None:
        delay = self.backoff_seconds * (attempt + 1)
        logger.warning("Retrying Alpha Vantage request after %s seconds due to %s", delay, reason)
        time.sleep(delay)
