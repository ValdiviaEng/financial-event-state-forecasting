"""
Data layer package.

What this package should eventually contain:
- provider-specific client adapters,
- raw download orchestration,
- normalization logic,
- split and corporate-action handling,
- universe handling,
- final dataset assembly helpers.

Design rule:
- raw source access should be isolated here so that downstream feature and
  modeling code can depend on stable canonical tables instead of on provider
  response shapes.
"""
