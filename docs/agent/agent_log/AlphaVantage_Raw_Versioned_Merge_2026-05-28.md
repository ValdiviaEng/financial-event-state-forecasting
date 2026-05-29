# Alpha Vantage Raw Versioned Merge - 2026-05-28

## Scope
- Merge roots: `data/raw/alphavantage/` and `data/raw_zip2_extended_granularity/raw/alphavantage/`.
- Output root: `data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z/`.
- Canonical root overwrite: no.
- Live provider calls: no.
- Benchmark or model claim: no.

## Tools
- Merge script: `scripts/merge_alphavantage_news_raw_roots.py`.
- Output validator: `scripts/validate_alphavantage_news_merge_output.py`.
- Validator command: `source ~/venvs/ai/bin/activate && python scripts/validate_alphavantage_news_merge_output.py --run-root data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z`.
- Validator result: `MERGE_OUTPUT_VALID files=1408 rows=608238 provenance_rows=608238`.

## Merge Summary
- Input news files: `2187`.
- Valid input news files: `2187`.
- Invalid input news files: `0`.
- Output news files: `1408`.
- Source feed rows before within-window exact article dedupe: `852197`.
- Retained merged feed rows: `608238`.
- Exact duplicate article rows removed within ticker/window files: `243959`.
- Non-identical article-identity collision groups preserved rather than collapsed: `48740`.
- Non-identical article variants preserved within those collision groups: `97480`.
- `Zone.Identifier` sidecars ignored: `1602`.
- Duplicate file-content hash groups detected across inputs: `660`.
- Shared relative paths with different file hashes: `114`.
- Top-50 annual/current coverage in merged output: `850/850`, missing `0`.

## Truncation And Empty-Feed Audit
- Likely truncated output files at `limit=1000`: `309`.
- Likely truncated by window shape: annual `53`, annual-current `43`, current-partial `32`, custom `1`, monthly `103`, quarterly `77`.
- Empty output files: `10`.
- Empty output files by ticker: `ABBV=1`, `BRK.B=1`, `GEV=1`, `LIN=3`, `PLTR=4`.

## Output Manifests
- Merge summary: `data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z/manifests/merge_summary.json`.
- File manifest: `data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z/manifests/file_manifest.json`.
- Article provenance JSONL: `data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z/manifests/feed_article_provenance.jsonl`.
- Duplicate file hash groups: `data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z/manifests/duplicate_file_hash_groups.json`.
- Support file manifest: `data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z/manifests/support_file_manifest.json`.

## Non-Claims
- This is not a provider-completeness claim.
- This is not a Stage 2 through Stage 6 rerun.
- This is not a benchmark result, model result, live forecast, trading signal, or service/API/dashboard artifact.
- Remaining truncated files are explicitly preserved as limitation evidence.
- Canonical adoption or overwrite of `data/raw/alphavantage/` remains blocked pending explicit user approval.
