from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = PROJECT_ROOT / "docs" / "Prompts" / "v1p0_Stage47_Lockbox_Portfolio_Simulation.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_stage47_prompt_declares_roster_and_stale_artifact_guards() -> None:
    text = _read(PROMPT_PATH)

    assert "# v1p0 Stage 47 Prompt: Lockbox Portfolio Simulation" in text
    assert "historical, lockbox-only, non-claim portfolio simulation" in text
    assert "all valid best individual models plus the best valid mixed model" in text
    assert "updated_av_xgboost_event_market_optuna_v1" in text
    assert "updated_av_tsmixer_event_market_optuna_v1_seed_mean" in text
    assert "current frozen Stage 44 TSMixer diagnostic input" in text
    assert "no-direct-TSMixer-tuning horizon mixer" in text
    assert "Do not run stale Stage 45 meta predictions as the final mixed model" in text
    assert "blocked_missing_or_schema_incompatible" in text


def test_stage47_prompt_locks_fold_mean_constant_skip_and_1d_sell_pressure() -> None:
    text = _read(PROMPT_PATH)

    assert "Collapse duplicate fold predictions by fold-mean" in text
    assert "Skip any model/date/horizon where the cross-section is constant" in text
    assert "Do not fabricate tie-broken top-k or bot-k lists" in text
    assert "Sell pressure is always `1d` bot-k only." in text
    assert "Non-1d bot-k lists, including `5d`, `10d`, `20d`, and `60d`, are diagnostics-only and must not trigger liquidation." in text
    assert "If the `1d` horizon is constant or skipped for a model/date, there is no bot-k sell pressure" in text


def test_stage47_decision_docs_record_portfolio_policy() -> None:
    architecture = _read(PROJECT_ROOT / "ArchitecturalDesignDecisions.md")
    roadmap = _read(PROJECT_ROOT / "docs" / "NextSteps_Brainstorming.md")

    assert "## 8A. Stage 47 Lockbox Portfolio Simulation Decisions" in architecture
    assert "Current Stage 43 XGBoost is valid" in architecture
    assert "current frozen Stage 44 TSMixer may be used as a diagnostic input only" in architecture
    assert "Stage 45 XGBoost+TSMixer meta remains stale historical evidence" in architecture
    assert "`one_d_bot10`, `none`, `botk_4_of_5`, `botk_3_of_5`, and `botk_2_of_5`" in architecture
    assert "### Decision 38: Lockbox Portfolio Simulation Diagnostic Stage" in roadmap
    assert "liquidation pressure is always the model's non-constant `1d` bot-k list" in roadmap
    assert "Bot-k lists for `5d`, `10d`, `20d`, `60d`, or any non-1d horizon are diagnostics-only" in roadmap
    assert "no direct TSMixer tuning is allowed" in roadmap
    assert "at least 4 of 5 horizons" in roadmap


def test_stage47_status_register_tracks_prompt_as_completed_current() -> None:
    status_register = _read(PROJECT_ROOT / "docs" / "Prompts" / "v1p0_Prompt_Status_Register.md")

    assert "| 47 | `v1p0_Stage47_Lockbox_Portfolio_Simulation.md` | completed_current |" in status_register
    assert "Post-selection diagnostic only; no trading/product/claim scope." in status_register
    assert "Stage 48 frozen-TSMixer horizon mixer completed 800/800 meta/mixer trials" in status_register
