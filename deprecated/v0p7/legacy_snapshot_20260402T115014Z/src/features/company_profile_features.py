"""
Company-profile feature blueprint.

This file should eventually implement:
- static metadata features such as sector, industry, exchange, and SIC,
- optional embeddings of descriptive company text,
- optional time-indexed profile snapshots,
- null-safe handling when company-profile data is unavailable,
- profile-branch toggles for ablation studies.

Important future concerns:
- avoid leakage from current descriptions being used in historical periods,
- separate identity metadata from semantic profile features,
- keep this branch optional so the main pipeline stays tractable.
"""
