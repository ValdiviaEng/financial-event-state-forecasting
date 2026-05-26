from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class V1P0ReportError(ValueError):
    """Raised when report output violates v1p0 non-claim rules."""


def render_static_report(metrics: pd.DataFrame, strata: pd.DataFrame, intervals: pd.DataFrame, output_dir: str | Path, config: dict[str, Any]) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output_path / "metrics.csv", index=False)
    strata.to_csv(output_path / "strata.csv", index=False)
    intervals.to_csv(output_path / "uncertainty.csv", index=False)
    caveats = list(config["required_caveats"])
    html = "\n".join(
        [
            "<html><body>",
            "<h1>v1p0 First-Slice Smoke Report</h1>",
            "<p>Historical smoke output only. This is not trading advice, not a live forecast, and not a Stage 6 reinterpretation.</p>",
            "<h2>Caveats</h2>",
            "<ul>",
            *[f"<li>{item}</li>" for item in caveats],
            "</ul>",
            _table_section("metrics", "Metrics", "Source: metrics.csv", metrics),
            _table_section("strata", "Stratified Metrics", "Source: strata.csv", strata),
            _table_section("uncertainty", "Uncertainty Evidence", "Source: uncertainty.csv", intervals),
            "</body></html>",
        ]
    )
    lower_html = html.lower()
    forbidden = [phrase for phrase in config["forbidden_phrases"] if phrase in lower_html and phrase not in {"live forecast"}]
    if forbidden:
        raise V1P0ReportError(f"report contains forbidden wording: {forbidden}")
    report_path = output_path / "report.html"
    report_path.write_text(html, encoding="utf-8")
    return report_path


def _table_section(section_id: str, title: str, caption: str, frame: pd.DataFrame) -> str:
    table = frame.to_html(index=False)
    table = table.replace(">\n  <thead>", f">\n  <caption>{caption}</caption>\n  <thead>", 1)
    return "\n".join(
        [
            f'<section id="{section_id}" data-row-count="{len(frame)}">',
            f"<h2>{title}</h2>",
            table,
            "</section>",
        ]
    )
