#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


REQUIRED_FILES = [
    "AgentRules.md",
    "docs/agent/AgentMemory.md",
    "docs/agent/AgentGlossary.md",
    "docs/agent/AgentTemplates.md",
    "docs/agent/AgentResearchWorkflows.md",
    "docs/agent/AgentAppendices.md",
    "docs/agent/AgentCompliance.md",
    "docs/agent/agent_log/Current_State.md",
    "docs/agent/agent_log/Event_Ledger.ndjson",
    "scripts/validate_agent_governance.py",
]

AGENT_RULES_REQUIRED_MARKERS = [
    "## 0. Purpose",
    "## 1. Core Dependency Chain",
    "### 1.1 Forbidden reversals",
    "### 1.2 Mandatory interpretation",
    "## 2. Immutable Rules",
    "## 3. Interaction-Log and Memory",
    "## 4. Update Triggers and Change Propagation",
    "## 5. Fresh-Start Reconstruction",
    "## 6. Source-of-Truth Hierarchy",
    "## 7. Required Layered Files and Governance Integrity",
    "## 8. Contradiction Resolution Protocol",
    "## 9. Explicit User Approval Gates",
    "## 10. Benchmark Invalidation and Comparability Rules",
    "## 11. Appendices and Templates",
    "## 12. Maintenance and Staleness Discipline",
    "## 13. Self-Update Rules",
    "## 14. Final Non-Negotiable Rule",
]

AGENT_RULES_HARD_GATE_PHRASES = [
    "Not evidenced in repository materials.",
    "Plausible but unverified.",
    "Uncertain, verify manually.",
    "Immutable Task Contract",
    "Approval gates",
    "fully comparable",
    "partially comparable",
    "not comparable",
    "invalidated",
]

AGENT_MEMORY_REQUIRED_MARKERS = [
    "# 0. Scope and Authority",
    "# 1. Required Files and Their Meanings",
    "# 2. Source-of-Truth Relationship Inside the Interaction-Log Subsystem",
    "# 3. Non-Negotiable Global Rules",
    "# 4. Update Triggers",
    "# 6. ID Governance",
    "# 7. Event Taxonomy",
    "# 8. Required Ledger Object Schema",
    "# 9. Current_State.md Governance Rules",
    "# 10. Fresh-Start Reconstruction Procedure",
    "# 12. Benchmark and Comparability Logging Rules",
    "# 13. Correction Procedure",
    "# 14. Canonical Templates",
    "# 15. Session-Ending Procedure (Mandatory)",
    "# 17. Self-Update Restrictions for This File",
    "# 18. Final Rule",
]

AGENT_GLOSSARY_REQUIRED_TERMS = [
    "### 2.1 Meaningful change",
    "### 2.2 Evidence pointer",
    "### 2.4 Stage completion",
    "### 2.5 Stale-risk",
    "### 2.6 Benchmark comparability change",
    "### 2.8 Immutable Task Contract",
    "### 2.9 Approval gate",
    "### 2.10 Drift checkpoint",
    "### 2.11 Session",
]

AGENT_TEMPLATES_REQUIRED_MARKERS = [
    "## 2. Task and Planning Templates",
    "### 2.1 Task Register Entry",
    "## 3. Approval and Decision Templates",
    "### 3.1 Approval Request Template",
    "### 3.2 Approval Outcome Record",
    "## 4. Contradiction and Correction Templates",
    "### 4.1 Contradiction Detection Record",
    "### 4.2 Contradiction Resolution Record",
    "## 5. Evidence and Completion Templates",
    "### 5.1 Evidence Record",
    "### 5.2 Completion Basis Check",
    "## 6. Test and Benchmark Templates",
    "### 6.3 Benchmark Invalidation / Comparability Record",
    "### 6.5 Method / Technique Comparison Profile",
    "### 6.7 Paper Verification Record",
    "## 7. Session and Drift Templates",
    "### 7.1 Reconciliation Block",
    "### 7.2 Drift Checkpoint Block",
]

AGENT_RESEARCH_WORKFLOWS_REQUIRED_MARKERS = [
    "## 0. Purpose",
    "## 1. Scope and Authority",
    "## 2. When This Appendix Is Binding",
    "## 3. Repository-First Research Workflow",
    "## 4. Additive Research Documentation Rule",
    "## 5. Triple-Verification Literature Rule",
    "## 6. Comparison Framework Rule",
    "## 7. Similarity and Tie Handling Rule",
    "## 8. Research Comparison Output Rules",
    "## 9. Paper-Note Workflow",
    "## 10. Self-Update Restrictions",
    "## 11. Final Rule",
]

AGENT_COMPLIANCE_REQUIRED_MARKERS = [
    "## 0. Purpose",
    "## 1. Compliance Layer Mission",
    "## 2. Binding Governance Files",
    "## 4. Required Path Convention",
    "## 5. Compliance Scope",
    "## 6. Minimum Validator Responsibilities",
    "## 8. What the Validator Must Not Claim",
    "## 9. Current_State.md Structural Compliance Rules",
    "## 10. Event_Ledger.ndjson Structural Compliance Rules",
    "## 11. Compliance Severity Model",
    "## 12. Compliance Output Requirements",
    "## 15. Validator Evolution Rules",
    "## 17. Final Rule",
]

AGENT_APPENDICES_REQUIRED_MARKERS = [
    "## 0. Purpose",
    "## 1. Appendix System Principles",
    "## 2. Authoritative Appendix Set",
    "## 3. Authority and Responsibility of Each Appendix",
    "## 4. Mandatory Reading and Loading Order",
    "## 5. Always-Required vs Conditionally-Required Appendix Matrix",
    "## 6. Action-to-Appendix Loading Map",
    "## 7. Appendix Neglect Prevention Rules",
    "## 8. Appendix Boundary Rules",
    "## 9. Rules for Adding a New Appendix",
    "## 10. Rules for Removing, Merging, or Renaming an Appendix",
    "## 11. Compatibility and Path Migration Rules",
    "## 14. Appendix Loading Failure Conditions",
    "## 15. Final Rule",
]

CURRENT_STATE_REQUIRED_MARKERS = [
    "# Current State (Operational Memory)",
    "Last updated:",
    "## Immutable Task Contract (USER-APPROVED)",
    "## Current Priorities",
    "## Task Register",
    "## Decisions and Approvals Index (REFERENCE-ONLY)",
    "## Open Questions for User",
    "## Last Session Delta",
    "## Drift / Staleness Flags",
]

EVENT_LEDGER_REQUIRED_KEYS = [
    "event_id",
    "timestamp_utc",
    "event_type",
    "severity",
    "session_id",
    "request_id",
    "task_ids",
    "summary",
    "details",
    "evidence",
    "source",
    "trust",
    "links",
]

APPENDIX_REFERENCE_NAMES = [
    "AgentMemory.md",
    "AgentGlossary.md",
    "AgentTemplates.md",
    "AgentResearchWorkflows.md",
    "AgentAppendices.md",
    "AgentCompliance.md",
]

ACTIVE_GOVERNANCE_FILES = [
    "AgentRules.md",
    "docs/agent/AgentMemory.md",
    "docs/agent/AgentGlossary.md",
    "docs/agent/AgentTemplates.md",
    "docs/agent/AgentResearchWorkflows.md",
    "docs/agent/AgentAppendices.md",
    "docs/agent/AgentCompliance.md",
]

LEGACY_PATH = "docs/agent_log/"
ACTIVE_PATH_EXPECTATIONS = [
    "docs/agent/AgentMemory.md",
    "docs/agent/agent_log/Current_State.md",
    "docs/agent/agent_log/Event_Ledger.ndjson",
]

LEGACY_PATH_ALLOWED_FILES = {
    "docs/agent/AgentCompliance.md",
    "docs/agent/AgentAppendices.md",
}


@dataclass
class Finding:
    severity: str
    message: str


@dataclass
class ValidatorState:
    findings: list[Finding] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.findings.append(Finding("ERROR", message))

    def warning(self, message: str) -> None:
        self.findings.append(Finding("WARNING", message))

    def info(self, message: str) -> None:
        self.findings.append(Finding("INFO", message))

    def has_errors(self) -> bool:
        return any(item.severity == "ERROR" for item in self.findings)


def read_text(path: Path, state: ValidatorState) -> str | None:
    if not path.exists():
        state.error(f"Missing file: {path.as_posix()}")
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        state.error(f"Could not read {path.as_posix()}: {exc}")
        return None


def require_markers(
    text: str | None,
    file_path: str,
    markers: Iterable[str],
    state: ValidatorState,
) -> None:
    if text is None:
        return
    for marker in markers:
        if marker not in text:
            state.error(f"{file_path} missing required marker: {marker}")


def require_substrings(
    text: str | None,
    file_path: str,
    substrings: Iterable[str],
    state: ValidatorState,
) -> None:
    if text is None:
        return
    for value in substrings:
        if value not in text:
            state.error(f"{file_path} missing required reference or phrase: {value}")


def validate_required_files(repo_root: Path, state: ValidatorState) -> None:
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).exists():
            state.error(f"Missing file: {rel_path}")


def validate_no_legacy_paths(repo_root: Path, state: ValidatorState) -> None:
    for rel_path in ACTIVE_GOVERNANCE_FILES:
        text = read_text(repo_root / rel_path, state)
        if text is None:
            continue
        if LEGACY_PATH in text and rel_path not in LEGACY_PATH_ALLOWED_FILES:
            state.error(f"Legacy path '{LEGACY_PATH}' found in {rel_path}")
    # Also ensure the core uses the active paths explicitly.
    core_text = read_text(repo_root / "AgentRules.md", state)
    require_substrings(core_text, "AgentRules.md", ACTIVE_PATH_EXPECTATIONS, state)


def validate_agent_rules(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "AgentRules.md"
    text = read_text(path, state)
    require_markers(text, "AgentRules.md", AGENT_RULES_REQUIRED_MARKERS, state)
    require_substrings(text, "AgentRules.md", AGENT_RULES_HARD_GATE_PHRASES, state)
    require_substrings(text, "AgentRules.md", APPENDIX_REFERENCE_NAMES, state)
    if text is None:
        return
    if "Theory -> Design -> Code -> Tests and Benchmarks -> Update and Retraining Operations" not in text:
        state.error("AgentRules.md missing exact dependency-chain statement")
    if "docs/agent/AgentMemory.md" not in text or "docs/agent/agent_log/Event_Ledger.ndjson" not in text:
        state.error("AgentRules.md does not fully declare the active interaction-log subsystem")
    if "Appendices do not override this constitution." not in text:
        state.error("AgentRules.md missing appendix non-override protection")


def validate_agent_memory(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "docs/agent/AgentMemory.md"
    text = read_text(path, state)
    require_markers(text, path.as_posix().replace(str(repo_root) + "/", ""), AGENT_MEMORY_REQUIRED_MARKERS, state)
    if text is None:
        return
    require_substrings(
        text,
        "docs/agent/AgentMemory.md",
        [
            "docs/agent/agent_log/Current_State.md",
            "docs/agent/agent_log/Event_Ledger.ndjson",
            "Scope_change_proposed",
            "Drift_Checkpoint",
            "R-YYYY-MM-DD-####",
            "T-YYYY-MM-DD-####",
            "E-YYYY-MM-DD-####",
            "S-YYYY-MM-DD-####",
        ],
        state,
    )


def validate_agent_glossary(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "docs/agent/AgentGlossary.md"
    text = read_text(path, state)
    require_markers(text, "docs/agent/AgentGlossary.md", AGENT_GLOSSARY_REQUIRED_TERMS, state)


def validate_agent_templates(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "docs/agent/AgentTemplates.md"
    text = read_text(path, state)
    require_markers(text, "docs/agent/AgentTemplates.md", AGENT_TEMPLATES_REQUIRED_MARKERS, state)
    if text is None:
        return
    if "### USER INPUT REQUIRED" not in text:
        state.error("docs/agent/AgentTemplates.md missing approval gate prompt body marker")


def validate_agent_research_workflows(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "docs/agent/AgentResearchWorkflows.md"
    text = read_text(path, state)
    require_markers(text, "docs/agent/AgentResearchWorkflows.md", AGENT_RESEARCH_WORKFLOWS_REQUIRED_MARKERS, state)
    if text is None:
        return
    require_substrings(
        text,
        "docs/agent/AgentResearchWorkflows.md",
        [
            "Not evidenced in repository materials.",
            "Plausible but unverified.",
            "Uncertain, verify manually.",
            "three independent sources",
            "at least one primary or official source",
            "no single overall score",
            "higher still means better",
        ],
        state,
    )


def validate_agent_compliance(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "docs/agent/AgentCompliance.md"
    text = read_text(path, state)
    require_markers(text, "docs/agent/AgentCompliance.md", AGENT_COMPLIANCE_REQUIRED_MARKERS, state)
    require_substrings(text, "docs/agent/AgentCompliance.md", REQUIRED_FILES, state)


def validate_agent_appendices(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "docs/agent/AgentAppendices.md"
    text = read_text(path, state)
    require_markers(text, "docs/agent/AgentAppendices.md", AGENT_APPENDICES_REQUIRED_MARKERS, state)
    require_substrings(text, "docs/agent/AgentAppendices.md", APPENDIX_REFERENCE_NAMES, state)


def validate_current_state(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "docs/agent/agent_log/Current_State.md"
    text = read_text(path, state)
    require_markers(text, "docs/agent/agent_log/Current_State.md", CURRENT_STATE_REQUIRED_MARKERS, state)
    if text is None:
        return

    # Conservative done-evidence check.
    lines = text.splitlines()
    task_blocks: list[list[str]] = []
    current_block: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- Task ID:"):
            if current_block:
                task_blocks.append(current_block)
            current_block = [stripped]
        elif current_block:
            if stripped.startswith("- Task ID:"):
                task_blocks.append(current_block)
                current_block = [stripped]
            else:
                current_block.append(stripped)
    if current_block:
        task_blocks.append(current_block)

    for block in task_blocks:
        block_text = "\n".join(block)
        status_match = re.search(r"- Status:\s*(.+)", block_text)
        evidence_match = re.search(r"- Evidence pointers:\s*(.*)", block_text)
        if status_match:
            status_value = status_match.group(1).strip().lower()
            evidence_value = evidence_match.group(1).strip() if evidence_match else ""
            if status_value == "done" and not evidence_value:
                task_id_match = re.search(r"- Task ID:\s*(.+)", block_text)
                task_id = task_id_match.group(1).strip() if task_id_match else "<unknown>"
                state.error(
                    f"docs/agent/agent_log/Current_State.md has DONE task without evidence pointers: {task_id}"
                )


def validate_event_ledger(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "docs/agent/agent_log/Event_Ledger.ndjson"
    if not path.exists():
        state.error(f"Missing file: {path.as_posix()}")
        return

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        state.error(f"Could not read {path.as_posix()}: {exc}")
        return

    seen_event_ids: set[str] = set()
    for index, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            state.error(f"Invalid JSON in {path.as_posix()} line {index}: {exc}")
            continue

        for key in EVENT_LEDGER_REQUIRED_KEYS:
            if key not in data:
                state.error(f"{path.as_posix()} line {index} missing required key: {key}")

        event_id = data.get("event_id")
        if isinstance(event_id, str):
            if event_id in seen_event_ids:
                state.error(f"Duplicate event_id in {path.as_posix()}: {event_id}")
            seen_event_ids.add(event_id)

        severity = data.get("severity")
        if severity not in {"INFO", "MINOR", "MAJOR", "CRITICAL"}:
            state.error(
                f"{path.as_posix()} line {index} has invalid severity: {severity}"
            )

        trust = data.get("trust")
        if trust not in {"trusted", "untrusted", "mixed"}:
            state.error(f"{path.as_posix()} line {index} has invalid trust value: {trust}")

        if data.get("event_type") == "Task_completed":
            evidence = data.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                state.error(
                    f"{path.as_posix()} line {index} marks Task_completed without evidence"
                )


def validate_validator_self_alignment(repo_root: Path, state: ValidatorState) -> None:
    path = repo_root / "scripts/validate_agent_governance.py"
    text = read_text(path, state)
    if text is None:
        return
    if "REQUIRED_FILES" not in text:
        state.error("scripts/validate_agent_governance.py missing REQUIRED_FILES definition")
    if "LEGACY_PATH" not in text:
        state.warning("scripts/validate_agent_governance.py missing explicit legacy-path constant")
    if "Current_State.md" not in text or "Event_Ledger.ndjson" not in text:
        state.warning("scripts/validate_agent_governance.py may not fully validate interaction-log files")


def emit_report(state: ValidatorState) -> int:
    errors = [item for item in state.findings if item.severity == "ERROR"]
    warnings = [item for item in state.findings if item.severity == "WARNING"]
    infos = [item for item in state.findings if item.severity == "INFO"]

    if errors:
        print("VALIDATION FAILED")
    else:
        print("VALIDATION PASSED")

    for item in errors + warnings + infos:
        print(f"{item.severity}: {item.message}")

    return 1 if errors else 0


def main() -> int:
    repo_root = Path.cwd()
    state = ValidatorState()

    validate_required_files(repo_root, state)
    validate_no_legacy_paths(repo_root, state)
    validate_agent_rules(repo_root, state)
    validate_agent_memory(repo_root, state)
    validate_agent_glossary(repo_root, state)
    validate_agent_templates(repo_root, state)
    validate_agent_research_workflows(repo_root, state)
    validate_agent_compliance(repo_root, state)
    validate_agent_appendices(repo_root, state)
    validate_current_state(repo_root, state)
    validate_event_ledger(repo_root, state)
    validate_validator_self_alignment(repo_root, state)

    if not state.findings:
        state.info("All governance checks passed.")
    return emit_report(state)


if __name__ == "__main__":
    sys.exit(main())
