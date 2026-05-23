from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import stage8_data_update_common as stage8_common  # noqa: E402


def test_news_plan_default_writes_manifest_without_provider_calls(tmp_path: Path, monkeypatch) -> None:
    universe_path = _write_universe(tmp_path, ["BRK.B", "MSFT"])
    manifest_path = tmp_path / "manifest.json"
    ledger_path = tmp_path / "ledger.jsonl"

    def fail_execute(*_args, **_kwargs):
        raise AssertionError("plan-only mode must not execute provider calls")

    monkeypatch.setattr(stage8_common, "execute_news_plan", fail_execute)

    status = stage8_common.run_news_update(
        "daily",
        [
            "--universe-file",
            str(universe_path),
            "--raw-root",
            str(tmp_path / "raw" / "alphavantage"),
            "--manifest",
            str(manifest_path),
            "--ledger",
            str(ledger_path),
            "--end-date",
            "2026-05-22",
        ],
    )

    manifest = _read_json(manifest_path)
    assert status == 0
    assert ledger_path.exists() is False
    assert manifest["status"] == "planned_only"
    assert manifest["execute"] is False
    assert manifest["benchmark_claim"] is False
    assert manifest["planned_count"] == 2
    assert manifest["planned_entries"][0]["ticker"] == "BRK.B"
    assert manifest["planned_entries"][0]["request_ticker"] == "BRK-B"
    assert "BRK.B" in manifest["planned_entries"][0]["target_path"]
    assert "not_a_live_trading_signal" in manifest["non_claims"]


def test_existing_news_target_skips_without_overwrite(tmp_path: Path) -> None:
    universe_path = _write_universe(tmp_path, ["MSFT"])
    raw_root = tmp_path / "raw" / "alphavantage"
    existing_target = raw_root / "MSFT" / "news_sentiment__2026-05-16__2026-05-22.json"
    _write_json(existing_target, {"feed": []})
    manifest_path = tmp_path / "manifest.json"

    status = stage8_common.run_news_update(
        "weekly",
        [
            "--universe-file",
            str(universe_path),
            "--raw-root",
            str(raw_root),
            "--manifest",
            str(manifest_path),
            "--end-date",
            "2026-05-22",
        ],
    )

    manifest = _read_json(manifest_path)
    assert status == 0
    assert manifest["planned_count"] == 0
    assert manifest["skipped_existing_count"] == 1
    assert manifest["skipped_existing_entries"][0]["skip_reason"] == "target_exists_no_overwrite"
    assert manifest["raw_write_policy"]["existing_targets_skipped_by_default"] is True


def test_ohlcv_plan_includes_spy_support_and_full_window_target(tmp_path: Path) -> None:
    universe_path = _write_universe(tmp_path, ["AAPL"])
    manifest_path = tmp_path / "manifest.json"

    status = stage8_common.run_ohlcv_update(
        "daily",
        [
            "--universe-file",
            str(universe_path),
            "--raw-root",
            str(tmp_path / "raw" / "twelvedata"),
            "--manifest",
            str(manifest_path),
            "--end-date",
            "2026-05-22",
            "--include-spy",
        ],
    )

    manifest = _read_json(manifest_path)
    assert status == 0
    assert manifest["provider"] == "Twelve Data"
    assert manifest["ticker_count"] == 2
    assert manifest["tickers"] == ["AAPL", "SPY"]
    assert manifest["extra"]["include_spy_support_ticker"] is True
    spy_entry = next(item for item in manifest["planned_entries"] if item["ticker"] == "SPY")
    assert spy_entry["support_ticker"] is True
    assert Path(spy_entry["target_path"]).parts[-2:] == ("SPY", "time_series__2010-01-01__2026-05-22.json")


def test_live_execute_requires_key_and_writes_blocked_manifest(tmp_path: Path, monkeypatch) -> None:
    universe_path = _write_universe(tmp_path, ["AAPL"])
    manifest_path = tmp_path / "manifest.json"
    ledger_path = tmp_path / "ledger.jsonl"
    monkeypatch.delenv("STAGE8_TEST_MISSING_KEY", raising=False)

    status = stage8_common.run_news_update(
        "daily",
        [
            "--universe-file",
            str(universe_path),
            "--raw-root",
            str(tmp_path / "raw" / "alphavantage"),
            "--manifest",
            str(manifest_path),
            "--ledger",
            str(ledger_path),
            "--end-date",
            "2026-05-22",
            "--execute",
            "--api-key-env",
            "STAGE8_TEST_MISSING_KEY",
            "--env-file",
            str(tmp_path / "missing.env"),
        ],
    )

    manifest = _read_json(manifest_path)
    assert status == 2
    assert ledger_path.exists() is False
    assert manifest["status"] == "blocked_missing_api_key"
    assert manifest["api_key_env"] == "STAGE8_TEST_MISSING_KEY"
    assert "apikey" not in json.dumps(manifest).lower()


def test_secret_sanitization_removes_keys_and_redacts_urls() -> None:
    raw = {
        "apikey": "SECRET1",
        "api_key": "SECRET2",
        "token": "SECRET3",
        "key": "SECRET4",
        "nested": [{"url": "https://provider.test/query?apikey=SECRET1&api_key=SECRET2&token=SECRET3&key=SECRET4&symbol=AAPL"}],
    }

    sanitized = stage8_common.sanitize_for_shareable_output(raw)
    serialized = json.dumps(sanitized, sort_keys=True)

    assert "SECRET" not in serialized
    assert "symbol=AAPL" in serialized
    assert serialized.count("REDACTED") == 4


def test_candidate_wrapper_scripts_dispatch_expected_cadences(monkeypatch) -> None:
    calls: list[tuple[str, str, list[str]]] = []

    for script_name, function_name, expected_cadence in [
        ("news_update_daily.py", "run_news_update", "daily"),
        ("news_update_weekly.py", "run_news_update", "weekly"),
        ("OHLCV_daily_update.py", "run_ohlcv_update", "daily"),
        ("OHLCV_weekly_update.py", "run_ohlcv_update", "weekly"),
    ]:
        module = _load_script(script_name)

        def fake_run(cadence: str, argv: list[str] | None = None, *, _script_name: str = script_name) -> int:
            calls.append((_script_name, cadence, list(argv or [])))
            return 17

        monkeypatch.setattr(module, function_name, fake_run)
        assert module.main(["--json"]) == 17

    assert calls == [
        ("news_update_daily.py", "daily", ["--json"]),
        ("news_update_weekly.py", "weekly", ["--json"]),
        ("OHLCV_daily_update.py", "daily", ["--json"]),
        ("OHLCV_weekly_update.py", "weekly", ["--json"]),
    ]


def _load_script(script_name: str) -> ModuleType:
    module_name = f"stage8_wrapper_test_{script_name.replace('.', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS_ROOT / script_name)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_universe(tmp_path: Path, tickers: list[str]) -> Path:
    path = tmp_path / "universe.csv"
    path.write_text("ticker\n" + "\n".join(tickers) + "\n", encoding="utf-8")
    return path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
