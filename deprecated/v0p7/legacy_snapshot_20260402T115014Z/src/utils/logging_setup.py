"""Logging helpers for consistent console and file logging."""

from __future__ import annotations

import logging
from pathlib import Path
import sys
import time


DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(run_id)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class RunContextFilter(logging.Filter):
    """Ensure every log record contains a run identifier field."""

    def __init__(self, run_id: str | None = None) -> None:
        super().__init__()
        self.run_id = run_id or "-"

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "run_id"):
            record.run_id = self.run_id
        return True


def configure_logging(
    log_level: str | int = "INFO",
    logger_name: str | None = None,
    run_id: str | None = None,
    log_file: str | Path | None = None,
    console: bool = True,
    use_utc: bool = False,
    reset_handlers: bool = True,
) -> logging.Logger:
    """Configure a logger with consistent console and optional file output."""

    logger = logging.getLogger(logger_name)
    logger.setLevel(_coerce_log_level(log_level))
    logger.propagate = False

    if reset_handlers:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
        for existing_filter in list(logger.filters):
            logger.removeFilter(existing_filter)

    run_filter = RunContextFilter(run_id=run_id)
    logger.addFilter(run_filter)
    formatter = _build_formatter(use_utc=use_utc)

    if console:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.addFilter(run_filter)
        logger.addHandler(stream_handler)

    if log_file is not None:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.addFilter(run_filter)
        logger.addHandler(file_handler)

    if not logger.handlers:
        logger.addHandler(logging.NullHandler())

    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a named logger without mutating global logging configuration."""

    return logging.getLogger(name)


def _build_formatter(use_utc: bool) -> logging.Formatter:
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
    if use_utc:
        formatter.converter = time.gmtime
    return formatter


def _coerce_log_level(log_level: str | int) -> int:
    if isinstance(log_level, int):
        return log_level

    normalized = log_level.strip().upper()
    if normalized not in logging.getLevelNamesMapping():
        raise ValueError(f"Unsupported log level: {log_level}")
    return logging.getLevelNamesMapping()[normalized]
