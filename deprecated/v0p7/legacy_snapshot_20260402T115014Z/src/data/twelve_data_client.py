"""Thin client for Twelve Data market-history access."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, date
import logging
import time
from typing import Any

import requests

from src.utils.config_loader import ResolvedSettings


logger = logging.getLogger(__name__)


class TwelveDataClientError(RuntimeError):
    """Raised when Twelve Data requests or payloads are invalid."""


@dataclass(frozen=True, slots=True)
class TwelveDataRequestMetadata:
    """Request metadata useful for ledgers and debugging."""

    endpoint: str
    symbol: str
    requested_at_utc: datetime
    request_url: str
    request_params: dict[str, Any]
    response_status: int
    response_headers: dict[str, str]
    is_empty: bool = False

    def as_ledger_record(self, *, raw_path: str, success: bool = True, error_message: str | None = None) -> dict[str, Any]:
        """Convert request metadata into a ledger-friendly dictionary."""

        return {
            "request_id": f"{self.endpoint}:{self.symbol}:{self.requested_at_utc.isoformat()}",
            "provider": "twelve_data",
            "endpoint": self.endpoint,
            "ticker": self.symbol,
            "requested_at_utc": self.requested_at_utc,
            "response_status": self.response_status,
            "success": success,
            "raw_path": raw_path,
            "interval": self.request_params.get("interval"),
            "outputsize": self.request_params.get("outputsize"),
            "start_date": self.request_params.get("start_date"),
            "end_date": self.request_params.get("end_date"),
            "credits_used": self.response_headers.get("api-credits-used"),
            "credits_left": self.response_headers.get("api-credits-left"),
            "request_url": self.request_url,
            "error_message": error_message,
        }


class TwelveDataClient:
    """Client for the Twelve Data REST API.

    The first implemented goal of this class is deliberately narrow:
    daily OHLCV downloads via the `time_series` endpoint with safe request
    defaults and canonical parsing helpers.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.twelvedata.com",
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
    def from_settings(cls, settings: ResolvedSettings) -> "TwelveDataClient":
        """Build a client from validated project settings."""

        source_cfg = settings.data_sources_config.get("market_data", {})
        return cls(
            api_key=settings.environment.twelve_data_api_key.get_secret_value(),
            base_url=source_cfg.get("base_url", "https://api.twelvedata.com"),
            timeout_seconds=source_cfg.get("timeout_seconds", 30),
            max_retries=source_cfg.get("max_retries", 3),
            backoff_seconds=source_cfg.get("backoff_seconds", 1.0),
        )

    def get_time_series(
        self,
        symbol: str,
        interval: str = "1day",
        outputsize: int = 5000,
        start_date: str | None = None,
        end_date: str | None = None,
        order: str = "ASC",
        timezone: str = "UTC",
    ) -> tuple[dict[str, Any], TwelveDataRequestMetadata]:
        """Fetch raw time-series payload for a single symbol."""

        normalized_symbol = self.normalize_symbol(symbol)
        params: dict[str, Any] = {
            "symbol": normalized_symbol,
            "interval": interval,
            "outputsize": outputsize,
            "order": order,
            "timezone": timezone,
            "apikey": self.api_key,
        }
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date

        payload, response, requested_at = self._request_json(endpoint="time_series", params=params)

        metadata = TwelveDataRequestMetadata(
            endpoint="time_series",
            symbol=normalized_symbol,
            requested_at_utc=requested_at,
            request_url=response.url,
            request_params={key: value for key, value in params.items() if key != "apikey"},
            response_status=response.status_code,
            response_headers=dict(response.headers),
            is_empty=self.is_empty_time_series_payload(payload),
        )
        return payload, metadata

    def parse_time_series(
        self,
        payload: dict[str, Any],
        symbol: str,
        source_name: str = "twelve_data",
    ) -> list[dict[str, Any]]:
        """Convert a raw Twelve Data time-series payload into canonical rows."""

        values = self.validate_time_series_payload(payload)
        if not values:
            return []

        rows: list[dict[str, Any]] = []
        normalized_symbol = self.normalize_symbol(symbol)
        for item in values:
            if not isinstance(item, dict):
                raise TwelveDataClientError("Expected each Twelve Data 'values' entry to be a mapping.")

            for required_field in ("open", "high", "low", "close"):
                if item.get(required_field) in (None, ""):
                    raise TwelveDataClientError(
                        f"Twelve Data row is missing required price field '{required_field}'."
                    )

            rows.append(
                {
                    "date": self._parse_date(item.get("datetime") or item.get("date")),
                    "ticker": normalized_symbol,
                    "open": self._to_float(item.get("open")),
                    "high": self._to_float(item.get("high")),
                    "low": self._to_float(item.get("low")),
                    "close": self._to_float(item.get("close")),
                    "volume": self._to_int(item.get("volume")),
                    "source": source_name,
                }
            )

        return sorted(rows, key=lambda row: row["date"])

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """Normalize a ticker symbol without altering dot tickers."""

        normalized = symbol.strip().upper()
        if not normalized:
            raise TwelveDataClientError("Ticker symbol must be non-empty.")
        return normalized

    @staticmethod
    def is_empty_time_series_payload(payload: dict[str, Any]) -> bool:
        values = payload.get("values")
        return isinstance(values, list) and len(values) == 0

    def validate_time_series_payload(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Validate and return the `values` list from a time-series payload."""

        if not isinstance(payload, dict):
            raise TwelveDataClientError("Expected Twelve Data payload to be a mapping.")

        values = payload.get("values")
        if values is None:
            if payload.get("status") == "ok":
                return []
            message = payload.get("message") or payload.get("code") or "missing values"
            raise TwelveDataClientError(f"Twelve Data payload did not contain 'values': {message}")
        if not isinstance(values, list):
            raise TwelveDataClientError("Expected Twelve Data payload to contain a list in 'values'.")
        return values

    def _request_json(
        self,
        endpoint: str,
        params: dict[str, Any],
    ) -> tuple[dict[str, Any], requests.Response, datetime]:
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

                if isinstance(payload, dict) and (
                    payload.get("status") == "error" or payload.get("code") not in (None, 200)
                ):
                    raise TwelveDataClientError(
                        f"Twelve Data returned provider error for endpoint '{endpoint}': "
                        f"{payload.get('message', payload.get('code', 'unknown error'))}"
                    )

                if not isinstance(payload, dict):
                    raise TwelveDataClientError("Expected Twelve Data response payload to be a mapping.")

                return payload, response, requested_at
            except (requests.RequestException, ValueError, TwelveDataClientError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                self._sleep_before_retry(attempt, reason=exc.__class__.__name__)

        raise TwelveDataClientError(f"Twelve Data request failed after retries: {last_error}")

    def _sleep_before_retry(self, attempt: int, reason: str) -> None:
        delay = self.backoff_seconds * (2**attempt)
        logger.warning("Retrying Twelve Data request after %s seconds due to %s", delay, reason)
        time.sleep(delay)

    @staticmethod
    def _parse_date(value: Any) -> date:
        if value in (None, ""):
            raise TwelveDataClientError("Missing date field in Twelve Data time-series row.")
        return date.fromisoformat(str(value)[:10])

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value in (None, ""):
            return None
        return float(value)

    @staticmethod
    def _to_int(value: Any) -> int | None:
        if value in (None, ""):
            return None
        return int(float(value))
