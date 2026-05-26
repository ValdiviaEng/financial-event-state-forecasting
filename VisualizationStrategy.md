# Visualization Strategy

Status: active v1p0 visualization strategy; static smoke report evidence exists for table readiness only

Updated: 2026-05-24

Primary authorities: `ArchitecturalDesignDecisions.md`, `ProjectDefinition.md`, `BenchmarkingStrategy.md`

## 1. Purpose

This document defines planned v1p0 visualizations, report/UI constraints, non-claims, accessibility expectations, and validation of displayed values.

A local v1p0 smoke report now exists with source-labeled metrics, strata, and uncertainty tables. Chart bundles, dashboards, APIs, live forecast displays, and publication-ready visualizations remain unevidenced and unapproved.

## 2. Report Boundary

| Boundary | Decision |
| --- | --- |
| Output form | Static local report artifacts only unless separately approved. |
| Dashboard/API | Not approved for v1p0 first slice. |
| Live forecast display | Not approved. |
| Trading display | No buy/sell, price target, portfolio, shorting, or advice language. |
| Stage 6 | Do not reinterpret v0p9 Stage 6. |

## 3. Planned Visualizations

| Visualization | Purpose | Inputs | Validation |
| --- | --- | --- | --- |
| Per-horizon metric table | Compare candidate models by horizon. | Metrics tables. | Table values equal source metrics. |
| Hurdle delta table | Show delta versus selected market hurdle. | Paired comparisons. | Deterministic join and sign checks. |
| Strata metric table | Show no-news/news-rich/truncation/article-count behavior. | Strata diagnostics. | Bucket definitions match manifests. |
| Fold dispersion chart | Show stability across folds. | Fold metrics. | Aggregations reproduce source rows. |
| Uncertainty interval table/chart | Show first uncertainty evidence. | CI outputs. | Interval method and sample count displayed. |
| Candidate caveat panel | Show non-claims and limitations. | Manifest limitations. | Required caveat strings present. |
| Historical marker view | If output packets exist, show historical model-output markers only. | Saved predictions and realized labels where available. | No projected price paths or fan charts. |

## 4. Accessibility Requirements

| Area | Requirement |
| --- | --- |
| Text | Plain-language caveats near each table/chart. |
| Color | Do not rely on color alone for sign or status. |
| Tables | Include column labels, units, model IDs, horizons, and row roles. |
| Static HTML | Use semantic headings and readable table structure. |
| Captions | Table-like displays should identify source tables or artifacts. |
| Export | Machine-readable CSV/Parquet/JSON must remain the source of truth. |

## 5. Value Fidelity Rules

| Rule | Requirement |
| --- | --- |
| Source-of-display | Rendered values must come from saved metric/diagnostic/report tables. |
| No recomputation drift | Report layer should not silently recompute metrics differently. |
| Determinism | Ranking, tie breaks, sorting, and formatting must be deterministic. |
| Provenance | Every display must identify source artifact, model ID, horizon, and row role. |
| Non-claims | Caveat text must be tested for required phrases. |

## 6. Smoke Tests

| Test | Purpose |
| --- | --- |
| Report generation smoke | Ensure minimal report writes without provider calls. |
| Table fidelity test | Compare rendered table values to source table values. |
| Caveat test | Verify required non-claim wording exists. |
| Accessibility smoke | Verify headings/tables/alt or caption text exist where practical. |
| No forbidden strings | Reject buy/sell/advice/price-target wording unless explicitly approved. |

## 7. Completion Rule

Visualization/report work is complete only after source tables, report artifacts, fidelity tests, and memory evidence exist. Design text alone is not output evidence.
