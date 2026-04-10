# AgentTemplates.md

## 0. Purpose

This file is the canonical template pack for governance-critical actions.

Its purpose is to make execution more consistent, more auditable, and less ambiguous by providing direct reusable structures for:

- task registration
- approval requests
- approval outcomes
- contradiction handling
- evidence recording
- benchmark logging
- benchmark invalidation and comparability updates
- research comparison records
- paper verification records
- literature note records
- stage completion certification
- session reconciliation
- drift checkpoints
- fresh-start reconstruction notes
- governance-change recording
- correction logging

This file does not override `AgentRules.md`.
This file does not replace `docs/agent/AgentMemory.md`.
It provides the default canonical structures to be used whenever those governing files require explicit records.

If a future agent needs a format for a governance-critical action and no better canonical format exists elsewhere, this file is the default authority.

---

## 1. Template Usage Rules

1. Use the templates in this file for governance-relevant actions unless a higher-authority file explicitly requires a different structure.
2. Templates may be extended with extra fields when needed, but required fields should not be removed silently.
3. If a template is used for a high-impact action, the resulting record must remain concise, factual, and auditable.
4. Templates are not free-form writing prompts. They are operational control structures.
5. If a template is insufficient for a recurring governance need, update this file explicitly rather than improvising inconsistent variants across the repo.

---

## 2. Task and Planning Templates

### 2.1 Task Register Entry (for `Current_State.md`)

```text
- Task ID:
- Title:
- Status:
- Priority:
- Owner:
- Created:
- Last touched:
- Request IDs:
- Dependencies:
- Blockers:
- Approvals needed:
- Benchmark status:
- Stale-risk status:
- Evidence pointers:
- Notes:
```

### 2.2 Task Status Change Record

```text
Task ID:
Previous status:
New status:
Change date:
Reason for change:
Related request IDs:
Related event IDs:
Evidence added:
Approvals affected:
Blockers affected:
Downstream files to review:
```

### 2.3 Task Split Record

```text
Original Task ID:
Original title:
Split date:
Reason for split:
New Task IDs:
Why the split improves clarity:
Dependencies redistributed:
Blockers redistributed:
Approvals redistributed:
Evidence pointers carried forward:
Notes:
```

### 2.4 Task Merge Record

```text
Merged Task IDs:
New surviving Task ID:
Merge date:
Reason for merge:
Scope relationship:
Dependencies after merge:
Blockers after merge:
Approvals after merge:
Evidence pointers retained:
Notes:
```

---

## 3. Approval and Decision Templates

### 3.1 Approval Request Template

```text
### USER INPUT REQUIRED
Issue:
[Direct description of the decision, ambiguity, contradiction, or branch point]

Layer:
[Theory | Design | Code | Validation | Operations | Governance]

Why this blocks safe progress:
[Direct explanation]

Relevant sources:
- [file]
- [file]

Best current interpretation:
[Label clearly as interpretation, not fact]

Possible options:
1. ...
2. ...
3. ...

Recommended option:
[State recommendation and why]

Downstream files affected if approved:
- ...
- ...
- ...

Risks if delayed:
- ...
- ...

Please confirm:
[Exact approval needed]
```

### 3.2 Approval Outcome Record

```text
Approval event ID:
Date:
Related request ID:
Related task IDs:
Approval gate:
Decision made:
Approved | Rejected | Partially approved:
Approved scope:
Rejected scope:
Conditions imposed by user:
Immediate next action:
Downstream files affected:
Notes:
```

### 3.3 Decision Record / ADR Entry

```text
Decision ID:
Date:
Title:
Theory basis:
Affected files or modules:
Options considered:
Chosen option:
Why chosen:
Rejected options and why:
Tradeoffs:
Benchmark implications:
User approval required: yes/no
User approval received: yes/no
Downstream files affected:
Follow-up actions:
Notes:
```

### 3.4 Scope Change Proposal Record

```text
Proposal ID:
Date:
Related request ID:
Related task IDs:
Current approved contract summary:
Proposed change:
Why the change is being proposed:
What triggered the proposal:
Benefits:
Risks:
Files that would need updates:
Approval required: yes
User response:
Notes:
```

---

## 4. Contradiction and Correction Templates

### 4.1 Contradiction Detection Record

```text
Conflict ID:
Date:
Severity:
Layer:
Sources in conflict:
Conflicting statements:
Why the conflict matters:
Which source currently appears authoritative:
Mechanically obvious: yes/no
User input required: yes/no
Immediate blocked actions:
Downstream files to review:
Ledger event IDs:
Notes:
```

### 4.2 Contradiction Resolution Record

```text
Conflict ID:
Resolution date:
Resolution method:
Authority used:
Resolved by:
User approval required: yes/no
User approval received: yes/no
Old state:
New state:
Files corrected:
Downstream propagation completed: yes/no
Remaining stale-risk:
Related event IDs:
Notes:
```

### 4.3 Correction Event Record

```text
Correction ID:
Date:
Original event ID:
What was wrong:
Why it was wrong:
Corrected interpretation:
Affected tasks:
Affected approvals:
Affected evidence:
Affected files:
State repair required:
Notes:
```

---

## 5. Evidence and Completion Templates

### 5.1 Evidence Record

```text
Evidence ID:
Date:
Evidence type:
Related request IDs:
Related task IDs:
Supports claim:
Artifact path or reference:
How to inspect:
Trust level:
Why this evidence is sufficient:
Limitations:
Notes:
```

### 5.2 Completion Basis Check

```text
Task or stage ID:
Date:
Scope satisfied: yes/no
Dependencies satisfied: yes/no
Required approvals satisfied: yes/no
Blockers resolved: yes/no
Benchmark comparability acceptable: yes/no/not-applicable
Evidence pointers:
Stale-risk remaining: yes/no
Completion decision:
Notes:
```

### 5.3 Stage Completion Certification

```text
Stage ID:
Stage name:
Completion date:
Objective satisfied:
Files completed or updated:
Required tests completed:
Required doc updates completed:
Guidebook updated: yes/no
Execution plan updated: yes/no
Contradictions resolved: yes/no
Remaining blockers:
Evidence pointers:
Final completion decision:
Notes:
```

### 5.4 Milestone Completion Record

```text
Milestone ID:
Date:
Milestone definition:
Tasks included:
Completion basis satisfied: yes/no
Evidence pointers:
Benchmark implications:
Outstanding risks:
User-visible impact:
Notes:
```

---

## 6. Test and Benchmark Templates

### 6.1 Test Log Entry

```text
YYYY-MM-DD
Test type:
Target:
Purpose:
Why this test exists:
Environment:
Input conditions:
Expected result:
Actual result:
Pass | Fail | Blocked:
Evidence pointer:
Stale after:
Follow-up required:
Notes:
```

### 6.2 Benchmark Run Record

```text
Benchmark ID:
Date:
Purpose:
Target artifact or model:
Dataset or split:
Metric definitions:
Environment:
Command or procedure:
Result summary:
Result location:
Comparable to prior results: yes/no/partial
Evidence pointers:
Notes:
```

### 6.3 Benchmark Invalidation / Comparability Record

```text
Benchmark impact ID:
Date:
Trigger:
Changed artifact:
Why comparability is affected:
Affected prior results:
Old result status: fully comparable | partially comparable | not comparable | invalidated
Required reruns:
Immediate planning impact:
Affected tasks:
Affected docs:
Notes:
```

### 6.4 Benchmark Success Claim Record

```text
Claim ID:
Date:
Benchmark ID:
Claim being made:
Comparability status:
Evidence pointers:
Why the claim is valid:
Known limitations:
Downstream docs that must reflect the claim:
Notes:
```

### 6.5 Method / Technique Comparison Profile

```text
Comparison profile ID:
Date:
Family category:
Method or technique name:
Comparison scope:
Evidence basis:
Scoring version:
Measured attributes:
- ...
Grouped scores:
- Scientific Value Score:
- Benchmark Integrity Score:
- Engineering Fit Score:
- Compatibility Score:
Confidence:
Similarity notes:
Distinctive traits:
Comments:
Non-decision conclusion:
```

### 6.6 Comparative Matrix Row Template

```text
Category:
Method/family:
Attribute scores:
- A1:
- A2:
- A3:
...
Grouped scores:
- SVS:
- BIS:
- EFS:
- COS:
Confidence:
Comments:
```

### 6.7 Paper Verification Record

```text
Paper ID:
Verification date:
Exact title:
Authors:
Year:
Venue:
DOI:
Source 1:
Source 2:
Source 3:
Primary or official source included: yes/no
Metadata fully match across sources: yes/no
Discrepancies:
Trust level:
Include in main research: yes/no
If no, why:
Notes:
```

### 6.8 Literature Note Record

```text
Paper ID:
Research family:
Why relevant to this project:
Main problem addressed:
Inputs/modalities:
Target design:
Model family:
Evaluation design:
Metrics:
Leakage or benchmark risks:
Pros:
Cons:
Repository-fit implications:
Modularity implications:
What this supports:
What this does not support:
Reproducibility notes:
Key literal quotes:
Final usefulness rating:
```

---

## 7. Session and Drift Templates

### 7.1 Reconciliation Block

```text
Session ID:
Date:
Asked:
Understood:
Executed:
Not executed and why:
New blockers:
Approvals required:
Evidence added:
Stale-risk discovered:
Corrections appended:
Next safe action:
Notes:
```

### 7.2 Drift Checkpoint Block

```text
Drift checkpoint ID:
Date:
Session ID:
Current Immutable Task Contract summary:
Next intended action:
Does the next action still serve the approved contract? yes/no
Reason:
If no or unclear, what must happen next:
Related task IDs:
Notes:
```

### 7.3 Session Closing Sanity Check

```text
Session ID:
Reconciliation completed: yes/no
Drift checkpoint appended: yes/no
Current_State updated: yes/no
Ledger updated for meaningful changes: yes/no
Any unresolved blocker hidden only in chat: yes/no
Any invalid DONE claim remaining: yes/no
Ready to close session: yes/no
Notes:
```

---

## 8. Fresh-Start and Reconstruction Templates

### 8.1 Fresh-Start Reconstruction Note

```text
Reconstruction ID:
Date:
Session ID:
AgentRules read: yes/no
AgentMemory read: yes/no
Current_State exists: yes/no
Event_Ledger exists: yes/no
Immutable Task Contract recovered: yes/no
Active tasks recovered: yes/no
Approvals recovered: yes/no
Evidence recovered: yes/no
Need user clarification before work continues: yes/no
Why:
Notes:
```

### 8.2 Missing File Recovery Record

```text
Recovery ID:
Date:
Missing file:
Why it matters:
Minimum valid skeleton created: yes/no
Blocked until approval: yes/no
Downstream files impacted:
Related task IDs:
Notes:
```

---

## 9. Governance Maintenance Templates

### 9.1 Governance Change Record

```text
Governance change ID:
Date:
Changed file:
Reason for change:
Governance category:
- source-of-truth hierarchy
- approval gates
- interaction-log policy
- evidence policy
- benchmark governance
- compliance logic
- appendix loading
- self-update rules
Old rule summary:
New rule summary:
User approval required: yes/no
User approval received: yes/no
Files requiring consistency review:
Notes:
```

### 9.2 Appendix Loading Record

```text
Loading record ID:
Date:
Core file being followed:
Appendix loaded:
Why it was required:
Binding for this action: yes/no
If binding, what requirement it supplied:
Notes:
```

### 9.3 Stale-Risk Record

```text
Stale-risk ID:
Date:
Affected file or artifact:
Upstream trigger:
Why stale-risk exists:
Tasks affected:
Completion claims affected:
Review required by:
Severity:
Notes:
```

---

## 10. Compact Operational Templates

These shorter forms are allowed when speed matters, but only if they do not reduce clarity.

### 10.1 Compact Task Note

```text
[TASK] T-... | status -> ... | reason: ... | blockers: ... | evidence: ...
```

### 10.2 Compact Benchmark Note

```text
[BENCH] Trigger: ... | old status: ... | new status: ... | reruns: ...
```

### 10.3 Compact Approval Note

```text
[APPROVAL] Needed for: ... | layer: ... | blocked until: ...
```

Use compact forms only for low-noise operational recording, not for high-impact ambiguous decisions.

---

## 11. Final Rule

If a governance-relevant action has no clear record structure and the absence of structure could create ambiguity, inconsistency, or audit weakness:

1. use the closest template in this file
2. extend it carefully if needed
3. update this file later if the pattern is likely to recur
