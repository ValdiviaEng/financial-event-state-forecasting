# Passdown Prompts For v1p0 Planning

Status: draft passdown for a fresh conversation.

Use this document as the starting prompt sequence for the next agent/session. It corrects paths, tightens approval gates, and keeps the intended v1p0 direction without overloading the first message.

## Recommendation

Start a fresh conversation after this passdown is saved and committed/pushed if possible. The current conversation has enough history to be noisy, and v1p0 will involve a major documentation and structure reset. A fresh session should read the documents listed below and treat this passdown as the operating plan.

## Non-Negotiable Rules

- Do not inspect private SSH keys.
- Do not change `AgentRules.md` or any `docs/agent/Agent*.md` file without explicit user approval first.
- Do not delete information. Consolidate first, verify, then deprecate only after approval.
- If deleting or superseding any active file, first preserve it under root `deprecated/v0p9/<domain>/<OriginalPath>` or the nearest equivalent path.
- Treat `docs/NextSteps_Brainstorming.md` as the foundation for v1p0 decisions until it is consolidated into `ArchitecturalDesignDecisions.md`.
- Preserve the distinction between implemented truth, research synthesis, and design-only roadmap.
- Do not run live provider calls, mutate raw data, rerun benchmarks, reinterpret Stage 6, create trading signals, create service/API/dashboard scope, or promote comparability unless explicitly approved.

## Corrected Core File List

Read these first:

- `AgentRules.md`
- `docs/agent/AgentAppendices.md`
- `docs/agent/AgentCompliance.md`
- `docs/agent/AgentGlossary.md`
- `docs/agent/AgentMemory.md`
- `docs/agent/AgentResearchWorkflows.md`
- `docs/agent/AgentTemplates.md`
- `ProjectDefinition.md`
- `ResearchTruth.md`
- `ScopeDefinition.md`
- `ScopeDecisionLog.md`
- `docs/NextSteps_Brainstorming.md`
- `UsageManual.md`
- `docs/Architecture_Map.md`
- `Complete_guidebook.txt`
- `ExecutionFlow.md`
- `ExecutionPipeline.md`

If `ArchitecturalDesignDecisions.md` does not exist yet, create it during the consolidation step below.

## Prompt 1: Reconstruct Current State

Read all agent rules files and all core documentation files listed above. Reconstruct the current project state, the completed v0p9 status, the Stage 6 `clean_null` result, the Stage 10C historical-prediction boundary, and the selected v1p0 roadmap.

Do not edit files in this step unless a file is missing and the user explicitly approves creating a placeholder.

## Prompt 2: Consolidate Final Design Decisions

Create `ArchitecturalDesignDecisions.md` as the final active decision file for v1p0.

Consolidate the contents of:

- `docs/NextSteps_Brainstorming.md`
- `ScopeDecisionLog.md`
- `ScopeDefinition.md`

Priority for contradictions:

1. `docs/NextSteps_Brainstorming.md`
2. `ScopeDecisionLog.md`
3. `ScopeDefinition.md`

Rules:

- Preserve all non-contradictory information.
- Do not silently drop details.
- If something is contradictory, outdated, or truly irrelevant, mark it in a short reconciliation note instead of deleting it silently.
- Keep a section for deprecated/resolved v0p9 decisions and a section for active v1p0 decisions.
- Clearly label design truth vs implemented truth.
- Ask the user if any contradiction cannot be resolved from the priority order.

## Prompt 3: Deprecate Superseded Decision Files Only After Verification

After `ArchitecturalDesignDecisions.md` is created and verified, ask the user before deleting or removing active references to the source files.

If approved, move or preserve superseded documentation files under:

- `deprecated/v0p9/docs/`

At minimum, preserve:

- `deprecated/v0p9/docs/NextSteps_Brainstorming.md`
- `deprecated/v0p9/docs/ScopeDecisionLog.md`
- `deprecated/v0p9/docs/ScopeDefinition.md`

Do not delete active files until:

- the consolidation is complete,
- references are updated,
- the user approves deletion/deprecation,
- and no information-loss risk remains.

For code deprecation, use the root versioned archive:

- `deprecated/v0p9/src/`

The older root `deprecated_version/` archive has been normalized to:

- `deprecated/v0p7/`

Do not move code until imports, tests, and planned v1p0 structure are understood.

## Prompt 4: Update Project Definition For v1p0

Update `ProjectDefinition.md` from:

- `ArchitecturalDesignDecisions.md`
- `ResearchTruth.md`
- current validated repository state

The updated project definition should describe v1p0 as a versioned first-slice implementation focused on performance and credibility while preserving benchmark discipline.

It should not claim that v1p0 has been implemented until the code and validation artifacts exist.

## Prompt 5: Establish v1p0 Naming

From this point forward, call the next implementation version `v1p0` when naming plans, folders, manifests, docs, and candidate artifact families.

Do not relabel v0p9 artifacts as v1p0. v0p9 remains historical/completed state.

## Prompt 6: Initial Sanitization Stage

Plan and execute an initial sanitization stage before modeling work.

Goals:

- Make active context files consistent with v1p0.
- Convert `UsageManual.md` into a barebones placeholder/manual skeleton until v1p0 outputs exist.
- Update or remove stale documentation in `docs/` only after preserving deprecated copies.
- Move `docs/Architecture_Map.md` to root as `Architecture_Map.md` if approved and update references.
- Update `Complete_guidebook.txt` to match the v1p0 architecture and file flow.

For every folder/file in the architecture map, include:

- purpose and intent,
- objective(s),
- expected inputs,
- expected outputs,
- data types or artifact types,
- dependencies,
- owner stage or prompt,
- validation or smoke-test expectation.

The guidebook should be more detailed than the architecture map and should describe file connections and intended implementation flow using comments/placeholders before code is generated.

## Prompt 7: Agent Rules Improvement Review

Review `AgentRules.md` and `docs/agent/Agent*.md` for possible improvements based on the full interaction history.

Do not edit those files directly.

Instead, produce a proposed change list with:

- file path,
- proposed change,
- reason,
- risk,
- whether it preserves existing rule intent,
- exact text if useful.

Ask for explicit approval before applying any change.

When updating references, replace temporary references to `docs/NextSteps_Brainstorming.md` with `ArchitecturalDesignDecisions.md` only after the consolidation exists.

## Prompt 8: Create Strategy Documents

Create these v1p0 strategy documents as active planning files:

- `LearningStrategy.md`: methodology for data processing, feature construction, leakage controls, model learning, train/validation behavior, and smoke tests.
- `BenchmarkingStrategy.md`: benchmark design choices, candidate promotion gates, diagnostics, statistical tests, and evidence required for claims.
- `VisualizationStrategy.md`: planned v1p0 visualizations, report/UI constraints, non-claims, accessibility, and validation of displayed values.
- `Unilu_Compatibility_requirements.md`: initially mostly comments/placeholders for future University of Luxembourg Iris cluster compatibility, environment constraints, reproducibility notes, and adaptation hooks.

Keep these documents design/planning only until implementation evidence exists.

## Prompt 9: Plan The v1p0 First Slice

Create a detailed `ExecutionFlow.md` for v1p0 first-slice implementation.

Requirements:

- Prefer many small stages.
- Each stage needs purpose, objectives, explicit paths, inputs, outputs, dependencies, smoke tests, completion criteria, and success metrics.
- Include readiness checks before moving to the next stage.
- Keep documentation updates as part of each stage.
- Use `ArchitecturalDesignDecisions.md` and `ResearchTruth.md` as top-level project truth.
- Compare reuse vs rewrite from `deprecated/v0p9/src/` or current v0p9 code. Reuse only if compatibility is cleaner than rewriting.
- Make compatibility tests mandatory when reusing old code.

The first slice should cover the selected integrated thin slice:

- v1p0 versioning and registry setup,
- sidecar feature registry,
- lag/rolling market features,
- lag-linear baseline,
- fixed XGBoost baseline,
- initial diagnostics core,
- stratified metrics,
- Stage 10C clarity/report-fidelity updates.

## Prompt 10: Create Stage Execution Prompts

Create individual detailed execution prompts for each v1p0 stage from `ExecutionFlow.md`.

Each prompt should reference:

- `ArchitecturalDesignDecisions.md`,
- `ResearchTruth.md`,
- `Architecture_Map.md`,
- `Complete_guidebook.txt`,
- `LearningStrategy.md`,
- `BenchmarkingStrategy.md` for benchmark stages,
- `VisualizationStrategy.md` for reporting/visualization stages.

Some stages may be testing-only or documentation-only. Make that explicit.

## Prompt 11: Execute First Slice

Execute v1p0 first slice stage-by-stage.

For each stage:

- follow its prompt,
- update documentation as part of completion,
- run smoke tests before continuing,
- update `ResearchTruth.md` only when new implemented truth or validated evidence exists,
- update `ArchitecturalDesignDecisions.md` only for decisions, not transient notes,
- update `UsageManual.md` only when a real v1p0 usage path exists.

Ask when documentation conflicts cannot be resolved by hierarchy.

## Prompt 12: Retrospective After First Slice

After the first slice is complete, run a retrospective.

Ask the user about each proposed new decision individually before adding it to `ArchitecturalDesignDecisions.md`.

Update `ResearchTruth.md` only for confirmed truths supported by artifacts, tests, manifests, or explicit user decisions.

## Prompt 13: Final v1p0 Sprint

After first-slice retrospective, execute the final v1p0 sprint focused on:

- testing,
- benchmarking,
- diagnostics,
- report fidelity,
- visualization readiness,
- documentation consistency.

Do not create positive claims unless benchmark evidence supports them.

## Prompt 14: Visualization And UI Work

Create planned visualizations and document them in `VisualizationStrategy.md`.

Create:

- `docs/visualization/`
- one documentation file per visualization

Each visualization document should include:

- purpose,
- source data,
- design choices,
- tests,
- validation against source tables,
- results,
- limitations,
- non-claims.

No dashboard/API/service scope unless explicitly approved.

## Prompt 15: LaTeX Report

Create LaTeX report documentation only when the project reaches that stage.

Before writing the report, ask the user for:

- reference reports,
- required structure,
- style preferences,
- target audience,
- required sections,
- citation style.

The report should include design choices, methodology, tests, results, limitations, and conclusions, with clear distinction between evidence and design intent.

## First Message For Fresh Conversation

Use this as the first user prompt in the new conversation:

```text
Read `docs/Passdown_NewPrompts.md` first. Then read all files listed in its Corrected Core File List. Reconstruct the current state and propose the first safe action.

Do not edit `AgentRules.md` or any `docs/agent/Agent*.md` file without explicit approval. Do not delete active files until consolidation is complete, deprecated copies exist, references are updated, and I approve.

The next implementation version is v1p0. The first goal is to consolidate decisions into `ArchitecturalDesignDecisions.md`, update project definition and architecture docs, then plan and execute the v1p0 first integrated thin slice.
```
