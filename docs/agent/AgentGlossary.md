# AgentGlossary.md

## 0. Purpose

This file is the canonical ambiguity-reduction layer for the repository governance system.

Its purpose is to define the highest-value governance terms in a strict, operationally useful way so that:

- `AgentRules.md` stays precise without repeating full definitions everywhere
- `AgentMemory.md` can apply event, evidence, and continuity rules consistently
- `AgentTemplates.md` can use stable terminology
- `AgentCompliance.md` and `scripts/validate_agent_governance.py` can check the correct concepts
- future agents do not reinterpret critical governance words loosely

This file is not a second constitution.
It does not override `AgentRules.md`.
It exists to reduce ambiguity, not to create alternative policy.

Where `AgentRules.md` or `AgentMemory.md` invokes a glossary term intentionally, the definition in this file is the canonical meaning unless the constitution explicitly narrows it further.

---

## 1. How to Use This Glossary

Each entry contains four fields:

- **Strict definition**  
  The authoritative meaning of the term inside this governance system.

- **Why it matters operationally**  
  Why the term affects decisions, logging, validation, or implementation behavior.

- **What it is not**  
  Common misreadings that must be excluded.

- **Typical consequences**  
  What actions usually follow when the term applies.

This glossary should remain intentionally small.
Only terms that materially reduce ambiguity belong here.

---

## 2. Canonical Terms

### 2.1 Meaningful change

**Strict definition**  
A change is meaningful if it alters scope, task state, approval state, execution status, evidence status, benchmark comparability, stale-risk, or the alignment of the next action with the approved contract.

**Why it matters operationally**  
Meaningful changes trigger mandatory updates to `Current_State.md` and `Event_Ledger.ndjson`, and often require downstream document review.

**What it is not**  
A typo fix, formatting cleanup, cosmetic wording tweak, or trial command with no state consequence is not meaningful by itself.

**Typical consequences**  
- append ledger event
- update `Current_State.md`
- review dependent tasks or files if the change propagates

---

### 2.2 Evidence pointer

**Strict definition**  
An evidence pointer is a concrete, inspectable reference that supports a claim that work was executed, validated, accepted, or completed.

**Why it matters operationally**  
No task, stage, milestone, or benchmark success claim may be marked DONE without at least one valid evidence pointer.

**What it is not**  
A confident statement, a remembered result, a vague “it should work,” or an unstored terminal impression is not evidence.

**Typical consequences**  
- enables DONE status when other conditions are also satisfied
- should be recorded in `Current_State.md`
- should appear in relevant ledger events

**Examples**  
- commit hash
- test run ID
- benchmark run ID
- reproducible command output
- saved artifact path
- explicit user acceptance note

---

### 2.3 Proof of completion

**Strict definition**  
Proof of completion is the full completion basis for a task or stage: evidence pointer plus satisfied dependencies plus no unresolved blocker invalidating the claim.

**Why it matters operationally**  
Completion is stronger than “some evidence exists.” A task is not truly complete if evidence exists but a required approval, blocker resolution, or comparability check remains missing.

**What it is not**  
A single passing test does not automatically prove full task completion if the task required more than that test.

**Typical consequences**  
- used before upgrading a task to `done`
- should survive audit or fresh-start review
- may require more than one evidence pointer

---

### 2.4 Stage completion

**Strict definition**  
Stage completion means the stage’s planned outputs, required document updates, required tests, required evidence, and required contradiction resolution conditions have all been satisfied according to the execution plan.

**Why it matters operationally**  
Stages structure implementation order. False stage completion corrupts planning, misleads future agents, and may hide stale-risk or missing validation.

**What it is not**  
“Most of the code is written” is not stage completion. “The main function works” is not stage completion if docs, tests, or blockers remain unresolved.

**Typical consequences**  
- stage may advance
- related task statuses may change
- guidebook, execution plan, and evidence records should already be aligned

---

### 2.5 Stale-risk

**Strict definition**  
Stale-risk is the condition where a file, summary, status, benchmark conclusion, or completion claim may no longer be reliable because an upstream dependency changed and the dependent artifact has not yet been reviewed.

**Why it matters operationally**  
Stale-risk prevents false certainty. It protects against partial truth updates and invalid reuse of docs, benchmarks, or operational summaries.

**What it is not**  
It is not a confirmed error. It is a reliability warning requiring review.

**Typical consequences**  
- log stale-risk if it affects planning or completion
- do not rely on the stale artifact as if current
- review downstream dependents before major implementation continues

---

### 2.6 Benchmark comparability change

**Strict definition**  
A benchmark comparability change is any change that may alter whether new and old benchmark results can still be fairly compared under the same interpretation.

**Why it matters operationally**  
Benchmark comparisons are only meaningful if the measured setup remains sufficiently equivalent. Comparability changes can invalidate performance claims and scientific conclusions.

**What it is not**  
Any code change is not automatically a comparability change. The change must plausibly affect the fairness, meaning, or interpretation of comparison.

**Typical consequences**  
- review benchmark status
- classify prior results
- possibly mark results partially comparable, not comparable, or invalidated
- reruns may become required

---

### 2.7 Benchmark invalidation trigger

**Strict definition**  
A benchmark invalidation trigger is a concrete upstream change that requires explicit review of whether prior benchmark results remain usable.

**Why it matters operationally**  
This term operationalizes benchmark rigor and prevents silent reuse of invalid comparisons.

**What it is not**  
It is not the invalidation outcome itself. It is the event or condition that forces the review.

**Typical consequences**  
- append benchmark-related event if operationally relevant
- update benchmark governance docs
- reclassify old results if necessary

**Common examples**  
- target definition changed
- split methodology changed
- metric definition changed
- feature construction changed
- label logic changed
- model output contract changed

---

### 2.8 Immutable Task Contract

**Strict definition**  
The Immutable Task Contract is the user-approved statement of objective, hard constraints, out-of-scope boundaries, approval gates, and canonical truth references stored in `Current_State.md`.

**Why it matters operationally**  
It is the anchor for drift control. The system uses it to decide whether the next action is still aligned with user-approved scope.

**What it is not**  
It is not a casual notes section, not a brainstorming area, and not a place to silently absorb inferred improvements.

**Typical consequences**  
- cannot be changed without explicit user approval
- drift checkpoints evaluate against it
- scope changes must be proposed before adoption

---

### 2.9 Approval gate

**Strict definition**  
An approval gate is a point where the system must stop and obtain explicit user consent before continuing because the next step would otherwise rely on ambiguity, scope expansion, design branching, or other high-impact judgment.

**Why it matters operationally**  
Approval gates prevent silent assumptions, silent scope expansion, and unapproved governance or benchmark changes.

**What it is not**  
A preference guess is not an approval gate unless it materially changes scope or architecture. An approval gate is not satisfied by vague user positivity unless the decision is explicit.

**Typical consequences**  
- append approval request event
- update open questions
- block forward action until approval or rejection is received

---

### 2.10 Drift checkpoint

**Strict definition**  
A drift checkpoint is an explicit audit question asking whether the next action still serves the current Immutable Task Contract.

**Why it matters operationally**  
It prevents the agent from slowly drifting from approved goals during long sessions, branching work, or maintenance-heavy tasks.

**What it is not**  
It is not a generic progress summary. It is a contract-alignment check.

**Typical consequences**  
- append `Drift_Checkpoint` event
- stop and ask if the answer is not clearly yes
- surface hidden scope drift early

---

### 2.11 Session

**Strict definition**  
A session is one coherent working interval of user-agent interaction for which reconciliation and drift review must be performed before the session is treated as closed.

**Why it matters operationally**  
Session boundaries determine when reconciliation, drift checkpoints, and state refreshes are mandatory.

**What it is not**  
It is not necessarily equal to one user message or one tool call. A session may span multiple linked requests and actions.

**Typical consequences**  
- assign or reuse session ID
- reconcile at session end
- ensure meaningful changes were logged before closure

---

### 2.12 Governance change

**Strict definition**  
A governance change is a modification to the rules, hierarchy, approval structure, continuity procedures, compliance expectations, or enforcement logic that controls how the repository is governed.

**Why it matters operationally**  
Governance changes affect the safety of future work and must not be treated like normal content edits.

**What it is not**  
Updating a normal implementation file is not a governance change unless it changes the governing system itself.

**Typical consequences**  
- log governance event
- review consistency with `AgentRules.md`
- often requires explicit user approval

---

### 2.13 Hard gate

**Strict definition**  
A hard gate is a condition that must be satisfied before a protected action may continue.

**Why it matters operationally**  
Hard gates turn abstract governance into enforceable behavior.

**What it is not**  
A recommendation, best practice, or suggestion is not a hard gate.

**Typical consequences**  
Protected actions stop until the gate is satisfied.

**Examples**  
- no DONE claim without evidence
- no scope change without approval
- no implementation when approved scope is unclear
- no action after negative drift checkpoint without clarification

---

### 2.14 Authority resolution

**Strict definition**  
Authority resolution is the act of determining which source wins when two sources disagree, using the declared source-of-truth hierarchy.

**Why it matters operationally**  
Without authority resolution, contradictions are handled arbitrarily and governance collapses into inconsistency.

**What it is not**  
It is not averaging two conflicting sources. It is not choosing the newest source by default.

**Typical consequences**  
- identify conflicting sources
- determine higher authority
- correct lower layer or ask the user if resolution is not mechanically obvious

---

### 2.15 Mechanically obvious contradiction

**Strict definition**  
A contradiction is mechanically obvious when the correct resolution is straightforward because a lower-authority artifact clearly drifted from a higher-authority source without any legitimate competing approval.

**Why it matters operationally**  
Mechanically obvious contradictions can be corrected without forcing unnecessary user approval, while still preserving auditability.

**What it is not**  
A difficult design tradeoff or ambiguous theory interpretation is not mechanically obvious.

**Typical consequences**  
- correct lower layer
- log contradiction and correction
- propagate downstream if needed

---

### 2.16 Contradiction

**Strict definition**  
A contradiction is a meaningful conflict between two sources, states, or claims that cannot both be treated as true for current execution purposes.

**Why it matters operationally**  
Contradictions must be surfaced explicitly because silent contradiction handling creates false trust in the repository state.

**What it is not**  
A wording preference difference without operational consequence is not necessarily a contradiction.

**Typical consequences**  
- classify severity
- resolve authority
- log detection
- correct or escalate

---

### 2.17 Downstream propagation

**Strict definition**  
Downstream propagation is the mandatory review and update of all dependent artifacts that may have become stale or wrong because an upstream source changed.

**Why it matters operationally**  
It is the main safeguard against partial truth updates.

**What it is not**  
It is not “update everything blindly.” It is a dependency-aware review and update obligation.

**Typical consequences**  
- inspect dependent docs, tests, guidebooks, plans, or operational summaries
- repair stale-risk where needed
- do not claim completion while required downstream updates remain missing

---

### 2.18 Source-of-truth hierarchy

**Strict definition**  
The source-of-truth hierarchy is the ordered authority system that determines which layer governs when conflicts occur: theory, design, code, validation, operations, with the interaction-log subsystem governing request, approval, execution, and evidence continuity rather than scientific truth.

**Why it matters operationally**  
It defines how disputes are resolved and prevents lower layers from silently redefining higher-layer intent.

**What it is not**  
It is not simply file recency or file size. It is a declared governance order.

**Typical consequences**  
- resolve contradictions by layer
- prevent README or code from overriding theory or design
- preserve traceability across the repository

---

### 2.19 No partial truth update

**Strict definition**  
A partial truth update occurs when one affected layer is updated but dependent layers that now rely on stale assumptions are left unreviewed or uncorrected.

**Why it matters operationally**  
Partial truth updates create hidden inconsistency and false completion claims.

**What it is not**  
A staged implementation is not automatically a partial truth update if the incomplete state is explicit, logged, and not misrepresented as aligned.

**Typical consequences**  
- review downstream propagation
- mark stale-risk if full propagation is not yet complete
- do not close the affected task prematurely

---

### 2.20 Fresh-start reconstruction

**Strict definition**  
Fresh-start reconstruction is the mandatory process of rebuilding trustworthy context from governance files before implementation continues after context loss, session reset, handoff, or environment restart.

**Why it matters operationally**  
It prevents new work from being based on memory leakage, stale summaries, or hidden assumptions.

**What it is not**  
It is not skimming the README and proceeding.

**Typical consequences**  
- read `AgentRules.md`
- read `AgentMemory.md`
- restore interaction-log state
- then reconstruct theory, design, implementation, validation, and operations context

---

### 2.21 Interaction-log stewardship

**Strict definition**  
Interaction-log stewardship is the duty to preserve an explicit, auditable record of what the user asked, what was approved, what was executed, what evidence exists, and what remains pending or drifting.

**Why it matters operationally**  
It is the continuity backbone for long-lived work and fresh starts.

**What it is not**  
It is not casual note-taking and not transcript dumping.

**Typical consequences**  
- maintain `Current_State.md`
- append `Event_Ledger.ndjson`
- reconcile sessions
- preserve approvals and evidence explicitly

---

### 2.22 Meaningfully separable request

**Strict definition**  
A meaningfully separable request is a user request component that can be tracked, approved, blocked, completed, or rejected independently of another request component without creating ambiguity.

**Why it matters operationally**  
It determines whether one user message should yield one Request ID or multiple Request IDs.

**What it is not**  
Two adjacent sentences about the same tightly coupled task are not necessarily separable.

**Typical consequences**  
- use separate Request IDs only when separation improves traceability
- avoid collapsing unrelated work into one request record

---

### 2.23 Completion basis

**Strict definition**  
Completion basis is the set of conditions that justify a completion claim: correct scope, satisfied dependencies, no unresolved blocker invalidating the claim, and adequate evidence.

**Why it matters operationally**  
It provides a disciplined way to distinguish “implemented,” “tested,” and “done.”

**What it is not**  
A strong intuition that the task is finished is not a completion basis.

**Typical consequences**  
- verify evidence
- verify approvals
- verify comparability if benchmarks matter
- verify no stale-risk invalidates the completion statement

---

### 2.24 Untrusted content

**Strict definition**  
Untrusted content is any content that has not yet been validated sufficiently for the purpose it is being used for, especially tool output, external text, copied notes, or unverified file interpretations.

**Why it matters operationally**  
It prevents accidental promotion of weak evidence into scope, contract, or design truth.

**What it is not**  
Untrusted does not always mean false. It means not yet safe to elevate automatically.

**Typical consequences**  
- label trust appropriately in ledger
- do not promote into Immutable Task Contract without approval
- verify before relying on it for high-impact claims

---

### 2.25 Reconciliation block

**Strict definition**  
A reconciliation block is the structured end-of-session comparison between what was asked, what was understood, what was executed, what remains unexecuted, what blockers emerged, and what approvals are still required.

**Why it matters operationally**  
It is the main safeguard against silent session drift and missing-state carryover.

**What it is not**  
It is not a celebratory summary or a generic status update.

**Typical consequences**  
- session-end requirement
- helps repair missing state before closure
- improves fresh-start reconstruction reliability

---

### 2.26 Comparison profile

**Strict definition**  
A comparison profile is a structured, non-winner description of a method, family, or branch across explicit measured attributes and grouped scores.

**Why it matters operationally**  
It allows broad research comparison without collapsing the result into premature winner-picking.

**What it is not**  
It is not a final recommendation ranking and not a hidden one-number score.

**Typical consequences**  
- compare within category first
- preserve comments and confidence levels
- avoid declaring a winner from profile data alone

---

### 2.27 Repo-stage fit

**Strict definition**  
Repo-stage fit is the degree to which a method or branch matches the repository’s current implementation maturity, artifact structure, benchmark machinery, and available operational support.

**Why it matters operationally**  
A direction can be strong in theory but still be a poor immediate fit for the current repository stage.

**What it is not**  
It is not the same as scientific value.

**Typical consequences**  
- keep repo-stage fit separate from intrinsic scientific attractiveness
- use lower scores to flag high-friction or architecture-breaking directions

---

### 2.28 Accumulative compatibility

**Strict definition**  
Accumulative compatibility is the ease with which a method or branch can be added on top of existing branches, artifacts, and benchmark families without forcing redesign or invalidating prior work.

**Why it matters operationally**  
It measures how safely the repository can accumulate knowledge and functionality over time.

**What it is not**  
It is not mere code-level installability.

**Typical consequences**  
- high compatibility supports extension status
- low compatibility signals large blast radius or hidden benchmark disruption

---

### 2.29 Similarity band

**Strict definition**  
A similarity band is the threshold rule used to interpret whether two scored methods are effectively similar, moderately different, or materially different.

**Why it matters operationally**  
It prevents fake distinctions when comparison scores are genuinely close.

**What it is not**  
It is not a replacement for qualitative comments.

**Typical consequences**  
- differences of 0.3 or less should be treated as effectively similar unless strong comments justify otherwise

---

### 2.30 Triple verification

**Strict definition**  
Triple verification is the requirement that a paper, citation, or literature note be checked against at least three independent sources, including at least one primary or official source, before being treated as verified.

**Why it matters operationally**  
It reduces citation hallucination, venue mistakes, DOI mistakes, and metadata drift in literature-heavy work.

**What it is not**  
It is not simple duplication of the same metadata mirror three times.

**Typical consequences**  
- record three source links
- record discrepancies explicitly
- preserve `Uncertain, verify manually.` when full agreement is not reached

---

## 3. Term Inclusion Policy

A term belongs in this glossary only if at least one of the following is true:

- it appears in the constitution or memory runbook and could be misread
- it affects approval, scope, contradiction, benchmark, evidence, or continuity behavior
- it is needed for validator checks or compliance interpretation
- it prevents future simplification from weakening governance accidentally

A term should be excluded if:

- it is obvious from normal English usage in context
- it does not materially change operational behavior
- it duplicates a longer policy better owned by `AgentRules.md` or `AgentMemory.md`

---

## 4. Glossary Maintenance Rule

This glossary must remain intentionally small and high-value.

It may be updated only when:

- a critical governance term is missing
- an existing term is ambiguous enough to create execution risk
- compliance or validator logic needs a canonical definition
- the constitution introduces a new high-impact governance concept

This file must not become an oversized theory or policy document.

If a term is not high-impact, define it where it is used instead of expanding this glossary.

---

## 5. Final Rule

If a future agent can plausibly read a critical governance term in two different ways, and the ambiguity could change behavior, that term should either:

- be defined here, or
- be rewritten in the governing file so no glossary entry is needed
