#!/usr/bin/env python3
"""Non-destructively merge Alpha Vantage NEWS_SENTIMENT raw roots.

The merge writes a new versioned raw root and leaves every source root untouched.
It ignores Windows Zone.Identifier sidecars, deduplicates exact duplicate feed
articles within each ticker/window, and records provenance for retained rows.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL_ROOT = PROJECT_ROOT / "data" / "raw" / "alphavantage"
DEFAULT_ZIP2_ROOT = PROJECT_ROOT / "data" / "raw_zip2_extended_granularity" / "raw" / "alphavantage"
DEFAULT_OUTPUT_PARENT = PROJECT_ROOT / "data" / "raw" / "alphavantage_merged_versions"
DEFAULT_UNIVERSE_FILE = PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
NEWS_FILE_RE = re.compile(r"^news_sentiment__(\d{4}-\d{2}-\d{2})__(\d{4}-\d{2}-\d{2}|current)\.json$")
ZONE_IDENTIFIER_MARKER = "Zone.Identifier"
DEFAULT_PROVIDER_LIMIT = 1000


@dataclass(frozen=True, slots=True)
class SourceRoot:
    label: str
    root: Path
    order: int


@dataclass(frozen=True, slots=True)
class SourceFile:
    source: SourceRoot
    path: Path
    relative_path: str
    ticker: str
    window_start: str
    window_end: str
    byte_hash: str
    payload: dict[str, Any] | None
    feed: list[Any]
    error: str | None


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge Alpha Vantage NEWS_SENTIMENT raw roots into a versioned output root.")
    parser.add_argument("--canonical-root", default=str(DEFAULT_CANONICAL_ROOT), help="Current canonical Alpha Vantage raw root.")
    parser.add_argument("--zip2-root", default=str(DEFAULT_ZIP2_ROOT), help="Second raw dump Alpha Vantage root.")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Optional extra source as LABEL=PATH. If any are supplied, defaults are not added unless explicitly supplied.",
    )
    parser.add_argument(
        "--output-run-root",
        default=None,
        help="Versioned run root. Defaults under data/raw/alphavantage_merged_versions/.",
    )
    parser.add_argument("--universe-file", default=str(DEFAULT_UNIVERSE_FILE), help="Top-50 universe file for annual/current coverage audit.")
    parser.add_argument("--limit", type=int, default=DEFAULT_PROVIDER_LIMIT, help="Provider limit used for truncation audit.")
    parser.add_argument("--dry-run", action="store_true", help="Build the audit without writing merged news payloads or copied support files.")
    parser.add_argument("--no-article-provenance", action="store_true", help="Do not write per-retained-article provenance JSONL.")
    parser.add_argument("--no-support-files", action="store_true", help="Do not copy non-news support files into support_files/.")
    parser.add_argument("--json", action="store_true", help="Print full summary JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    generated_at = datetime.now(UTC)
    sources = resolve_sources(args)
    run_root = resolve_run_root(args.output_run_root, generated_at=generated_at)
    merged_root = run_root / "alphavantage"
    manifest_dir = run_root / "manifests"
    support_root = run_root / "support_files"

    if not args.dry_run and run_root.exists():
        raise SystemExit(f"Output run root already exists: {run_root}")

    source_files, source_audits, skipped_zone_sidecars = collect_source_files(sources)
    grouped: dict[str, list[SourceFile]] = defaultdict(list)
    file_hash_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source_file in source_files:
        grouped[source_file.relative_path].append(source_file)
        file_hash_groups[source_file.byte_hash].append(
            {"source_label": source_file.source.label, "relative_path": source_file.relative_path}
        )

    if not args.dry_run:
        manifest_dir.mkdir(parents=True, exist_ok=True)
        merged_root.mkdir(parents=True, exist_ok=True)
        if not args.no_support_files:
            support_root.mkdir(parents=True, exist_ok=True)

    provenance_path = manifest_dir / "feed_article_provenance.jsonl"
    provenance_handle = None
    if not args.dry_run and not args.no_article_provenance:
        provenance_handle = provenance_path.open("w", encoding="utf-8")

    file_records: list[dict[str, Any]] = []
    output_rel_paths: set[str] = set()
    aggregate = build_empty_aggregate()
    try:
        for relative_path in sorted(grouped):
            record = merge_group(
                relative_path=relative_path,
                source_files=sorted(grouped[relative_path], key=lambda item: (item.source.order, item.path.as_posix())),
                merged_root=merged_root,
                dry_run=bool(args.dry_run),
                limit=int(args.limit),
                provenance_handle=provenance_handle,
            )
            file_records.append(record)
            update_aggregate(aggregate, record)
            if record["valid_source_file_count"] > 0:
                output_rel_paths.add(relative_path)
    finally:
        if provenance_handle is not None:
            provenance_handle.close()

    support_file_records = [] if args.no_support_files else copy_support_files(sources, support_root=support_root, dry_run=bool(args.dry_run))
    duplicate_file_hash_groups = [items for items in file_hash_groups.values() if len(items) > 1]
    universe_audit = build_universe_coverage_audit(resolve_path(args.universe_file), output_rel_paths, generated_at.year)
    truncation_audit = build_truncation_audit(file_records)
    summary = build_summary(
        generated_at=generated_at,
        run_root=run_root,
        merged_root=merged_root,
        manifest_dir=manifest_dir,
        sources=sources,
        source_audits=source_audits,
        skipped_zone_sidecars=skipped_zone_sidecars,
        file_records=file_records,
        support_file_records=support_file_records,
        duplicate_file_hash_groups=duplicate_file_hash_groups,
        aggregate=aggregate,
        universe_audit=universe_audit,
        truncation_audit=truncation_audit,
        dry_run=bool(args.dry_run),
        article_provenance_path=None if args.no_article_provenance else provenance_path,
    )

    if not args.dry_run:
        write_json(manifest_dir / "merge_summary.json", summary)
        write_json(manifest_dir / "file_manifest.json", {"files": file_records})
        write_json(manifest_dir / "duplicate_file_hash_groups.json", {"groups": duplicate_file_hash_groups})
        write_json(manifest_dir / "support_file_manifest.json", {"files": support_file_records})

    print_summary(summary, as_json=bool(args.json))
    return 0 if not summary["invalid_news_files"] else 2


def resolve_sources(args: argparse.Namespace) -> list[SourceRoot]:
    specs = args.source or [f"canonical={args.canonical_root}", f"zip2_extended={args.zip2_root}"]
    sources: list[SourceRoot] = []
    labels: set[str] = set()
    for order, spec in enumerate(specs):
        if "=" not in spec:
            raise SystemExit(f"Source must use LABEL=PATH form: {spec}")
        label, raw_path = spec.split("=", 1)
        label = sanitize_label(label.strip())
        if not label:
            raise SystemExit(f"Source label is empty: {spec}")
        if label in labels:
            raise SystemExit(f"Duplicate source label: {label}")
        labels.add(label)
        root = resolve_path(raw_path)
        if not root.exists() or not root.is_dir():
            raise SystemExit(f"Source root does not exist or is not a directory: {root}")
        sources.append(SourceRoot(label=label, root=root, order=order))
    if len(sources) < 2:
        raise SystemExit("At least two source roots are required for a merge audit.")
    return sources


def sanitize_label(label: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", label).strip("._-")
    return sanitized


def resolve_run_root(raw_run_root: str | None, *, generated_at: datetime) -> Path:
    if raw_run_root:
        return resolve_path(raw_run_root)
    stamp = generated_at.strftime("%Y%m%dT%H%M%SZ")
    return DEFAULT_OUTPUT_PARENT / f"alphavantage_canonical_plus_zip2_extended_granularity__{stamp}"


def collect_source_files(sources: list[SourceRoot]) -> tuple[list[SourceFile], list[dict[str, Any]], list[dict[str, str]]]:
    source_files: list[SourceFile] = []
    source_audits: list[dict[str, Any]] = []
    skipped_zone_sidecars: list[dict[str, str]] = []
    for source in sources:
        audit = {
            "source_label": source.label,
            "root": str(source.root),
            "news_file_count": 0,
            "valid_news_file_count": 0,
            "invalid_news_file_count": 0,
            "feed_rows": 0,
            "zone_identifier_sidecars_skipped": 0,
            "support_file_count": 0,
        }
        for path in sorted(item for item in source.root.rglob("*") if item.is_file()):
            relative_path = path.relative_to(source.root).as_posix()
            if ZONE_IDENTIFIER_MARKER in path.name:
                audit["zone_identifier_sidecars_skipped"] += 1
                skipped_zone_sidecars.append({"source_label": source.label, "relative_path": relative_path})
                continue
            parsed_name = parse_news_file_name(path.name)
            if parsed_name is None or path.parent == source.root:
                audit["support_file_count"] += 1
                continue
            source_file = load_source_file(source, path, parsed_name=parsed_name)
            source_files.append(source_file)
            audit["news_file_count"] += 1
            if source_file.error is None:
                audit["valid_news_file_count"] += 1
                audit["feed_rows"] += len(source_file.feed)
            else:
                audit["invalid_news_file_count"] += 1
        source_audits.append(audit)
    return source_files, source_audits, skipped_zone_sidecars


def parse_news_file_name(file_name: str) -> tuple[str, str] | None:
    match = NEWS_FILE_RE.match(file_name)
    if not match:
        return None
    return match.group(1), match.group(2)


def load_source_file(source: SourceRoot, path: Path, *, parsed_name: tuple[str, str]) -> SourceFile:
    raw_bytes = path.read_bytes()
    byte_hash = sha256_bytes(raw_bytes)
    payload: dict[str, Any] | None = None
    feed: list[Any] = []
    error: str | None = None
    try:
        decoded = json.loads(raw_bytes.decode("utf-8"))
        if not isinstance(decoded, dict):
            error = f"payload_not_object:{type(decoded).__name__}"
        else:
            payload = decoded
            raw_feed = decoded.get("feed")
            if not isinstance(raw_feed, list):
                error = f"feed_not_list:{type(raw_feed).__name__}"
            else:
                feed = raw_feed
    except UnicodeDecodeError as exc:
        error = f"utf8_decode_error:{exc}"
    except json.JSONDecodeError as exc:
        error = f"json_decode_error:{exc}"
    return SourceFile(
        source=source,
        path=path,
        relative_path=path.relative_to(source.root).as_posix(),
        ticker=path.parent.name,
        window_start=parsed_name[0],
        window_end=parsed_name[1],
        byte_hash=byte_hash,
        payload=payload,
        feed=feed,
        error=error,
    )


def merge_group(
    *,
    relative_path: str,
    source_files: list[SourceFile],
    merged_root: Path,
    dry_run: bool,
    limit: int,
    provenance_handle: Any,
) -> dict[str, Any]:
    valid_files = [item for item in source_files if item.error is None and item.payload is not None]
    invalid_files = [item for item in source_files if item.error is not None]
    first = source_files[0]
    record: dict[str, Any] = {
        "relative_path": relative_path,
        "ticker": first.ticker,
        "window_start": first.window_start,
        "window_end": first.window_end,
        "window_shape": classify_window(first.window_start, first.window_end),
        "source_file_count": len(source_files),
        "valid_source_file_count": len(valid_files),
        "invalid_source_file_count": len(invalid_files),
        "source_files": [
            {
                "source_label": item.source.label,
                "source_relative_path": item.relative_path,
                "byte_hash": item.byte_hash,
                "feed_count": None if item.error is not None else len(item.feed),
                "error": item.error,
            }
            for item in source_files
        ],
        "source_file_hash_unique_count": len({item.byte_hash for item in source_files}),
        "source_feed_rows": sum(len(item.feed) for item in valid_files),
        "merged_feed_rows": 0,
        "exact_duplicate_article_rows_removed": 0,
        "identity_collision_groups_preserved": 0,
        "identity_collision_article_variants_preserved": 0,
        "metadata_variant_count": 0,
        "likely_truncated_after_merge": False,
        "empty_feed_after_merge": False,
        "wrote_payload": False,
    }
    if not valid_files:
        return record

    base_payload = valid_files[0].payload
    assert base_payload is not None
    metadata_hashes = {object_hash(metadata_without_feed(item.payload)) for item in valid_files if item.payload is not None}
    retained_by_content_hash: dict[str, Any] = {}
    provenance_by_content_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    identity_by_content_hash: dict[str, str] = {}
    identity_groups: dict[str, set[str]] = defaultdict(set)

    for source_file in valid_files:
        for index, article in enumerate(source_file.feed):
            content_hash = object_hash(article)
            identity_hash = article_identity_hash(article, fallback_content_hash=content_hash)
            identity_groups[identity_hash].add(content_hash)
            if content_hash not in retained_by_content_hash:
                retained_by_content_hash[content_hash] = article
                identity_by_content_hash[content_hash] = identity_hash
            provenance_by_content_hash[content_hash].append(
                {
                    "source_label": source_file.source.label,
                    "source_relative_path": source_file.relative_path,
                    "source_feed_index": index,
                }
            )

    merged_feed = sorted(retained_by_content_hash.values(), key=article_sort_key)
    merged_payload = dict(base_payload)
    merged_payload["feed"] = merged_feed
    if "items" in merged_payload and isinstance(merged_payload["items"], str) and merged_payload["items"].isdigit():
        merged_payload["items"] = str(len(merged_feed))

    record["merged_feed_rows"] = len(merged_feed)
    record["exact_duplicate_article_rows_removed"] = record["source_feed_rows"] - len(retained_by_content_hash)
    record["identity_collision_groups_preserved"] = sum(1 for variants in identity_groups.values() if len(variants) > 1)
    record["identity_collision_article_variants_preserved"] = sum(len(variants) for variants in identity_groups.values() if len(variants) > 1)
    record["metadata_variant_count"] = len(metadata_hashes)
    record["likely_truncated_after_merge"] = len(merged_feed) >= limit
    record["empty_feed_after_merge"] = len(merged_feed) == 0

    if not dry_run:
        output_path = merged_root / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(output_path, merged_payload)
        record["wrote_payload"] = True
        if provenance_handle is not None:
            write_article_provenance(
                provenance_handle=provenance_handle,
                relative_path=relative_path,
                ticker=first.ticker,
                retained_by_content_hash=retained_by_content_hash,
                identity_by_content_hash=identity_by_content_hash,
                provenance_by_content_hash=provenance_by_content_hash,
            )
    return record


def metadata_without_feed(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {}
    return {key: value for key, value in payload.items() if key != "feed"}


def article_identity_hash(article: Any, *, fallback_content_hash: str) -> str:
    if not isinstance(article, dict):
        return f"content:{fallback_content_hash}"
    url = normalize_identity_field(article.get("url"))
    title = normalize_identity_field(article.get("title"))
    time_published = normalize_identity_field(article.get("time_published"))
    if not (url or title or time_published):
        return f"content:{fallback_content_hash}"
    return "identity:" + sha256_text("\x1f".join([url, title, time_published]))


def normalize_identity_field(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def article_sort_key(article: Any) -> tuple[str, str, str]:
    if not isinstance(article, dict):
        return ("", "", canonical_json_text(article))
    time_published = str(article.get("time_published") or "")
    title = str(article.get("title") or "")
    url = str(article.get("url") or "")
    return (invert_for_descending(time_published), title, url)


def invert_for_descending(value: str) -> str:
    return "".join(chr(0x10FFFF - ord(char)) for char in value)


def write_article_provenance(
    *,
    provenance_handle: Any,
    relative_path: str,
    ticker: str,
    retained_by_content_hash: dict[str, Any],
    identity_by_content_hash: dict[str, str],
    provenance_by_content_hash: dict[str, list[dict[str, Any]]],
) -> None:
    for content_hash in sorted(retained_by_content_hash):
        article = retained_by_content_hash[content_hash]
        record = {
            "relative_path": relative_path,
            "ticker": ticker,
            "article_content_hash": content_hash,
            "article_identity_hash": identity_by_content_hash[content_hash],
            "time_published": article.get("time_published") if isinstance(article, dict) else None,
            "title": article.get("title") if isinstance(article, dict) else None,
            "url": article.get("url") if isinstance(article, dict) else None,
            "source_occurrences": provenance_by_content_hash[content_hash],
        }
        provenance_handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def copy_support_files(sources: list[SourceRoot], *, support_root: Path, dry_run: bool) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in sources:
        for path in sorted(item for item in source.root.rglob("*") if item.is_file()):
            relative_path = path.relative_to(source.root).as_posix()
            if ZONE_IDENTIFIER_MARKER in path.name:
                continue
            if parse_news_file_name(path.name) is not None and path.parent != source.root:
                continue
            destination = support_root / source.label / relative_path
            record = {
                "source_label": source.label,
                "relative_path": relative_path,
                "byte_hash": sha256_bytes(path.read_bytes()),
                "copied_to": str(destination),
                "copied": False,
            }
            if not dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
                record["copied"] = True
            records.append(record)
    return records


def build_empty_aggregate() -> dict[str, int]:
    return {
        "relative_path_count": 0,
        "valid_output_file_count": 0,
        "invalid_only_relative_path_count": 0,
        "source_feed_rows": 0,
        "merged_feed_rows": 0,
        "exact_duplicate_article_rows_removed": 0,
        "identity_collision_groups_preserved": 0,
        "identity_collision_article_variants_preserved": 0,
        "relative_paths_with_conflicting_source_file_hashes": 0,
        "relative_paths_with_metadata_variants": 0,
        "likely_truncated_output_file_count": 0,
        "empty_output_file_count": 0,
    }


def update_aggregate(aggregate: dict[str, int], record: dict[str, Any]) -> None:
    aggregate["relative_path_count"] += 1
    if record["valid_source_file_count"] > 0:
        aggregate["valid_output_file_count"] += 1
    else:
        aggregate["invalid_only_relative_path_count"] += 1
    aggregate["source_feed_rows"] += int(record["source_feed_rows"])
    aggregate["merged_feed_rows"] += int(record["merged_feed_rows"])
    aggregate["exact_duplicate_article_rows_removed"] += int(record["exact_duplicate_article_rows_removed"])
    aggregate["identity_collision_groups_preserved"] += int(record["identity_collision_groups_preserved"])
    aggregate["identity_collision_article_variants_preserved"] += int(record["identity_collision_article_variants_preserved"])
    if record["source_file_hash_unique_count"] > 1:
        aggregate["relative_paths_with_conflicting_source_file_hashes"] += 1
    if record["metadata_variant_count"] > 1:
        aggregate["relative_paths_with_metadata_variants"] += 1
    if record["likely_truncated_after_merge"]:
        aggregate["likely_truncated_output_file_count"] += 1
    if record["empty_feed_after_merge"]:
        aggregate["empty_output_file_count"] += 1


def build_universe_coverage_audit(universe_file: Path, output_rel_paths: set[str], current_year: int) -> dict[str, Any]:
    tickers = read_universe_tickers(universe_file)
    if not tickers:
        return {
            "universe_file": str(universe_file),
            "ticker_count": 0,
            "expected_annual_current_window_count": 0,
            "present_annual_current_window_count": 0,
            "missing_annual_current_window_count": None,
            "missing_by_ticker": {},
        }
    expected: list[str] = []
    missing_by_ticker: dict[str, list[str]] = {}
    for ticker in tickers:
        ticker_expected: list[str] = []
        for year in range(2010, current_year):
            ticker_expected.append(f"{ticker}/news_sentiment__{year}-01-01__{year}-12-31.json")
        ticker_expected.append(f"{ticker}/news_sentiment__{current_year}-01-01__current.json")
        expected.extend(ticker_expected)
        missing = [item for item in ticker_expected if item not in output_rel_paths]
        if missing:
            missing_by_ticker[ticker] = missing
    expected_set = set(expected)
    return {
        "universe_file": str(universe_file),
        "ticker_count": len(tickers),
        "expected_annual_current_window_count": len(expected_set),
        "present_annual_current_window_count": len(expected_set.intersection(output_rel_paths)),
        "missing_annual_current_window_count": sum(len(items) for items in missing_by_ticker.values()),
        "missing_by_ticker": missing_by_ticker,
    }


def build_truncation_audit(file_records: list[dict[str, Any]]) -> dict[str, Any]:
    truncated_by_ticker: dict[str, int] = defaultdict(int)
    truncated_by_shape: dict[str, int] = defaultdict(int)
    empty_by_ticker: dict[str, int] = defaultdict(int)
    for record in file_records:
        if record["valid_source_file_count"] <= 0:
            continue
        if record["likely_truncated_after_merge"]:
            truncated_by_ticker[record["ticker"]] += 1
            truncated_by_shape[record["window_shape"]] += 1
        if record["empty_feed_after_merge"]:
            empty_by_ticker[record["ticker"]] += 1
    return {
        "likely_truncated_output_file_count": sum(truncated_by_ticker.values()),
        "likely_truncated_by_ticker": dict(sorted(truncated_by_ticker.items())),
        "likely_truncated_by_window_shape": dict(sorted(truncated_by_shape.items())),
        "empty_output_file_count": sum(empty_by_ticker.values()),
        "empty_output_by_ticker": dict(sorted(empty_by_ticker.items())),
    }


def classify_window(start: str, end: str) -> str:
    if end == "current":
        return "current_partial" if not start.endswith("-01-01") else "annual_current"
    start_year, start_month, start_day = start.split("-")
    end_year, end_month, end_day = end.split("-")
    if start_month == "01" and start_day == "01" and end_month == "12" and end_day == "31" and start_year == end_year:
        return "annual"
    if start_day == "01" and start_year == end_year and (start_month, end_month, end_day) in {
        ("01", "03", "31"),
        ("04", "06", "30"),
        ("07", "09", "30"),
        ("10", "12", "31"),
    }:
        return "quarterly"
    if start_day == "01" and start_year == end_year and start_month == end_month:
        return "monthly"
    return "custom"


def build_summary(
    *,
    generated_at: datetime,
    run_root: Path,
    merged_root: Path,
    manifest_dir: Path,
    sources: list[SourceRoot],
    source_audits: list[dict[str, Any]],
    skipped_zone_sidecars: list[dict[str, str]],
    file_records: list[dict[str, Any]],
    support_file_records: list[dict[str, Any]],
    duplicate_file_hash_groups: list[list[dict[str, str]]],
    aggregate: dict[str, int],
    universe_audit: dict[str, Any],
    truncation_audit: dict[str, Any],
    dry_run: bool,
    article_provenance_path: Path | None,
) -> dict[str, Any]:
    invalid_records = [record for record in file_records if record["invalid_source_file_count"] > 0]
    relative_path_presence = build_relative_path_presence(file_records)
    return {
        "artifact_type": "alphavantage_news_raw_root_non_destructive_merge_audit",
        "generated_at_utc": generated_at.isoformat().replace("+00:00", "Z"),
        "status": "dry_run_completed" if dry_run else "completed",
        "dry_run": dry_run,
        "source_roots": [{"label": source.label, "root": str(source.root)} for source in sources],
        "run_root": str(run_root),
        "merged_alphavantage_root": str(merged_root),
        "manifest_dir": str(manifest_dir),
        "article_provenance_path": None if article_provenance_path is None else str(article_provenance_path),
        "canonical_source_untouched": True,
        "source_roots_untouched": True,
        "zone_identifier_sidecars_skipped_count": len(skipped_zone_sidecars),
        "zone_identifier_sidecars_skipped_sample": skipped_zone_sidecars[:25],
        "source_audits": source_audits,
        "news_relative_path_presence": relative_path_presence,
        "input_news_files": sum(item["news_file_count"] for item in source_audits),
        "valid_news_files": sum(item["valid_news_file_count"] for item in source_audits),
        "invalid_news_files": sum(item["invalid_news_file_count"] for item in source_audits),
        "invalid_news_file_records": invalid_records[:100],
        "output_news_files": aggregate["valid_output_file_count"],
        "aggregate": aggregate,
        "duplicate_file_hash_group_count": len(duplicate_file_hash_groups),
        "duplicate_file_hash_duplicate_instances": sum(len(group) - 1 for group in duplicate_file_hash_groups),
        "duplicate_file_hash_groups_sample": duplicate_file_hash_groups[:25],
        "support_file_count": len(support_file_records),
        "support_files_sample": support_file_records[:25],
        "universe_coverage_audit": universe_audit,
        "truncation_audit": truncation_audit,
        "non_claims": [
            "not_a_live_provider_call",
            "not_a_benchmark_result",
            "not_a_model_training_or_prediction_artifact",
            "canonical_data_raw_alphavantage_not_overwritten",
        ],
    }


def build_relative_path_presence(file_records: list[dict[str, Any]]) -> dict[str, Any]:
    only_by_source: dict[str, int] = defaultdict(int)
    shared_count = 0
    conflicting_shared_count = 0
    for record in file_records:
        source_labels = sorted({item["source_label"] for item in record["source_files"]})
        if len(source_labels) == 1:
            only_by_source[source_labels[0]] += 1
        else:
            shared_count += 1
            if record["source_file_hash_unique_count"] > 1:
                conflicting_shared_count += 1
    return {
        "relative_path_count": len(file_records),
        "only_by_source": dict(sorted(only_by_source.items())),
        "shared_relative_path_count": shared_count,
        "shared_relative_paths_with_different_file_hashes": conflicting_shared_count,
    }


def read_universe_tickers(universe_file: Path) -> list[str]:
    if not universe_file.exists():
        return []
    lines = universe_file.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    header = [part.strip() for part in lines[0].split(",")]
    ticker_index = header.index("ticker") if "ticker" in header else 0
    tickers: list[str] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(",")]
        if ticker_index < len(parts) and parts[ticker_index]:
            tickers.append(parts[ticker_index])
    return tickers


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def object_hash(payload: Any) -> str:
    return sha256_text(canonical_json_text(payload))


def canonical_json_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
        return
    print(f"status={summary['status']}")
    print(f"run_root={summary['run_root']}")
    print(f"merged_alphavantage_root={summary['merged_alphavantage_root']}")
    print(f"input_news_files={summary['input_news_files']} valid={summary['valid_news_files']} invalid={summary['invalid_news_files']}")
    print(f"output_news_files={summary['output_news_files']}")
    print(f"source_feed_rows={summary['aggregate']['source_feed_rows']} merged_feed_rows={summary['aggregate']['merged_feed_rows']}")
    print(f"exact_duplicate_article_rows_removed={summary['aggregate']['exact_duplicate_article_rows_removed']}")
    print(f"identity_collision_groups_preserved={summary['aggregate']['identity_collision_groups_preserved']}")
    print(f"zone_identifier_sidecars_skipped_count={summary['zone_identifier_sidecars_skipped_count']}")
    print(f"likely_truncated_output_file_count={summary['truncation_audit']['likely_truncated_output_file_count']}")
    print(f"empty_output_file_count={summary['truncation_audit']['empty_output_file_count']}")
    coverage = summary["universe_coverage_audit"]
    print(
        "annual_current_coverage="
        f"{coverage['present_annual_current_window_count']}/{coverage['expected_annual_current_window_count']} "
        f"missing={coverage['missing_annual_current_window_count']}"
    )


if __name__ == "__main__":
    sys.exit(main())
