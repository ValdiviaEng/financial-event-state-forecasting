RESEARCH COMPARISON ADDENDUM: REPOSITORY FIT AND MODULARITY COMPARISON

Purpose

This document extends `docs/research_results/research_comparison.md` without modifying it.

Its purpose is to compare methods and branches primarily on repository fit and modularity, because this project is already implemented enough that poor fit and poor modularity are real scientific risks, not just engineering inconveniences.


SECTION 1. REPO-FIT AND MODULARITY METHODOLOGY

This addendum focuses on six core repository questions.

1. Branch separability
- Can this family be implemented as a branch without silently changing upstream truths?

2. Swappability
- Can it be swapped in and out while preserving interfaces and benchmark comparability?

3. Blast radius
- How small is the number of repo layers it would touch?
- Higher score means lower blast radius.

4. Testing burden
- How little new test infrastructure does it require?
- Higher score means lower added testing burden.

5. Documentation burden
- How little explanatory and governance overhead does it create?
- Higher score means lower burden.

6. Rollback ease
- If the family fails, how easy is it to remove without destabilizing the repo?

7. Stale-risk creation
- How unlikely is it to create many downstream stale documents or stale claims?
- Higher score means lower stale-risk.

8. Config compatibility
- How naturally does it fit the repo’s existing config-driven structure?

9. Artifact compatibility
- How naturally can it use the current raw/interim/final/embeddings/manifests structure?

10. Evaluation compatibility
- How naturally does it fit the current saved-prediction, frozen-label evaluation style?


SECTION 2. FAMILIES COMPARED THROUGH REPO-FIT LENS

- conservative market branch
- pooled event-state branch
- event-state scalar enrichment branch
- static company metadata branch
- derivative appendix branch
- ranking-first branch
- uncertainty-aware output branch
- stronger frozen encoder branch
- dynamic profile branch
- graph / relation-aware branch
- end-to-end text fine-tuning branch
- MoE / expert-routing branch


SECTION 3. REPO-FIT PROFILES

Conservative market branch
- Branch separability: 5
- Swappability: 5
- Blast radius: 5
- Testing burden: 4
- Documentation burden: 4
- Rollback ease: 5
- Stale-risk creation: 4
- Config compatibility: 5
- Artifact compatibility: 5
- Evaluation compatibility: 5
- Comments:
  - best-fitting family in the whole repo
  - already a structural backbone

Pooled event-state branch
- Branch separability: 5
- Swappability: 4
- Blast radius: 4
- Testing burden: 4
- Documentation burden: 4
- Rollback ease: 4
- Stale-risk creation: 4
- Config compatibility: 5
- Artifact compatibility: 5
- Evaluation compatibility: 5
- Comments:
  - strongest current text-side branch
  - already deeply integrated but still modular

Event-state scalar enrichment branch
- Branch separability: 5
- Swappability: 5
- Blast radius: 4
- Testing burden: 4
- Documentation burden: 4
- Rollback ease: 5
- Stale-risk creation: 4
- Config compatibility: 5
- Artifact compatibility: 5
- Evaluation compatibility: 5
- Comments:
  - one of the cleanest extension families in the entire repo

Static company metadata branch
- Branch separability: 5
- Swappability: 5
- Blast radius: 4
- Testing burden: 4
- Documentation burden: 4
- Rollback ease: 5
- Stale-risk creation: 4
- Config compatibility: 4
- Artifact compatibility: 5
- Evaluation compatibility: 4
- Comments:
  - low-risk, high-modularity extension

Derivative appendix branch
- Branch separability: 5
- Swappability: 4
- Blast radius: 4
- Testing burden: 3
- Documentation burden: 3
- Rollback ease: 5
- Stale-risk creation: 3
- Config compatibility: 5
- Artifact compatibility: 5
- Evaluation compatibility: 4
- Comments:
  - technically easy to add and remove
  - scientifically risky if expanded too much

Ranking-first branch
- Branch separability: 3
- Swappability: 3
- Blast radius: 3
- Testing burden: 3
- Documentation burden: 3
- Rollback ease: 3
- Stale-risk creation: 3
- Config compatibility: 3
- Artifact compatibility: 4
- Evaluation compatibility: 3
- Comments:
  - objective-family shift more than a simple branch addition

Uncertainty-aware output branch
- Branch separability: 4
- Swappability: 4
- Blast radius: 3
- Testing burden: 2
- Documentation burden: 2
- Rollback ease: 4
- Stale-risk creation: 3
- Config compatibility: 3
- Artifact compatibility: 4
- Evaluation compatibility: 2
- Comments:
  - relatively modular architecturally
  - evaluation and reporting burden is the main repo cost

Stronger frozen encoder branch
- Branch separability: 4
- Swappability: 4
- Blast radius: 3
- Testing burden: 3
- Documentation burden: 3
- Rollback ease: 4
- Stale-risk creation: 3
- Config compatibility: 4
- Artifact compatibility: 5
- Evaluation compatibility: 4
- Comments:
  - good medium-friction extension

Dynamic profile branch
- Branch separability: 2
- Swappability: 2
- Blast radius: 2
- Testing burden: 1
- Documentation burden: 1
- Rollback ease: 2
- Stale-risk creation: 1
- Config compatibility: 2
- Artifact compatibility: 2
- Evaluation compatibility: 2
- Comments:
  - one of the weakest repo-fit directions now

Graph / relation-aware branch
- Branch separability: 2
- Swappability: 2
- Blast radius: 2
- Testing burden: 1
- Documentation burden: 2
- Rollback ease: 2
- Stale-risk creation: 2
- Config compatibility: 2
- Artifact compatibility: 2
- Evaluation compatibility: 2
- Comments:
  - relation construction and point-in-time safety create large blast radius

End-to-end text fine-tuning branch
- Branch separability: 2
- Swappability: 2
- Blast radius: 2
- Testing burden: 1
- Documentation burden: 2
- Rollback ease: 2
- Stale-risk creation: 2
- Config compatibility: 2
- Artifact compatibility: 1
- Evaluation compatibility: 2
- Comments:
  - breaks the strongest parts of the current frozen-artifact philosophy

MoE / expert-routing branch
- Branch separability: 2
- Swappability: 1
- Blast radius: 2
- Testing burden: 1
- Documentation burden: 1
- Rollback ease: 1
- Stale-risk creation: 1
- Config compatibility: 2
- Artifact compatibility: 2
- Evaluation compatibility: 2
- Comments:
  - highest repo-governance and benchmark burden among compared branches


SECTION 4. REPO-FIT AND MODULARITY TABLE

Family | BS | SW | BR | TB | DB | RE | SRC | CC | AC | EC | Comments
------ | -- | -- | -- | -- | -- | -- | --- | -- | -- | -- | --------
Conservative market branch | 5 | 5 | 5 | 4 | 4 | 5 | 4 | 5 | 5 | 5 | Best-fitting family in the repo
Pooled event-state branch | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 5 | Strong current text-side core
Event-state scalar enrichment | 5 | 5 | 4 | 4 | 4 | 5 | 4 | 5 | 5 | 5 | Cleanest event-state extension
Static company metadata | 5 | 5 | 4 | 4 | 4 | 5 | 4 | 4 | 5 | 4 | Strong low-risk extension
Derivative appendix | 5 | 4 | 4 | 3 | 3 | 5 | 3 | 5 | 5 | 4 | Easy to add, must stay narrow
Ranking-first branch | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | More of an objective-family shift
Uncertainty-aware outputs | 4 | 4 | 3 | 2 | 2 | 4 | 3 | 3 | 4 | 2 | Eval burden is the main cost
Stronger frozen encoder | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 4 | 5 | 4 | Good medium-friction extension
Dynamic profile branch | 2 | 2 | 2 | 1 | 1 | 2 | 1 | 2 | 2 | 2 | High stale-risk and leakage risk
Graph / relation-aware branch | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | Large repo blast radius
End-to-end text fine-tuning | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | Breaks frozen-artifact simplicity
MoE / expert routing | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | Highest governance and maintenance burden

Legend
- BS = Branch separability
- SW = Swappability
- BR = Blast radius, higher means lower blast radius
- TB = Testing burden, higher means lower burden
- DB = Documentation burden, higher means lower burden
- RE = Rollback ease
- SRC = Stale-risk creation, higher means lower stale-risk
- CC = Config compatibility
- AC = Artifact compatibility
- EC = Evaluation compatibility


SECTION 5. NON-DECISION SUMMARY FOR REPO FIT AND MODULARITY

This addendum does not pick what should be implemented next.

What it shows clearly is:
- the current repo is best suited to conservative market, pooled event-state, scalar event-state enrichments, and static metadata additions
- derivative appendix work is technically easy and rollback-friendly, which partly explains why it is tempting
- dynamic profile, graph-heavy, end-to-end text, and MoE directions all have high repo blast radius and high stale-risk creation
- repo-fit and scientific attractiveness are not the same thing, and this distinction should remain explicit in future discussions
