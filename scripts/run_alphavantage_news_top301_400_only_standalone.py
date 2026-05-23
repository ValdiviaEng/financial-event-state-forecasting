"""Standalone Alpha Vantage NEWS_SENTIMENT runner for Slickcharts ranks 301-400."""

from __future__ import annotations

import sys

from alphavantage_news_bucket_common import BucketConfig, main_for_bucket


FALLBACK_API_KEY = ""

TOP301_400_TICKERS = (
    "CBOE", "PAYX", "TPR", "VICI", "TDY", "FISV", "PPL", "FE", "DVN", "EXR",
    "DOV", "EIX", "WDAY", "RJF", "STZ", "HUBB", "CNP", "TPL", "NTRS", "IQV",
    "DOW", "EXPE", "AXON", "CTSH", "STLD", "Q", "KHC", "CASY", "CHTR", "CFG",
    "ON", "MTD", "AWK", "WTW", "ES", "EL", "ROL", "DG", "BIIB", "CTRA",
    "SYF", "CINF", "PPG", "DXCM", "WRB", "CMS", "BG", "VRSN", "EXE", "LYB",
    "TSCO", "SBAC", "AVB", "RF", "TSN", "EQR", "HUM", "PHM", "KEY", "RL",
    "NI", "ULTA", "CHD", "ARES", "L", "WSM", "FIS", "BRO", "SW", "DRI",
    "LEN", "VLTO", "FICO", "FSLR", "STE", "VRSK", "LH", "JBHT", "EFX", "OMC",
    "DGX", "CPAY", "ALB", "MRNA", "TROW", "PFG", "SNA", "DLTR", "LUV", "IP",
    "DD", "CHRW", "LDOS", "EVRG", "INCY", "EXPD", "AMCR", "GIS", "LULU", "NTAP",
)


CONFIG = BucketConfig(
    script_description="Run a standalone Alpha Vantage NEWS_SENTIMENT daemon for Slickcharts ranks 301-400.",
    bucket_label="top301_400",
    bucket_slug="top301_400_only",
    ticker_range_label="301-400",
    base_tickers=TOP301_400_TICKERS,
    fallback_api_key=FALLBACK_API_KEY,
    user_agent="EventStateForecastingAlphaVantageTop301To400Only/1.0",
)


if __name__ == "__main__":
    raise SystemExit(main_for_bucket(CONFIG, sys.argv[1:]))
