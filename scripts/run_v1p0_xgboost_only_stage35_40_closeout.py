from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import run_xgboost_only_stage35_40_closeout  # noqa: E402


def main() -> None:
    outputs = run_xgboost_only_stage35_40_closeout()
    stage40 = outputs[-1]
    print(
        json.dumps(
            {
                "status": "completed_xgboost_only_nonclaiming",
                "stage_statuses": {f"stage_{output.stage:02d}": output.status for output in outputs},
                "stage40_manifest": stage40.summary["manifest"],
                "positive_claim_approved": False,
                "benchmark_comparability_promotion_approved": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
