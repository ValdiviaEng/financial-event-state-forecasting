# Legacy Deprecation Summary

A full snapshot of the previous repository state was archived at:

- `deprecated_version/legacy_snapshot_20260402T115014Z`

This root was intentionally cleared for a true fresh start.

What happened:
- every current top-level project item was moved into the snapshot
- hidden files were also moved when present, except for:
  - `.git/`
  - `deprecated_version/`
- this summary file was created at root
- the archival script copied itself into the snapshot for traceability

Top-level items archived:
- `.cache`
- `.env`
- `.env.example`
- `.gitignore`
- `.pytest_cache`
- `.ruff_cache`
- `Complete_guidebook.txt`
- `ExecutionFlow.md`
- `Expanded_Testing.md`
- `LICENSE`
- `Makefile`
- `README.md`
- `artifacts`
- `configs`
- `data`
- `docs`
- `execution_plan.txt`
- `notebooks`
- `project_extra_data.txt`
- `pyproject.toml`
- `reports`
- `requirements.txt`
- `runs`
- `src`
- `tests`

Where to look for details:
- full manifest: `deprecated_version/legacy_snapshot_20260402T115014Z/DEPRECATION_MANIFEST.txt`
- captured pre-archive tree: `deprecated_version/legacy_snapshot_20260402T115014Z/ROOT_TREE_BEFORE.txt`
- snapshot readme: `deprecated_version/legacy_snapshot_20260402T115014Z/README.md`

Recommended next step:
- create the new project structure from scratch at repo root
- reintroduce only what you can justify and defend from the archived snapshot
