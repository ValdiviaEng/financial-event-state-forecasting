# AgentResearchWorkflows.md

## 0. Purpose

This file is the binding research-workflow appendix for repository-first literature expansion, paper verification, and non-winner comparison methodology.

Its purpose is to make research-heavy work more explicit, more auditable, and less hallucination-prone by defining:

- when repository-first reading is mandatory
- how research documentation should accumulate rather than overwrite by default
- how literal paper verification must be done
- how methods and techniques should be compared without premature winner-picking
- how comparison scores should be interpreted
- what research outputs belong in `docs/research_results/`
- how paper notes and comparison notes should be structured conceptually

This file does not override `AgentRules.md`.
It does not replace theory truth, design truth, or implementation truth.
It governs how research synthesis and comparison work should be performed when those tasks are active.

## 1. Scope and Authority

This appendix is authoritative for:

- repository-first research reconstruction procedure below the constitutional core
- additive research-document creation rules
- triple-verification literature rules
- method-comparison workflow and scoring discipline
- paper-note workflow expectations
- non-winner comparison discipline

This appendix is not authoritative for:

- changing the source-of-truth hierarchy
- deciding final architecture winners
- overriding explicit user approval gates
- replacing benchmark science with comparison scores

## 2. When This Appendix Is Binding

Load and use this appendix whenever the task includes one or more of the following:

- repository-first deep research
- literature expansion
- paper-note creation
- comparison framework creation
- comparative matrices across methods, techniques, or branches
- broad state-of-the-art mapping without final winner selection
- deciding whether to create a new research file versus editing an existing one

## 3. Repository-First Research Workflow

When doing research-heavy work:

1. Read the repository first.
2. Reconstruct the current repo stage before expanding the literature map.
3. Do not assume every documented branch is equally mature.
4. Distinguish implemented, plausible, and aspirational branches explicitly.
5. Treat benchmark comparability as part of the science, not an afterthought.

If a repository capability is not evidenced, say exactly:

Not evidenced in repository materials.

If something seems likely but is not proven, say exactly:

Plausible but unverified.

If a citation detail, provider behavior, benchmark convention, or architectural assumption is uncertain, say exactly:

Uncertain, verify manually.

## 4. Additive Research Documentation Rule

Default rule:

- preserve previous research documentation
- add new research files instead of overwriting old ones
- create sibling documents, addenda, indexes, or logs where appropriate

Do not overwrite an existing research document unless the user explicitly requests a replacement or revision.

This matters because research history should accumulate, including contradictory or superseded investigations, as long as the distinction is explicit.

## 5. Triple-Verification Literature Rule

Any paper included as a verified paper note must be checked against:

- three independent sources
- at least one primary or official source

Examples of acceptable primary or official sources:

- publisher page
- proceedings page
- ACL Anthology page
- official DOI page
- official arXiv page

Examples of acceptable secondary sources:

- Crossref
- DBLP
- OpenAlex
- RePEc / IDEAS
- Semantic Scholar

The paper note must record:

- Source 1
- Source 2
- Source 3
- whether metadata fully match across sources
- any discrepancy explicitly

If metadata disagree materially, preserve the discrepancy and use:

Uncertain, verify manually.

Do not fabricate a DOI, venue, or publication year just to make the note cleaner.

## 6. Comparison Framework Rule

Comparison work must be broad, measurable, and non-winner by default.

Use these rules:

1. compare within category first
2. higher still means better, even for burden or risk columns
3. use explicit measurable attributes, not vague impressions
4. keep a separate confidence score
5. do not create a hidden winner through one overall score unless the user explicitly asks for that and approves the consequences

Default scoring scale:

- 1 = very unfavorable
- 2 = unfavorable
- 3 = mixed / conditional / moderate
- 4 = favorable
- 5 = very favorable

## 7. Similarity and Tie Handling Rule

To avoid fake distinctions:

- if two compared methods differ by 0.3 or less on a grouped score, treat them as effectively similar on that dimension
- if they differ by 0.4 to 0.7, treat the difference as moderate
- if they differ by 0.8 or more, treat the difference as materially meaningful

If two methods are genuinely close overall, say so explicitly.
Do not force an ordering for rhetorical neatness.

## 8. Research Comparison Output Rules

When producing comparison outputs:

- include comments for distinctive traits
- mention hardware dependencies if relevant
- mention special architecture assumptions if relevant
- mention strong compatibilities or hard incompatibilities if relevant
- distinguish intrinsic scientific attractiveness from current repo-stage fit
- distinguish benchmark integrity from predictive upside potential

Default rule:

- no single overall score
- no final winner selection
- no hidden recommendation ranking

## 9. Paper-Note Workflow

When creating paper notes:

1. verify paper metadata three times
2. record all three sources
3. preserve discrepancies explicitly
4. state what the paper supports
5. state what the paper does not support
6. state repository-fit implications
7. state modularity implications
8. preserve key literal quotes only when safely verified

Paper notes should be separate files, not absorbed silently into the main research document.

## 10. Self-Update Restrictions

This appendix should be edited only when one or more of the following change:

- the repository-first research workflow
- the additive research-document rule
- the literal paper verification workflow
- the default comparison scoring discipline
- the tie-handling rule
- the expected structure of paper notes or comparison outputs

If unsure whether a change is warranted, stop and ask.

## 11. Final Rule

Broadness in research mapping is good.
Premature narrowing into a winner is not.

Research comparison should maximize explicitness, measurability, and citation integrity before any final architectural commitment is considered.
