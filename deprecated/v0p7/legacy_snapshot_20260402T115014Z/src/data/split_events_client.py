"""Provider-agnostic split-event normalization interface."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Any

from src.utils.config_loader import ResolvedSettings


class SplitEventsClientError(RuntimeError):
    """Raised when split-event inputs cannot be normalized safely."""


@dataclass(frozen=True, slots=True)
class SplitEvent:
    """Canonical representation of one split event."""

    ticker: str
    split_date: date
    split_factor: float
    source: str
    provider_event_id: str | None = None
    raw_factor_text: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "split_date": self.split_date,
            "split_factor": self.split_factor,
            "source": self.source,
            "provider_event_id": self.provider_event_id,
            "raw_factor_text": self.raw_factor_text,
        }


@dataclass(frozen=True, slots=True)
class SplitProviderSpec:
    """Field conventions used to normalize split records from one provider family."""

    provider_name: str
    date_keys: tuple[str, ...]
    factor_keys: tuple[str, ...] = ()
    ratio_keys: tuple[str, ...] = ()
    numerator_keys: tuple[str, ...] = ()
    denominator_keys: tuple[str, ...] = ()
    event_id_keys: tuple[str, ...] = ()


PROVIDER_SPECS: dict[str, SplitProviderSpec] = {
    "twelve_data": SplitProviderSpec(
        provider_name="twelve_data",
        date_keys=("date", "split_date"),
        factor_keys=("split_factor", "factor"),
        ratio_keys=("ratio", "split_ratio"),
        event_id_keys=("id", "event_id"),
    ),
    "external_or_upgrade_path": SplitProviderSpec(
        provider_name="external_or_upgrade_path",
        date_keys=("date", "split_date", "executionDate"),
        factor_keys=("split_factor", "factor"),
        ratio_keys=("ratio", "split_ratio", "numerator_denominator"),
        numerator_keys=("toFactor", "new_shares", "numerator"),
        denominator_keys=("forFactor", "old_shares", "denominator"),
        event_id_keys=("id", "event_id"),
    ),
}


class SplitEventsClient:
    """Provider-agnostic split-event normalization and validation helper."""

    def __init__(self, provider_name: str) -> None:
        normalized_provider = provider_name.strip().lower()
        if normalized_provider not in PROVIDER_SPECS:
            known = ", ".join(sorted(PROVIDER_SPECS))
            raise SplitEventsClientError(
                f"Unsupported split provider '{provider_name}'. Known providers: {known}"
            )
        self.provider_name = normalized_provider
        self.provider_spec = PROVIDER_SPECS[normalized_provider]

    @classmethod
    def from_settings(cls, settings: ResolvedSettings) -> "SplitEventsClient":
        provider_name = settings.data_sources_config.get("split_events", {}).get(
            "provider", "external_or_upgrade_path"
        )
        return cls(provider_name=provider_name)

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        normalized = symbol.strip().upper()
        if not normalized:
            raise SplitEventsClientError("Ticker symbol must be non-empty.")
        return normalized

    def normalize_events(
        self,
        records: list[dict[str, Any]],
        *,
        symbol: str,
        source_name: str | None = None,
    ) -> list[SplitEvent]:
        """Normalize raw provider records into canonical split events."""

        ticker = self.normalize_symbol(symbol)
        source = source_name or self.provider_name
        events = [self.normalize_event(record, symbol=ticker, source_name=source) for record in records]
        return sorted(events, key=lambda event: event.split_date)

    def normalize_event(
        self,
        record: dict[str, Any],
        *,
        symbol: str,
        source_name: str | None = None,
    ) -> SplitEvent:
        """Normalize one raw split record into canonical form."""

        split_date = self._parse_date_from_record(record, self.provider_spec.date_keys)
        factor_value = self._extract_first(record, self.provider_spec.factor_keys)
        ratio_value = self._extract_first(record, self.provider_spec.ratio_keys)
        numerator_value = self._extract_first(record, self.provider_spec.numerator_keys)
        denominator_value = self._extract_first(record, self.provider_spec.denominator_keys)
        raw_factor_text = str(ratio_value) if ratio_value not in (None, "") else None

        split_factor = self.normalize_split_factor(
            factor=factor_value,
            ratio_text=ratio_value,
            numerator=numerator_value,
            denominator=denominator_value,
        )
        provider_event_id = self._string_or_none(self._extract_first(record, self.provider_spec.event_id_keys))

        return SplitEvent(
            ticker=self.normalize_symbol(symbol),
            split_date=split_date,
            split_factor=split_factor,
            source=source_name or self.provider_name,
            provider_event_id=provider_event_id,
            raw_factor_text=raw_factor_text,
        )

    @staticmethod
    def normalize_split_factor(
        *,
        factor: Any = None,
        ratio_text: Any = None,
        numerator: Any = None,
        denominator: Any = None,
    ) -> float:
        """Normalize one split factor into canonical `new_shares / old_shares` form."""

        if factor not in (None, ""):
            normalized_factor = float(factor)
        elif numerator not in (None, "") and denominator not in (None, ""):
            normalized_factor = float(numerator) / float(denominator)
        elif ratio_text not in (None, ""):
            normalized_factor = SplitEventsClient.parse_ratio_text(str(ratio_text))
        else:
            raise SplitEventsClientError("No usable split factor information was found in the record.")

        if normalized_factor <= 0:
            raise SplitEventsClientError(
                f"Split factor must be positive, got {normalized_factor}."
            )
        return normalized_factor

    @staticmethod
    def parse_ratio_text(ratio_text: str) -> float:
        """Parse common split ratio text into `new_shares / old_shares` form."""

        cleaned = ratio_text.strip().lower().replace("for", ":")
        cleaned = cleaned.replace("-", "")
        match = re.search(r"(\d+(?:\.\d+)?)\s*[:/]\s*(\d+(?:\.\d+)?)", cleaned)
        if match:
            numerator = float(match.group(1))
            denominator = float(match.group(2))
            if denominator == 0:
                raise SplitEventsClientError(f"Split ratio has zero denominator: {ratio_text}")
            return numerator / denominator

        try:
            numeric = float(cleaned)
        except ValueError as exc:
            raise SplitEventsClientError(f"Could not parse split ratio text: {ratio_text}") from exc

        if numeric <= 0:
            raise SplitEventsClientError(f"Parsed split ratio must be positive: {ratio_text}")
        return numeric

    @staticmethod
    def validate_known_split_dates(
        events: list[SplitEvent],
        expected_dates: list[str | date] | tuple[str | date, ...],
    ) -> None:
        """Validate that a set of expected split dates is present in normalized events."""

        observed = {event.split_date for event in events}
        missing: list[str] = []
        for expected in expected_dates:
            expected_date = expected if isinstance(expected, date) else date.fromisoformat(str(expected))
            if expected_date not in observed:
                missing.append(expected_date.isoformat())
        if missing:
            raise SplitEventsClientError(
                "Normalized split events are missing expected dates: " + ", ".join(sorted(missing))
            )

    @staticmethod
    def _parse_date_from_record(record: dict[str, Any], keys: tuple[str, ...]) -> date:
        raw_value = SplitEventsClient._extract_first(record, keys)
        if raw_value in (None, ""):
            keys_text = ", ".join(keys)
            raise SplitEventsClientError(
                f"Split record does not contain any recognized date field. Tried: {keys_text}"
            )
        return date.fromisoformat(str(raw_value)[:10])

    @staticmethod
    def _extract_first(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
        for key in keys:
            if key in record and record[key] not in (None, ""):
                return record[key]
        return None

    @staticmethod
    def _string_or_none(value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value)
