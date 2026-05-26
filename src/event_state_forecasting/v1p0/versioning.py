from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any


class V1P0ContractError(ValueError):
    """Raised when a v1p0 contract is malformed."""


def load_json_config(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def stable_digest(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return sha256(encoded).hexdigest()[:12]


def validate_version_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("implementation_version") != "v1p0":
        raise V1P0ContractError("version manifest must declare implementation_version=v1p0")
    family_id = str(manifest.get("benchmark_family_id", ""))
    if not family_id.endswith("_v1p0"):
        raise V1P0ContractError("benchmark_family_id must be explicitly v1p0")
    components = manifest.get("components")
    if not isinstance(components, list) or not components:
        raise V1P0ContractError("version manifest must list components")
    component_ids = [str(component.get("component_id", "")) for component in components]
    if len(component_ids) != len(set(component_ids)):
        raise V1P0ContractError("component_id values must be unique")
    for component_id in component_ids:
        if component_id.startswith("v0p9") or component_id.endswith("_v0p9"):
            raise V1P0ContractError("v0p9 component IDs cannot be relabeled as v1p0")
    result = dict(manifest)
    result["manifest_digest"] = stable_digest(manifest)
    return result
