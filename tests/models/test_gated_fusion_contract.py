from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.models.gated_fusion import SimpleGatedFusionRegressor  # noqa: E402


def test_simple_gated_fusion_requires_market_and_event_features() -> None:
    model = SimpleGatedFusionRegressor(n_market_features=2, gate_feature_indices=[0], alpha=1.0)
    X = np.array(
        [
            [1.0, 0.5, 2.0, 0.0],
            [0.2, 0.1, 0.0, 1.0],
            [1.5, 0.4, 3.0, 0.0],
            [0.7, 0.2, 1.0, 0.0],
        ]
    )
    y = np.array([0.1, -0.2, 0.2, 0.0])

    model.fit(X, y)
    predictions = model.predict(X)

    assert predictions.shape == (4,)
    assert np.isfinite(predictions).all()


def test_simple_gated_fusion_rejects_missing_event_state_branch() -> None:
    model = SimpleGatedFusionRegressor(n_market_features=2, gate_feature_indices=[0], alpha=1.0)
    X = np.array([[1.0, 0.5], [0.2, 0.1]])
    y = np.array([0.1, -0.2])

    with pytest.raises(ValueError, match="event-state features"):
        model.fit(X, y)


def test_simple_gated_fusion_rejects_bad_gate_index() -> None:
    model = SimpleGatedFusionRegressor(n_market_features=2, gate_feature_indices=[4], alpha=1.0)
    X = np.array([[1.0, 0.5, 2.0], [0.2, 0.1, 0.0]])
    y = np.array([0.1, -0.2])

    with pytest.raises(ValueError, match="gate feature indices"):
        model.fit(X, y)
