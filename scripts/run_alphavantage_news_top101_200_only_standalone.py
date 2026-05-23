"""Standalone Alpha Vantage NEWS_SENTIMENT runner for Slickcharts ranks 101-200."""

from __future__ import annotations

import sys

from alphavantage_news_bucket_common import BucketConfig, main_for_bucket


FALLBACK_API_KEY = ""

TOP101_200_TICKERS = (
    "MDT", "VRTX", "HCA", "ACN", "SBUX", "SO", "CME", "MCK", "CEG", "TT",
    "DUK", "CVS", "EQIX", "HWM", "CMCSA", "FCX", "INTU", "CRWD", "NOC", "MAR",
    "WM", "BSX", "ADBE", "ICE", "GD", "FDX", "PNC", "BX", "WMB", "BK",
    "PWR", "JCI", "UPS", "USB", "NOW", "CMI", "AMT", "SHW", "KKR", "MRSH",
    "EMR", "REGN", "CRH", "CSX", "MMM", "SLB", "ITW", "ORLY", "ABNB", "ECL",
    "MCO", "ADP", "MDLZ", "SNPS", "RCL", "AEP", "MNST", "HLT", "CDNS", "EOG",
    "KMI", "MSI", "CI", "VLO", "ROST", "CIEN", "CTAS", "GM", "WBD", "ELV",
    "TDG", "CL", "TEL", "AON", "PCAR", "NSC", "APD", "MPWR", "RSG", "DASH",
    "LHX", "MPC", "SPG", "DLR", "SRE", "LITE", "PSX", "TRV", "NKE", "COR",
    "BKR", "HOOD", "TFC", "APO", "O", "COHR", "TER", "OXY", "AFL", "FTNT",
)


CONFIG = BucketConfig(
    script_description="Run a standalone Alpha Vantage NEWS_SENTIMENT daemon for Slickcharts ranks 101-200.",
    bucket_label="top101_200",
    bucket_slug="top101_200_only",
    ticker_range_label="101-200",
    base_tickers=TOP101_200_TICKERS,
    fallback_api_key=FALLBACK_API_KEY,
    user_agent="EventStateForecastingAlphaVantageTop101To200Only/1.0",
)


if __name__ == "__main__":
    raise SystemExit(main_for_bucket(CONFIG, sys.argv[1:]))
