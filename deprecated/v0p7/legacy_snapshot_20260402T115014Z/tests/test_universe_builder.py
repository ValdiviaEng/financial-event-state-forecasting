from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data.universe_builder import (
    DEFAULT_PILOT_TICKERS,
    UniverseBuilderError,
    build_and_save_sp500_universe_snapshot,
    parse_sp500_wikipedia_snapshot,
)


SAMPLE_HTML = """
<html>
  <body>
    <table>
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Security</th>
          <th>GICS Sector</th>
          <th>GICS Sub-Industry</th>
          <th>Headquarters Location</th>
          <th>Date added</th>
          <th>CIK</th>
          <th>Founded</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>AAPL</td><td>Apple Inc.</td><td>Information Technology</td><td>Technology Hardware</td><td>Cupertino, California</td><td>1982-11-30</td><td>320193</td><td>1976</td></tr>
        <tr><td>AMZN</td><td>Amazon.com Inc.</td><td>Consumer Discretionary</td><td>Internet Retail</td><td>Seattle, Washington</td><td>2005-11-18</td><td>1018724</td><td>1994</td></tr>
        <tr><td>BF.B</td><td>Brown-Forman</td><td>Consumer Staples</td><td>Distillers</td><td>Louisville, Kentucky</td><td>1982-08-31</td><td>14693</td><td>1870</td></tr>
        <tr><td>BRK.B</td><td>Berkshire Hathaway</td><td>Financials</td><td>Multi-Sector Holdings</td><td>Omaha, Nebraska</td><td>2010-02-16</td><td>1067983</td><td>1839</td></tr>
        <tr><td>GOOGL</td><td>Alphabet</td><td>Communication Services</td><td>Interactive Media</td><td>Mountain View, California</td><td>2014-04-03</td><td>1652044</td><td>1998</td></tr>
        <tr><td>JPM</td><td>JPMorgan Chase</td><td>Financials</td><td>Diversified Banks</td><td>New York, New York</td><td>1975-06-30</td><td>19617</td><td>1799</td></tr>
        <tr><td>MSFT</td><td>Microsoft</td><td>Information Technology</td><td>Systems Software</td><td>Redmond, Washington</td><td>1994-06-01</td><td>789019</td><td>1975</td></tr>
        <tr><td>NVDA</td><td>NVIDIA</td><td>Information Technology</td><td>Semiconductors</td><td>Santa Clara, California</td><td>2001-11-30</td><td>1045810</td><td>1993</td></tr>
        <tr><td>UNH</td><td>UnitedHealth Group</td><td>Health Care</td><td>Managed Health Care</td><td>Minnetonka, Minnesota</td><td>1994-07-01</td><td>731766</td><td>1977</td></tr>
        <tr><td>XOM</td><td>ExxonMobil</td><td>Energy</td><td>Integrated Oil & Gas</td><td>Irving, Texas</td><td>1957-03-04</td><td>34088</td><td>1999</td></tr>
      </tbody>
    </table>
  </body>
</html>
"""


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


class _FakeSession:
    def __init__(self, html: str) -> None:
        self.html = html

    def get(self, *args, **kwargs):
        return _FakeResponse(self.html)


def test_parse_sp500_wikipedia_snapshot_preserves_dot_tickers() -> None:
    snapshot = parse_sp500_wikipedia_snapshot(
        SAMPLE_HTML,
        source_name="test_source",
        snapshot_date="2026-03-19",
        source_url="https://example.test/sp500",
    )

    assert snapshot.row_count == 10
    assert snapshot.tickers[2] == "BF.B"
    assert snapshot.tickers[3] == "BRK.B"
    assert snapshot.source_name == "test_source"
    assert snapshot.snapshot_date == "2026-03-19"


def test_build_and_save_sp500_universe_snapshot_writes_expected_files(tmp_path: Path) -> None:
    result = build_and_save_sp500_universe_snapshot(
        tmp_path,
        source_url="https://example.test/sp500",
        source_name="test_source",
        snapshot_date="2026-03-19",
        include_pilot_subset=True,
        pilot_tickers=DEFAULT_PILOT_TICKERS,
        session=_FakeSession(SAMPLE_HTML),
    )

    assert result.raw_html_path.exists()
    assert result.dated_snapshot_path.exists()
    assert result.latest_snapshot_path.exists()
    assert result.dated_manifest_path.exists()
    assert result.pilot_snapshot_path is not None and result.pilot_snapshot_path.exists()

    manifest = json.loads(result.dated_manifest_path.read_text(encoding="utf-8"))
    assert manifest["row_count"] == 10
    assert manifest["snapshot_date"] == "2026-03-19"

    latest_rows = result.latest_snapshot_path.read_text(encoding="utf-8").splitlines()
    assert latest_rows[0].startswith("ticker,")
    assert any("BRK.B" in line for line in latest_rows)

    pilot_rows = result.pilot_snapshot_path.read_text(encoding="utf-8").splitlines()
    assert len(pilot_rows) == 11  # header + 10 rows


def test_parse_sp500_wikipedia_snapshot_raises_if_components_table_missing() -> None:
    with pytest.raises(UniverseBuilderError, match="Could not locate the S&P 500 constituents table"):
        parse_sp500_wikipedia_snapshot("<html><body><table><tr><td>irrelevant</td></tr></table></body></html>")
