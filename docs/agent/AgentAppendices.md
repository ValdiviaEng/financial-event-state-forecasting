# AgentAppendices.md

## 0. Purpose

This file is the appendix authority map for the repository governance system.

Its purpose is to make the distributed governance architecture safe to use by defining:

- which appendices exist
- what each appendix is authoritative for
- when each appendix must be loaded
- which appendices are always required
- which appendices are conditionally required
- how appendix loading interacts with `AgentRules.md`
- how appendix use must remain explicit and auditable
- how to prevent appendix neglect, ambiguity, or silent weakening of core governance

This file is not a second constitution.
It does not override `AgentRules.md`.
It exists to make distributed governance operationally safe and explicit.

Where `AgentRules.md` invokes an appendix, that invoked appendix is binding for the purpose explicitly named by the constitution.

---

## 1. Appendix System Principles

The repository uses a distributed governance system.
That is allowed only if the distribution remains explicit, hierarchical, and non-ambiguous.

The appendix system must follow these principles:

1. **Core-first principle**  
   `AgentRules.md` is always the constitutional entry point.

2. **No silent appendix reliance**  
   An appendix must not become mandatory only through habit or hidden expectation.
   If the appendix is required, the constitution or this file must say so explicitly.

3. **Binding-where-invoked principle**  
   An appendix is binding only for the purposes explicitly assigned to it by the constitutional core or this appendix authority map.

4. **No appendix override principle**  
   No appendix may silently weaken, reinterpret, or override the constitutional core.

5. **Explicit loading principle**  
   A future agent must be able to determine what to read next from rules, not guesswork.

6. **Separation-of-concern principle**  
   Appendices must own distinct governance responsibilities.
   They must not drift into overlapping pseudo-constitutions.

7. **Auditability principle**  
   If an appendix was required for a high-impact action, that dependency should be inferable from the governing files and, where relevant, recordable through the logging system.

---

## 2. Authoritative Appendix Set

The canonical appendix set for the governance system is:

- `docs/agent/AgentMemory.md`
- `docs/agent/AgentGlossary.md`
- `docs/agent/AgentTemplates.md`
- `docs/agent/AgentResearchWorkflows.md`
- `docs/agent/AgentCompliance.md`
- `docs/agent/AgentAppendices.md`

These files together form the appendix layer.
They support the constitutional core but do not replace it.

If future appendices are added, they must be integrated explicitly through:

1. `AgentRules.md`
2. this file
3. the compliance layer if the new appendix becomes structurally important

No silent appendix sprawl is allowed.

---

## 3. Authority and Responsibility of Each Appendix

## 3.1 `docs/agent/AgentMemory.md`

### Authority
This file is the binding operational runbook for the interaction-log and continuity subsystem.

### It is authoritative for
- interaction-log stewardship
- event taxonomy
- request, task, session, and event identity rules
- reconciliation rules
- drift checkpoint rules
- evidence logging rules in the interaction-log layer
- correction handling in the interaction-log layer
- fresh-start continuity reconstruction in the interaction-log layer

### It is not authoritative for
- theory truth
- design truth
- benchmark science
- architecture truth
- code semantics outside continuity tracking

### When it must be loaded
Load `AgentMemory.md` when any of the following occurs:

- a fresh start
- a new user request affecting tracked work
- any task status change
- approval request or approval result
- contradiction affecting tracked execution state
- benchmark event affecting task status or evidence
- session ending reconciliation
- repair of `Current_State.md` or `Event_Ledger.ndjson`

### Loading class
**Always required** for continuity-sensitive work.

---

## 3.2 `docs/agent/AgentGlossary.md`

### Authority
This file is the canonical ambiguity-reduction layer.

### It is authoritative for
- strict meaning of critical governance terms
- disambiguation of terms used across constitution, memory runbook, templates, compliance, and validator
- defining what high-impact governance words mean operationally

### It is not authoritative for
- introducing new policy on its own
- changing constitutional rules
- replacing detailed procedures owned elsewhere

### When it must be loaded
Load `AgentGlossary.md` when:

- interpreting ambiguous governance terms
- validating whether terms are being used correctly
- editing governance files that depend on canonical term consistency
- updating compliance checks that refer to glossary-defined concepts
- deciding whether a term belongs in the glossary or should instead be rewritten locally

### Loading class
**Conditionally required**, but practically required for governance editing, validator evolution, and ambiguity review.

---

## 3.3 `docs/agent/AgentTemplates.md`

### Authority
This file is the canonical template pack for governance-critical records and action formats.

### It is authoritative for
- approval request structures
- approval outcome structures
- approval-gate decision-option comparison matrices
- contradiction records
- correction records
- evidence records
- benchmark-impact records
- reconciliation blocks
- drift checkpoint blocks
- task and stage record structures
- governance maintenance record structures

### It is not authoritative for
- deciding whether an action is allowed
- deciding whether approval is required
- deciding which source of truth wins
- deciding what is scientifically correct

### When it must be loaded
Load `AgentTemplates.md` when:

- a canonical governance record must be created
- an approval gate is triggered
- a contradiction is logged or resolved
- evidence is being formalized
- a benchmark invalidation or comparability record is needed
- a session reconciliation block is produced
- a governance change record is required

### Loading class
**Conditionally required**, but mandatory whenever canonical governance record structure is needed.

---

## 3.4 `docs/agent/AgentCompliance.md`

### Authority
This file is the compliance specification for mechanically checkable governance protections.

### It is authoritative for
- which governance artifacts must exist
- which structural checks the validator must perform
- which hard-gate phrases and sections must remain present
- what the validator may and may not claim
- how compliance failures are classified conceptually

### It is not authoritative for
- replacing human judgment
- deciding theory quality
- deciding architecture quality
- deciding whether a contradiction was substantively resolved well

### When it must be loaded
Load `AgentCompliance.md` when:

- evaluating compliance expectations
- updating the validator
- changing governance file structure
- reviewing path migration correctness
- determining whether a proposed simplification weakens enforceability
- checking whether core hard-gate protections remain mechanically protected

### Loading class
**Conditionally required**, but mandatory for validator work and governance restructuring.

---

## 3.5 `docs/agent/AgentResearchWorkflows.md`

### Authority
This file is the binding research-workflow appendix for repository-first literature expansion, paper verification, and non-winner comparison methodology.

### It is authoritative for
- repository-first loading discipline for research work
- additive research-document creation rules
- triple-verification workflow for paper notes
- comparison-framework rules for methods, techniques, and branches
- comparison-scoring consistency where active comparison documents exist
- paper-note and comparison-note workflow boundaries

### It is not authoritative for
- constitutional source-of-truth hierarchy
- benchmark science itself
- design truth
- implementation semantics
- replacing user approval when a comparison methodology or research-scope change is high-impact
- defining the canonical structure of approval-gate decision prompts, which belongs to `docs/agent/AgentTemplates.md`

### When it must be loaded
Load `AgentResearchWorkflows.md` when:

- performing repository-first research synthesis
- creating or updating paper-note collections
- creating comparison frameworks or comparative matrices
- deciding whether to create a new research file versus editing an existing one
- evaluating research directions without selecting a final winner
- formalizing literature verification or comparison scoring methodology

### Loading class
**Conditionally required**, but mandatory whenever the task is research-synthesis-heavy, comparison-heavy, or literature-documentation-heavy.

---

## 3.6 `docs/agent/AgentAppendices.md`

### Authority
This file is the appendix authority and loading map.

### It is authoritative for
- appendix loading order
- appendix necessity classification
- boundary lines between appendices
- prevention of appendix neglect and silent role drift

### It is not authoritative for
- redefining the constitutional core
- replacing the appendix files themselves
- acting as the template pack, glossary, runbook, or compliance spec

### When it must be loaded
Load this file when:

- a future agent is determining what else must be read after `AgentRules.md`
- evaluating whether a new appendix is justified
- checking whether appendix overlap or ownership drift exists
- reviewing distributed governance safety

### Loading class
**Always required** when working on governance architecture or when a fresh agent is learning the appendix system.

---

## 4. Mandatory Reading and Loading Order

The safest default reading order for a fresh agent is:

1. `AgentRules.md`
2. `docs/agent/AgentAppendices.md`
3. `docs/agent/AgentMemory.md`
4. `docs/agent/agent_log/Current_State.md`
5. `docs/agent/agent_log/Event_Ledger.ndjson` as needed for continuity reconstruction
6. `docs/agent/AgentGlossary.md`
7. `docs/agent/AgentTemplates.md`
8. `docs/agent/AgentResearchWorkflows.md` when research, literature, or comparison work is active
9. `docs/agent/AgentCompliance.md`
10. `scripts/validate_agent_governance.py` when validator behavior matters

Reason for this order:

- the constitution must define the governing frame first
- the appendix map must explain what else must be loaded and why
- the memory runbook must be loaded early because continuity is a hard gate
- the interaction-log files are needed to reconstruct current scope and approvals
- the glossary reduces ambiguity before editing governance artifacts
- the templates support correct formal record creation
- the research-workflow appendix prevents research drift, citation hallucination, and hidden winner-picking during research-heavy work
- the compliance spec and validator matter once structural enforcement or governance changes are in play

---

## 5. Always-Required vs Conditionally-Required Appendix Matrix

## 5.1 Always-required appendices

These must be treated as effectively mandatory for safe governance work:

- `docs/agent/AgentAppendices.md`
- `docs/agent/AgentMemory.md`

Reason:
Without them, loading order and continuity control are under-specified.

## 5.2 Usually-required appendices

These are not required for every repository action, but they are required for most governance-sensitive work:

- `docs/agent/AgentGlossary.md`
- `docs/agent/AgentTemplates.md`

Reason:
They reduce ambiguity and structure high-impact actions.

## 5.3 Situationally-required appendices

These are required when the nature of the work makes them relevant:

- `docs/agent/AgentResearchWorkflows.md`
- `docs/agent/AgentCompliance.md`

Reason:
- `AgentResearchWorkflows.md` becomes mandatory when repository-first research synthesis, paper-note work, or method-comparison work is involved.
- `AgentCompliance.md` becomes mandatory when compliance, validator, pathing, or governance restructuring is involved.

---

## 6. Action-to-Appendix Loading Map

Use the table below as an operational loading rule.

### 6.1 Fresh start
Must load:

- `AgentRules.md`
- `AgentAppendices.md`
- `AgentMemory.md`

Then reconstruct operational state through:

- `Current_State.md`
- `Event_Ledger.ndjson`

Recommended next:
- `AgentGlossary.md`

### 6.2 New user request affecting tracked work
Must load:
- `AgentMemory.md`

Recommended:
- `AgentTemplates.md` if the request creates approval-gated or structured records

### 6.3 Approval gate encountered
Must load:
- `AgentMemory.md`
- `AgentTemplates.md`

Recommended:
- `AgentGlossary.md` if any governance term is ambiguous

### 6.4 Contradiction detected
Must load:
- `AgentMemory.md`
- `AgentTemplates.md`

Recommended:
- `AgentGlossary.md` for term discipline
- `AgentCompliance.md` if the contradiction concerns governance files

### 6.5 Benchmark invalidation or comparability update
Must load:
- `AgentMemory.md`
- `AgentTemplates.md`

Recommended:
- `AgentGlossary.md`

### 6.6 Governance file editing
Must load:
- `AgentAppendices.md`
- `AgentGlossary.md`

And load as needed:
- `AgentMemory.md` if continuity implications exist
- `AgentTemplates.md` if canonical records are needed
- `AgentCompliance.md` if structural protections may be affected

### 6.7 Validator editing
Must load:
- `AgentCompliance.md`
- `AgentGlossary.md`

Recommended:
- `AgentRules.md`
- `AgentAppendices.md`

### 6.8 Governance simplification proposal
Must load:
- `AgentRules.md`
- `AgentAppendices.md`
- `AgentCompliance.md`
- `AgentGlossary.md`

Recommended:
- `AgentMemory.md` if continuity handling is affected

### 6.9 Repository-first research synthesis
Must load:
- `AgentResearchWorkflows.md`

Recommended:
- `AgentGlossary.md`
- `AgentTemplates.md`

### 6.10 Paper verification and literature-note creation
Must load:
- `AgentResearchWorkflows.md`
- `AgentTemplates.md`

Recommended:
- `AgentGlossary.md`

### 6.11 Comparison framework or comparative-matrix work
Must load:
- `AgentResearchWorkflows.md`
- `AgentTemplates.md`

Recommended:
- `AgentGlossary.md`
- `AgentCompliance.md` if the comparison workflow becomes structurally enforced

---

## 7. Appendix Neglect Prevention Rules

A distributed governance system fails if future agents skip critical appendices.
To prevent that:

1. `AgentRules.md` must explicitly reference required appendices by path and purpose.
2. This file must explicitly classify appendix necessity.
3. The compliance layer should verify critical appendix references remain present.
4. The validator should fail if required appendix references disappear from the constitutional core.
5. Governance editing must not proceed by reading only the core constitution when the action also depends on continuity, definitions, templates, or compliance enforcement.

If an appendix is required for a protected action and it is not loaded, the action should be treated as unsafe.

---

## 8. Appendix Boundary Rules

To prevent distributed governance from collapsing into overlap, the appendices must respect these boundaries.

## 8.1 `AgentMemory.md` boundary

May define:
- continuity procedure
- logging rules
- event schema
- state reconciliation

Must not define:
- benchmark science
- source-of-truth hierarchy beyond interaction-log authority relationships
- design architecture truth

## 8.2 `AgentGlossary.md` boundary

May define:
- canonical meanings of high-impact governance terms

Must not define:
- new constitutional policy
- long procedural runbooks
- template structures

## 8.3 `AgentTemplates.md` boundary

May define:
- canonical structures for records

Must not define:
- whether actions are allowed
- approval policy itself
- contradiction authority itself

## 8.4 `AgentCompliance.md` boundary

May define:
- what is mechanically inspectable
- what checks are required
- validator scope limits

Must not define:
- substantive scientific truth
- human judgment replacement
- alternative constitutional rules

## 8.5 `AgentAppendices.md` boundary

May define:
- loading map
- appendix necessity
- appendix ownership boundaries

Must not redefine:
- constitutional rules
- memory procedures
- glossary meanings
- template bodies
- compliance logic details

## 8.6 `AgentResearchWorkflows.md` boundary

May define:
- repository-first research loading order below the constitutional layer
- literature verification procedures
- additive research-document creation rules
- non-winner comparison methodology rules

Must not define:
- constitutional approval policy
- source-of-truth hierarchy itself
- benchmark science as a substitute for theory truth
- code or architecture truth

---

## 9. Rules for Adding a New Appendix

A new appendix may be added only if all of the following are true:

1. it owns a distinct governance responsibility not already well-owned
2. keeping that content in the core would materially reduce readability or maintainability
3. moving that content out will not weaken constitutional hard gates
4. the new appendix can be named clearly and non-ambiguously
5. `AgentRules.md` and this appendix map are updated explicitly
6. the compliance layer is reviewed for whether the new appendix must be validated

`docs/agent/AgentResearchWorkflows.md` satisfies this rule set and is now part of the appendix layer.

A new appendix must not be added merely because the file set “looks cleaner.”
The appendix must improve governance clarity without weakening enforceability.

---

## 10. Rules for Removing, Merging, or Renaming an Appendix

An appendix may be removed, merged, or renamed only if:

- its responsibility becomes redundant
- its authority can be preserved elsewhere without ambiguity
- `AgentRules.md` is updated
- this file is updated
- `AgentCompliance.md` is updated if needed
- the validator is updated if needed
- path migration is explicit
- no protected action is left without a canonical support layer

Silent appendix removal is forbidden.

---

## 11. Compatibility and Path Migration Rules

If historical materials refer to:

- `docs/agent_log/AgentMemory.md`
- `docs/agent_log/Current_State.md`
- `docs/agent_log/Event_Ledger.ndjson`

but the active system uses:

- `docs/agent/AgentMemory.md`
- `docs/agent/agent_log/Current_State.md`
- `docs/agent/agent_log/Event_Ledger.ndjson`

then the migration must be treated as a governance-level path update.

Rules:

1. the active authoritative paths must be declared explicitly
2. the validator should detect unintended legacy references
3. mixed old/new references should be treated as risky unless a documented compatibility mechanism exists
4. future governance editing should use only the active authoritative paths

---

## 12. Appendix Use and Auditability

For high-impact governance-sensitive actions, appendix usage should be inferable from the artifacts produced.

Examples:

- if an approval gate was triggered, the resulting structure should visibly follow `AgentTemplates.md`
- if continuity was reconstructed, the resulting state should visibly align with `AgentMemory.md`
- if a validator expectation changed, the change should visibly align with `AgentCompliance.md`
- if an ambiguous term was clarified, the resulting wording should align with `AgentGlossary.md`

This does not require a formal usage log for every appendix in every case.
It does require that future agents can understand why the action structure looks the way it does.

---

## 13. Maintenance Rules for the Appendix Layer

The appendix layer should be reviewed when:

- the constitutional core changes
- path conventions change
- the validator evolves materially
- ambiguity repeatedly appears around a missing or weak definition
- recurring governance actions lack stable structure
- appendix overlap begins to appear
- a future agent cannot determine reading order safely

During maintenance, check:

- is each appendix still distinct?
- is any appendix silently growing into a second constitution?
- is any appendix too weak to support the role assigned to it?
- is any appendix missing from the constitutional references?
- does the validator still match the appendix system?

---

## 14. Appendix Loading Failure Conditions

The distributed system should be treated as unsafe if any of the following occurs:

- a required appendix is not referenced where needed
- a future agent cannot determine reading order
- an appendix silently takes over a role owned by the constitution
- the template pack is required but unavailable
- glossary definitions are needed but absent
- continuity rules are required but `AgentMemory.md` is not loaded
- compliance enforcement is expected but `AgentCompliance.md` and the validator drift apart

These are governance failures, not cosmetic issues.

---

## 15. Final Rule

A distributed governance system is only better than a monolithic one if it preserves constitutional strength while improving clarity.

If appendix distribution causes ambiguity, skipped requirements, weakened hard gates, or uncertain reading order, the distribution has failed and must be repaired.
