"""Standalone Alpha Vantage NEWS_SENTIMENT runner for Slickcharts ranks 401-500.

Use `--include-expanded` to append a curated set of notable, news-rich, liquid
tickers that are not present in the repository's 2026-03-19 S&P 500 snapshot.
Use `--expanded-only` to run only that curated expansion bucket.
"""

from __future__ import annotations

import sys

from alphavantage_news_bucket_common import BucketConfig, main_for_bucket


FALLBACK_API_KEY = ""

TOP401_500_TICKERS = (
    "LNT", "NVR", "CF", "IFF", "WST", "PKG", "CNC", "ZBH", "GPN", "FTV",
    "WY", "BR", "LII", "HPQ", "BALL", "FFIV", "CDW", "ESS", "TXT", "PTC",
    "VTRS", "KIM", "INVH", "HII", "TKO", "NDSN", "CSGP", "DECK", "SMCI", "TRMB",
    "GPC", "IEX", "MAA", "PNR", "MKC", "J", "REG", "COO", "HST", "APA",
    "PODD", "BF.B", "TYL", "AKAM", "EG", "ERIE", "AVY", "BBY", "BEN", "HAS",
    "MAS", "CLX", "APTV", "PNW", "ALLE", "ALGN", "FOX", "DPZ", "FOXA", "GNRC",
    "PSKY", "DOC", "UDR", "HRL", "GL", "SOLV", "SWK", "UHS", "AIZ", "GEN",
    "WYNN", "ZBRA", "CPT", "JKHY", "GDDY", "IVZ", "AES", "IT", "RVTY", "DVA",
    "SJM", "TTD", "MGM", "FRT", "BLDR", "AOS", "NCLH", "NWSA", "BAX", "TECH",
    "CRL", "HSIC", "SWKS", "TAP", "BXP", "POOL", "MOS", "FDS", "ARE", "CAG",
)

# Curated notable non-S&P 500 names, validated against the repository's
# `sp500_snapshot_2026-03-19.csv` to avoid overlap with the benchmark universe.
EXPANDED_UNIVERSE_TICKERS = (
    "ARM", "MSTR", "SNOW", "SHOP", "MDB", "RBLX", "HUBS", "NET", "SPOT", "PDD",
    "BABA", "BIDU", "JD", "MELI", "CAVA", "RDDT", "ROKU", "DOCU", "ZM", "TEAM",
    "TWLO", "ESTC", "BILL", "OKTA", "U", "APPF", "AFRM", "NU", "SOFI", "CFLT",
    "DUOL", "CELH", "RKLB", "ASTS", "LUNR", "TEM", "HIMS", "CHWY", "WING", "ONON",
    "GFS", "CRWV", "SMR", "IONQ", "NIO", "LI", "XPEV", "GRAB", "SE", "WIX",
    "ZI", "S", "SOUN", "PATH", "MARA", "RIOT", "SFM", "TOL", "WSO", "GTLB",
    "CRDO", "ALAB", "CORZ", "FSLY", "BROS",
)


CONFIG = BucketConfig(
    script_description="Run a standalone Alpha Vantage NEWS_SENTIMENT daemon for Slickcharts ranks 401-500, with optional non-S&P expanded universe support.",
    bucket_label="top401_500",
    bucket_slug="top401_500_only",
    ticker_range_label="401-500",
    base_tickers=TOP401_500_TICKERS,
    expanded_tickers=EXPANDED_UNIVERSE_TICKERS,
    fallback_api_key=FALLBACK_API_KEY,
    user_agent="EventStateForecastingAlphaVantageTop401To500Only/1.0",
)


if __name__ == "__main__":
    raise SystemExit(main_for_bucket(CONFIG, sys.argv[1:]))
