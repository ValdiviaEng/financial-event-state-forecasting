"""Stage 7 policy selection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


SelectionSide = Literal["top", "bottom"]


class Stage7PolicyError(ValueError):
    """Raised when Stage 7 policy selection is invalid."""


@dataclass(frozen=True, slots=True)
class PolicySpec:
    policy_id: str
    policy_family: str
    score_column: str | None
    epsilon: float | None = None
    random_policy: bool = False


def select_top_bottom(
    frame: pd.DataFrame,
    *,
    k: int,
    score_column: str,
    policy_id: str,
    policy_family: str,
    epsilon: float | None,
    rng: np.random.Generator,
    force_random: bool = False,
) -> pd.DataFrame:
    if k <= 0:
        raise Stage7PolicyError("k must be positive")
    if len(frame) < k:
        raise Stage7PolicyError("cannot select k rows from a smaller candidate frame")
    working = frame.copy()
    exploration = bool(force_random)
    if not force_random and epsilon is not None and float(epsilon) > 0:
        exploration = bool(rng.random() < float(epsilon))
    if exploration:
        working["stage7_selection_score"] = rng.random(len(working))
    else:
        if score_column not in working.columns:
            raise Stage7PolicyError(f"missing policy score column: {score_column}")
        working["stage7_selection_score"] = working[score_column].astype("float64")

    top = rank_side(working, k=k, side="top")
    bottom = rank_side(working, k=k, side="bottom")
    selected = pd.concat([top, bottom], ignore_index=True)
    selected["policy_id"] = policy_id
    selected["policy_family"] = policy_family
    selected["k"] = int(k)
    selected["epsilon"] = np.nan if epsilon is None else float(epsilon)
    selected["exploration_used"] = exploration
    selected["selected_as"] = selected["selection_side"].map({"top": "upside_candidate", "bottom": "downside_avoid_candidate"})
    selected["trading_signal_approved"] = False
    return selected


def rank_side(frame: pd.DataFrame, *, k: int, side: SelectionSide) -> pd.DataFrame:
    ascending = side == "bottom"
    ranked = frame.sort_values(["stage7_selection_score", "canonical_ticker"], ascending=[ascending, True]).head(k).copy()
    ranked["selection_side"] = side
    ranked["selection_rank"] = np.arange(1, len(ranked) + 1)
    return ranked


def deterministic_rng(seed: int, *parts: object) -> np.random.Generator:
    payload = "|".join(str(part) for part in (seed, *parts))
    value = abs(hash(payload)) % (2**32)
    return np.random.default_rng(value)
