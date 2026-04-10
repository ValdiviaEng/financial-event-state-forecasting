"""Thin client for SEC EDGAR metadata access."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
import time
from typing import Any

import requests

from src.utils.config_loader import ResolvedSettings


logger = logging.getLogger(__name__)


class SecEdgarClientError(RuntimeError):
    """Raised when SEC EDGAR requests or payloads are invalid."""


@dataclass(frozen=True, slots=True)
class SecRequestMetadata:
    """Request metadata useful for ledgers and debugging."""

    endpoint: str
    cik: str
    requested_at_utc: datetime
    request_url: str
    response_status: int
    response_headers: dict[str, str]

    def as_ledger_record(self, *, raw_path: str, success: bool = True, error_message: str | None = None) -> dict[str, Any]:
        """Convert request metadata into a ledger-friendly dictionary."""

        return {
            "request_id": f"{self.endpoint}:{self.cik}:{self.requested_at_utc.isoformat()}",
            "provider": "sec_edgar",
            "endpoint": self.endpoint,
            "ticker": None,
            "cik": self.cik,
            "requested_at_utc": self.requested_at_utc,
            "response_status": self.response_status,
            "success": success,
            "raw_path": raw_path,
            "request_url": self.request_url,
            "error_message": error_message,
        }


class SecEdgarClient:
    """Client for SEC EDGAR JSON endpoints focused on submissions metadata."""

    def __init__(
        self,
        user_agent: str,
        base_url: str = "https://data.sec.gov",
        timeout_seconds: int = 30,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
        session: requests.Session | None = None,
    ) -> None:
        if not user_agent.strip():
            raise SecEdgarClientError("SEC user agent must be a non-empty string.")

        self.user_agent = user_agent
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
            }
        )

    @classmethod
    def from_settings(cls, settings: ResolvedSettings) -> "SecEdgarClient":
        """Build a SEC client from validated project settings."""

        source_cfg = settings.data_sources_config.get("company_kb", {})
        return cls(
            user_agent=settings.environment.sec_user_agent,
            base_url=source_cfg.get("base_url", "https://data.sec.gov"),
            timeout_seconds=source_cfg.get("timeout_seconds", 30),
            max_retries=source_cfg.get("max_retries", 3),
            backoff_seconds=source_cfg.get("backoff_seconds", 1.0),
        )

    def get_submissions(self, cik: str | int) -> tuple[dict[str, Any], SecRequestMetadata]:
        """Fetch the submissions JSON document for a given CIK."""

        cik_normalized = self.normalize_cik(cik)
        endpoint = f"submissions/CIK{cik_normalized}.json"
        payload, response, requested_at = self._request_json(endpoint=endpoint)

        if not isinstance(payload, dict):
            raise SecEdgarClientError("Expected SEC submissions payload to be a mapping.")

        metadata = SecRequestMetadata(
            endpoint=endpoint,
            cik=cik_normalized,
            requested_at_utc=requested_at,
            request_url=response.url,
            response_status=response.status_code,
            response_headers=dict(response.headers),
        )
        return payload, metadata

    def extract_company_metadata(
        self,
        payload: dict[str, Any],
        source_name: str = "sec_edgar",
    ) -> dict[str, Any]:
        """Extract a canonical metadata record from SEC submissions JSON."""

        tickers = [self._normalize_optional_string(ticker) for ticker in self._ensure_list(payload.get("tickers"))]
        tickers = [ticker for ticker in tickers if ticker is not None]
        exchanges = [self._normalize_optional_string(exchange) for exchange in self._ensure_list(payload.get("exchanges"))]
        exchanges = [exchange for exchange in exchanges if exchange is not None]
        former_names = self._normalize_former_names(payload.get("formerNames") or [])
        addresses = payload.get("addresses") or {}

        return {
            "cik": self.normalize_cik(payload.get("cik")),
            "ticker": tickers[0] if tickers else None,
            "tickers": tickers,
            "exchanges": exchanges,
            "name_current": self._normalize_optional_string(payload.get("name")),
            "former_names": former_names,
            "sic": self._normalize_optional_string(payload.get("sic")),
            "sic_description": self._normalize_optional_string(payload.get("sicDescription")),
            "state_of_incorporation": self._normalize_optional_string(payload.get("stateOfIncorporation")),
            "fiscal_year_end": self._normalize_optional_string(payload.get("fiscalYearEnd")),
            "entity_type": self._normalize_optional_string(payload.get("entityType")),
            "ein": self._normalize_optional_string(payload.get("ein")),
            "description": self._normalize_optional_string(payload.get("description")),
            "business_address": self._normalize_address(addresses.get("business")),
            "mailing_address": self._normalize_address(addresses.get("mailing")),
            "phone": self._normalize_optional_string(payload.get("phone")),
            "website": self._normalize_optional_string(payload.get("website")),
            "investor_website": self._normalize_optional_string(payload.get("investorWebsite")),
            "source": source_name,
        }

    def extract_ticker_cik_mappings(
        self,
        payload: dict[str, Any],
        source_name: str = "sec_edgar",
    ) -> list[dict[str, Any]]:
        """Extract ticker/CIK/exchange mappings from a submissions payload."""

        cik = self.normalize_cik(payload.get("cik"))
        tickers = [self._normalize_optional_string(ticker) for ticker in self._ensure_list(payload.get("tickers"))]
        tickers = [ticker for ticker in tickers if ticker is not None]
        exchanges = [self._normalize_optional_string(exchange) for exchange in self._ensure_list(payload.get("exchanges"))]
        exchanges = [exchange for exchange in exchanges if exchange is not None]

        mappings: list[dict[str, Any]] = []
        if not tickers:
            return mappings

        if exchanges and len(exchanges) == len(tickers):
            paired = zip(tickers, exchanges, strict=False)
        else:
            paired = ((ticker, exchanges[0] if exchanges else None) for ticker in tickers)

        for ticker, exchange in paired:
            mappings.append(
                {
                    "ticker": ticker,
                    "cik": cik,
                    "exchange": exchange,
                    "source": source_name,
                }
            )
        return mappings

    @staticmethod
    def normalize_cik(cik: str | int | Any) -> str:
        """Normalize a CIK to the SEC-standard zero-padded 10-character string."""

        if cik in (None, ""):
            raise SecEdgarClientError("CIK must be provided.")

        cleaned = str(cik).strip()
        if cleaned.startswith("CIK"):
            cleaned = cleaned[3:]
        if not cleaned.isdigit():
            raise SecEdgarClientError(f"CIK must contain digits only after normalization, got: {cik}")
        return cleaned.zfill(10)

    def _request_json(self, endpoint: str) -> tuple[dict[str, Any], requests.Response, datetime]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            requested_at = datetime.now(UTC)
            try:
                response = self.session.get(url, timeout=self.timeout_seconds)
                payload = response.json()

                if response.status_code in {429, 403} and attempt < self.max_retries:
                    self._sleep_before_retry(attempt, reason=f"http_{response.status_code}")
                    continue

                if response.status_code >= 500 and attempt < self.max_retries:
                    self._sleep_before_retry(attempt, reason="server_error")
                    continue

                response.raise_for_status()

                if not isinstance(payload, dict):
                    raise SecEdgarClientError("Expected SEC response payload to be a mapping.")

                return payload, response, requested_at
            except (requests.RequestException, ValueError, SecEdgarClientError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                self._sleep_before_retry(attempt, reason=exc.__class__.__name__)

        raise SecEdgarClientError(f"SEC EDGAR request failed after retries: {last_error}")

    def _sleep_before_retry(self, attempt: int, reason: str) -> None:
        delay = self.backoff_seconds * (2**attempt)
        logger.warning("Retrying SEC EDGAR request after %s seconds due to %s", delay, reason)
        time.sleep(delay)

    @staticmethod
    def _ensure_list(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @staticmethod
    def _normalize_former_names(items: list[Any]) -> list[dict[str, str | None]]:
        normalized: list[dict[str, str | None]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "name": SecEdgarClient._normalize_optional_string(item.get("name")),
                    "from": SecEdgarClient._normalize_optional_string(item.get("from")),
                    "to": SecEdgarClient._normalize_optional_string(item.get("to")),
                }
            )
        return normalized

    @staticmethod
    def _normalize_address(value: Any) -> dict[str, str | None] | None:
        if not isinstance(value, dict):
            return None
        normalized = {
            "street1": SecEdgarClient._normalize_optional_string(value.get("street1")),
            "street2": SecEdgarClient._normalize_optional_string(value.get("street2")),
            "city": SecEdgarClient._normalize_optional_string(value.get("city")),
            "state_or_country": SecEdgarClient._normalize_optional_string(value.get("stateOrCountry")),
            "state_or_country_description": SecEdgarClient._normalize_optional_string(
                value.get("stateOrCountryDescription")
            ),
            "zip_code": SecEdgarClient._normalize_optional_string(value.get("zipCode")),
        }
        if all(item is None for item in normalized.values()):
            return None
        return normalized

    @staticmethod
    def _normalize_optional_string(value: Any) -> str | None:
        if value in (None, ""):
            return None
        normalized = str(value).strip()
        return normalized or None
