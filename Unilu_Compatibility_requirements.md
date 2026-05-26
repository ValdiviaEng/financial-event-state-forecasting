# University of Luxembourg Iris Compatibility Requirements

Status: active v1p0 planning placeholder; mostly comments and future requirements

Updated: 2026-05-24

## 1. Purpose

This file records future compatibility requirements for running v1p0 work on the University of Luxembourg Iris cluster or similar HPC environments.

It is a planning placeholder only. It does not claim that Iris compatibility has been implemented, tested, or approved.

## 2. Current Status

| Area | Status |
| --- | --- |
| Iris account/project | Unknown; verify manually. |
| Module environment | Unknown; verify manually. |
| Python version | Unknown; verify manually. |
| GPU availability | Unknown; verify manually. |
| Storage quotas | Unknown; verify manually. |
| Scheduler details | Unknown; verify manually. |
| Network/provider policy | Unknown; verify manually. |

## 3. Future Environment Constraints

```text
# TODO: Record approved Iris partition/queue names.
# TODO: Record Python/module loading commands.
# TODO: Record CPU/GPU memory limits.
# TODO: Record wall-time limits for smoke tests and full runs.
# TODO: Record local scratch vs project storage paths.
# TODO: Record whether outbound network/provider calls are allowed.
# TODO: Record package-install policy and cache location.
```

## 4. Reproducibility Notes

```text
# TODO: Define environment capture format.
# TODO: Define dependency lockfile strategy.
# TODO: Define deterministic seed policy for CPU and GPU runs.
# TODO: Define artifact transfer and checksum policy.
# TODO: Define log redaction requirements before copying outputs off cluster.
```

## 5. Adaptation Hooks

| Hook | Future purpose |
| --- | --- |
| Config path overrides | Let local and Iris runs use different artifact roots without changing code. |
| Thread/process limits | Keep sklearn/XGBoost/PyTorch behavior scheduler-safe. |
| Temporary directory override | Avoid filling home directories. |
| Optional GPU switch | Keep first-slice CPU-capable while allowing future GPU stages. |
| No-network mode | Enforce provider-call prohibition on cluster runs unless approved. |

## 6. Validation Expectations

| Check | Purpose |
| --- | --- |
| Environment smoke | Print Python, package, CPU/GPU, and path information. |
| Config smoke | Load v1p0 configs with Iris path overrides. |
| Tiny model smoke | Run a small fold/sample without writing large artifacts. |
| Artifact write/read smoke | Confirm cluster storage paths are writable and readable. |
| No-network check | Ensure benchmark/model commands do not attempt provider calls. |

## 7. Non-Claims

This file does not approve cloud/HPC execution, provider calls, raw-data mutation, GPU-heavy modeling, or dependency expansion. Those remain separately approval-gated where applicable.
