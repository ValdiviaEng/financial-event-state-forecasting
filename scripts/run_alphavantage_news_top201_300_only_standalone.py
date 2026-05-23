"""Standalone Alpha Vantage NEWS_SENTIMENT runner for Slickcharts ranks 201-300."""

from __future__ import annotations

import sys

from alphavantage_news_bucket_common import BucketConfig, main_for_bucket


FALLBACK_API_KEY = ""

TOP201_300_TICKERS = (
    "AZO", "FAST", "D", "CTVA", "FIX", "KEYS", "GWW", "TGT", "AJG", "ALL",
    "OKE", "AME", "ETR", "FANG", "CARR", "VST", "TRGP", "PSA", "NXPI", "XEL",
    "EA", "CAH", "ZTS", "EXC", "GRMN", "F", "URI", "MET", "CVNA", "NDAQ",
    "ADSK", "WAB", "EW", "IDXX", "YUM", "FITB", "ROK", "CMG", "COIN", "DAL",
    "BDX", "ODFL", "EBAY", "NUE", "KR", "PEG", "CBRE", "DHI", "AIG", "ED",
    "HSY", "PCG", "PYPL", "AMP", "VTR", "MSCI", "STT", "CCL", "MCHP", "VMC",
    "WEC", "MLM", "HIG", "LYV", "CCI", "DDOG", "XYZ", "SATS", "EQT", "TTWO",
    "KDP", "EME", "LVS", "ROP", "NRG", "SYY", "ACGL", "PRU", "ADM", "IR",
    "GEHC", "HBAN", "RMD", "KVUE", "HPE", "MTB", "IRM", "A", "KMB", "IBKR",
    "JBL", "CPRT", "ATO", "HAL", "WAT", "AEE", "UAL", "DTE", "OTIS", "XYL",
)


CONFIG = BucketConfig(
    script_description="Run a standalone Alpha Vantage NEWS_SENTIMENT daemon for Slickcharts ranks 201-300.",
    bucket_label="top201_300",
    bucket_slug="top201_300_only",
    ticker_range_label="201-300",
    base_tickers=TOP201_300_TICKERS,
    fallback_api_key=FALLBACK_API_KEY,
    user_agent="EventStateForecastingAlphaVantageTop201To300Only/1.0",
)


if __name__ == "__main__":
    raise SystemExit(main_for_bucket(CONFIG, sys.argv[1:]))
