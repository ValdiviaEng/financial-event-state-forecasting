"""Test package marker.

The repository now contains a mixed testing stack:
- fast unit tests for core logic,
- integration-style synthetic workflow tests,
- opt-in live API tests under `tests/integration/`.

The live integration tests are intentionally skipped by default and should only
be run manually when API keys, quota, and network conditions are appropriate.
"""
