# AgentCompliance.md

## 0. Purpose

This file defines the automated compliance layer for the repository governance system.

Its purpose is to reduce cognitive burden **without weakening governance** by turning critical structural, naming, pathing, and hard-gate expectations into mechanically checkable requirements.

This file does **not** replace human judgment.
This file does **not** replace `AgentRules.md`.
This file does **not** decide theory quality, design quality, or scientific merit.

It defines:

- what governance artifacts must exist
- what governance sections must remain present
- what appendix references must remain valid
- what path conventions must remain consistent
- what interaction-log files must remain structurally valid
- what glossary and template dependencies must remain intact
- what validator behavior is required
- what the compliance layer may check automatically
- what the compliance layer must leave to human judgment

This file is binding wherever `AgentRules.md` invokes the compliance layer.

---

## 1. Compliance Layer Mission

The compliance layer exists to protect the repository from silent governance erosion.

It must help detect:

- missing governance files
- broken path migrations
- lost core sections
- missing appendix references
- missing glossary anchors
- broken interaction-log structure
- malformed NDJSON event streams
- silent weakening of hard-gate protections
- incomplete benchmark-governance coverage
- accidental drift between constitution, runbook, templates, and validator

The compliance layer is successful only if it makes governance **more enforceable** while preserving or improving:

- source-of-truth hierarchy
- dependency-chain discipline
- documentation-first discipline
- contradiction visibility
- explicit approval discipline
- benchmark integrity
- evidence-gated completion
- interaction-log stewardship
- fresh-start reconstruction reliability
- self-update safety

---

## 2. Binding Governance Files

At minimum, the compliance layer must require the existence of these files:

- `AgentRules.md`
- `docs/agent/AgentMemory.md`
- `docs/agent/AgentGlossary.md`
- `docs/agent/AgentTemplates.md`
- `docs/agent/AgentResearchWorkflows.md`
- `docs/agent/AgentAppendices.md`
- `docs/agent/AgentCompliance.md`
- `docs/agent/agent_log/Current_State.md`
- `docs/agent/agent_log/Event_Ledger.ndjson`
- `scripts/validate_agent_governance.py`

If one of these is intentionally renamed in the future, the constitution, this file, the appendix map, and the validator must all be updated together.

No silent renames are allowed.

---

## 3. Governance Layers the Compliance System Must Protect

The compliance layer must protect the integrity of the following governance structure.

### 3.1 Constitutional core

- `AgentRules.md`

This must remain the binding constitutional core.

### 3.2 Operational continuity layer

- `docs/agent/AgentMemory.md`
- `docs/agent/agent_log/Current_State.md`
- `docs/agent/agent_log/Event_Ledger.ndjson`

These must remain the continuity and audit subsystem.

### 3.3 Canonical support appendices

- `docs/agent/AgentGlossary.md`
- `docs/agent/AgentTemplates.md`
- `docs/agent/AgentAppendices.md`
- `docs/agent/AgentCompliance.md`

These must remain supporting but binding where invoked.

### 3.4 Mechanical enforcement layer

- `scripts/validate_agent_governance.py`

This must remain the executable checker for inspectable governance conditions.

---

## 4. Required Path Convention

The authoritative governance structure uses:

- `docs/agent/AgentMemory.md`
- `docs/agent/AgentGlossary.md`
- `docs/agent/AgentTemplates.md`
- `docs/agent/AgentAppendices.md`
- `docs/agent/AgentCompliance.md`
- `docs/agent/agent_log/Current_State.md`
- `docs/agent/agent_log/Event_Ledger.ndjson`

Legacy pathing under `docs/agent_log/` must not remain in active governance files unless a deliberate compatibility shim exists and is explicitly documented.

By default, the validator must treat active unapproved legacy references as compliance failures.

---

## 5. Compliance Scope

The compliance layer must check **inspectable governance conditions** only.

That means it must verify structure, presence, references, schemas, and required hard-gate phrases where appropriate.

It must not claim to fully validate:

- scientific correctness
- methodological correctness
- benchmark fairness in the research sense
- whether a recommendation is intellectually best
- whether human judgment calls are wise

Those remain human-governed and constitution-governed responsibilities.

---

## 6. Minimum Validator Responsibilities

The validator script must check all of the following.

### 6.1 Required file existence

It must verify that all required governance files exist.

### 6.2 Core section presence in `AgentRules.md`

It must verify that the strengthened constitutional core still includes clearly detectable sections or markers for at least:

- purpose
- core dependency chain
- forbidden reversals
- mandatory interpretation
- immutable rules
- interaction-log and memory
- update triggers and change propagation
- fresh-start reconstruction
- source-of-truth hierarchy
- required layered files and governance integrity
- contradiction resolution protocol
- explicit user approval gates
- benchmark invalidation and comparability rules
- appendices and templates
- maintenance and staleness discipline
- self-update rules
- final non-negotiable rule

The validator may use exact headings, stable anchor phrases, or a defined marker strategy, but the check must be explicit and stable.

### 6.3 Core hard-gate phrase preservation

It must verify the continued presence of critical anti-erosion phrases or their exact approved equivalents, including at minimum:

- `Not evidenced in repository materials.`
- `Plausible but unverified.`
- `Uncertain, verify manually.`
- `Immutable Task Contract`
- `Approval gates`
- `fully comparable`
- `partially comparable`
- `not comparable`
- `invalidated`

These checks are required because removing such phrases can silently weaken governance behavior.

### 6.4 Appendix reference integrity

It must verify that `AgentRules.md` references all required appendices and that those referenced appendix files actually exist.

At minimum:

- `AgentMemory.md`
- `AgentGlossary.md`
- `AgentTemplates.md`
- `AgentAppendices.md`
- `AgentCompliance.md`

### 6.5 Path consistency

It must verify that active governance files do not silently reference deprecated `docs/agent_log/` paths when the authoritative structure is `docs/agent/...` and `docs/agent/agent_log/...`.

### 6.6 Glossary presence and integrity

It must verify that the glossary exists and includes, at minimum, canonical entries for:

- Meaningful change
- Evidence pointer
- Immutable Task Contract
- Approval gate
- Drift checkpoint
- Session
- Benchmark comparability change
- Stage completion
- Stale-risk

### 6.7 Template pack coverage

It must verify that the template pack contains inspectable templates for at least:

- task register entry
- approval request
- approval outcome
- contradiction detection
- contradiction resolution
- evidence record
- benchmark invalidation or comparability record
- session reconciliation
- drift checkpoint
- stage completion or completion basis check

### 6.8 Interaction-log file structure

It must verify that:

- `Current_State.md` exists
- `Event_Ledger.ndjson` exists
- `Current_State.md` contains the required major sections
- `Event_Ledger.ndjson` is valid NDJSON
- each non-empty ledger line is valid JSON

### 6.9 Inspectable DONE-evidence rule

Where inspectable from `Current_State.md`, the validator should check that entries marked done are not obviously missing evidence pointers.

If the file format is too free-form for perfect parsing, the validator must at least perform a conservative detectable check and report limitations clearly.

### 6.10 Self-consistency between compliance spec and validator

If this file requires a check that is mechanically inspectable, the validator should implement it.
If the validator does not implement it, the omission must be intentional, explicit, and documented in the script.

---

## 7. Optional Advanced Validator Responsibilities

The validator may additionally check:

- whether `AgentRules.md` references benchmark comparability labels explicitly
- whether `AgentMemory.md` preserves the session-ending procedure
- whether required glossary terms appear in relevant governing files
- whether required appendix-loading statements remain present
- whether the validator file itself is listed in required files
- whether `Current_State.md` appears to be missing mandatory subsections under the Task Register
- whether obviously empty governance files exist where non-empty structure is expected

Optional advanced checks must remain conservative.
False authority claims are forbidden.

---

## 8. What the Validator Must Not Claim

The validator must not pretend to validate what it cannot truly inspect.

It must not claim certainty about:

- scientific soundness
- design quality
- whether a contradiction was resolved correctly in substance
- whether a benchmark claim is intellectually fair beyond inspectable metadata
- whether a completion claim is truly correct when evidence semantics are too complex to infer automatically
- whether the best architectural choice was made

The validator may flag structural suspicion.
It must not fake substantive certainty.

---

## 9. Current_State.md Structural Compliance Rules

The compliance layer must require `Current_State.md` to contain at least:

- `# Current State (Operational Memory)`
- `Last updated:`
- `## Immutable Task Contract (USER-APPROVED)`
- `## Current Priorities`
- `## Task Register`
- `## Decisions and Approvals Index (REFERENCE-ONLY)`
- `## Open Questions for User`
- `## Last Session Delta`
- `## Drift / Staleness Flags`

It should also verify that the Immutable Task Contract section is present and non-empty enough to be operationally meaningful where inspectable.

The validator must not require exact sentence wording for user-derived content, only structural integrity and core field presence where practical.

---

## 10. Event_Ledger.ndjson Structural Compliance Rules

The compliance layer must require that each non-empty line in `Event_Ledger.ndjson` is valid JSON.

Where practical, it should also check for presence of required fields such as:

- `event_id`
- `timestamp_utc`
- `event_type`
- `severity`
- `session_id`
- `request_id`
- `task_ids`
- `summary`
- `details`
- `evidence`
- `source`
- `trust`
- `links`

If a line is valid JSON but missing required keys, that is a compliance failure.

The compliance layer must also preserve the append-only expectation conceptually, but note that automated append-only verification may require repository history integration and is not fully guaranteed by a local file-only validator.

---

## 11. Compliance Severity Model

Compliance failures should be reported with severity categories.

Suggested categories:

- `ERROR`
  - missing required file
  - invalid NDJSON
  - missing core constitutional section
  - legacy path still present in active governance files
  - missing interaction-log required sections
  - missing required appendix references

- `WARNING`
  - optional advanced check not satisfied
  - likely weak DONE-evidence formatting
  - partially missing glossary coverage
  - likely stale appendix reference

- `INFO`
  - compliant but notable
  - intentionally skipped advanced checks
  - validator limitations

The validator must not downgrade serious structural failures to warnings.

---

## 12. Compliance Output Requirements

When the validator runs, it should output:

1. overall pass/fail result
2. each failure or warning on its own line
3. enough detail to identify:
   - which file failed
   - what condition failed
   - what the expected condition was

The validator output must be concise and operational.
It must not dump excessive internal detail.

---

## 13. Change Management for the Compliance Layer

Any meaningful change to this file must trigger review of:

- `AgentRules.md`
- `AgentMemory.md`
- `AgentTemplates.md`
- `AgentGlossary.md`
- `AgentAppendices.md`
- `scripts/validate_agent_governance.py`

Reason:
the compliance layer is not safe if the spec and the validator drift apart.

A governance change to the compliance layer should be logged as a governance event.

---

## 14. Appendix Interaction Rules

This file depends on the following appendix relationships.

### 14.1 With `AgentRules.md`

`AgentRules.md` defines what the compliance layer must protect.

### 14.2 With `AgentMemory.md`

`AgentMemory.md` defines interaction-log behavior that the validator may partly inspect structurally.

### 14.3 With `AgentGlossary.md`

The glossary defines the canonical meaning of critical governance terms used in compliance interpretation.

### 14.4 With `AgentTemplates.md`

Templates define what canonical governance action records should look like.
The validator may inspect template presence, not the wisdom of their future use.

### 14.5 With `AgentResearchWorkflows.md`

The research-workflow appendix defines repository-first literature, paper-verification, and non-winner comparison procedures.
The validator may inspect that the appendix exists and that core references remain consistent.

### 14.6 With `AgentAppendices.md`

The appendix map must explain when appendices are binding and how they are loaded.
The validator may check that appendix references remain consistent.

---

## 15. Validator Evolution Rules

The validator should evolve when one of the following happens:

- the governance file set changes
- the path structure changes
- the constitutional core gains a new inspectable hard gate
- the interaction-log schema changes
- a missing automated check caused a real governance failure
- glossary or template dependencies become stronger and inspectable

The validator must not be expanded just to look “smart.”
It should only gain checks that are stable, meaningful, and inspectable.

---

## 16. Minimal CI Readiness Rule

The compliance layer must be written so that the validator can be run manually now and integrated into CI later without redesigning the governance spec.

That means:

- stable file paths
- stable check definitions
- deterministic validator output
- no dependence on hidden runtime state for the basic checks

A full CI workflow is optional, but the compliance layer must remain compatible with future CI integration.

---

## 17. Final Rule

The compliance layer exists to make governance harder to weaken silently.

If a proposed simplification removes enforceability, obscures authority, weakens hard gates, or makes appendix loading ambiguous, the compliance layer must treat that simplification as a governance regression, not an improvement.
