"""Market + event-state multimodal model builders."""

from __future__ import annotations

import importlib
from typing import Any


class MultimodalModelError(RuntimeError):
    """Raised when a multimodal model cannot be constructed safely."""


def build_multimodal_regressor(
    *,
    market_input_dim: int,
    output_dim: int,
    event_state_input_dim: int | None = None,
    company_input_dim: int | None = None,
    market_hidden_dim: int = 64,
    event_hidden_dim: int = 32,
    company_hidden_dim: int = 16,
    fusion_hidden_dim: int = 64,
    dropout: float = 0.0,
    use_event_state: bool = True,
    use_company_profile: bool = False,
) -> Any:
    """Build a simple multimodal regressor with gating.

    The first implementation intentionally keeps the architecture simple:
    - market encoder
    - event-state encoder
    - optional company encoder
    - event-state gating using market and event representations
    - final fusion MLP to multi-horizon regression outputs
    """

    try:
        torch = importlib.import_module("torch")
    except ModuleNotFoundError as exc:
        raise MultimodalModelError("PyTorch is required for multimodal models.") from exc

    nn = torch.nn

    if market_input_dim <= 0:
        raise MultimodalModelError("market_input_dim must be positive.")
    if output_dim <= 0:
        raise MultimodalModelError("output_dim must be positive.")
    if use_event_state and (event_state_input_dim is None or event_state_input_dim <= 0):
        raise MultimodalModelError("event_state_input_dim must be positive when use_event_state=True.")
    if use_company_profile and (company_input_dim is None or company_input_dim <= 0):
        raise MultimodalModelError("company_input_dim must be positive when use_company_profile=True.")

    def encoder(input_dim: int, hidden_dim: int) -> Any:
        layers: list[Any] = [nn.Linear(input_dim, hidden_dim), nn.ReLU()]
        if dropout > 0:
            layers.append(nn.Dropout(dropout))
        return nn.Sequential(*layers)

    class MarketEventStateRegressor(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.use_event_state = use_event_state
            self.use_company_profile = use_company_profile

            self.market_encoder = encoder(market_input_dim, market_hidden_dim)
            if self.use_event_state:
                self.event_encoder = encoder(int(event_state_input_dim), event_hidden_dim)
                self.event_gate = nn.Linear(market_hidden_dim + event_hidden_dim, event_hidden_dim)
            else:
                self.event_encoder = None
                self.event_gate = None

            if self.use_company_profile:
                self.company_encoder = encoder(int(company_input_dim), company_hidden_dim)
            else:
                self.company_encoder = None

            fusion_input_dim = market_hidden_dim
            if self.use_event_state:
                fusion_input_dim += event_hidden_dim
            if self.use_company_profile:
                fusion_input_dim += company_hidden_dim

            fusion_layers: list[Any] = [nn.Linear(fusion_input_dim, fusion_hidden_dim), nn.ReLU()]
            if dropout > 0:
                fusion_layers.append(nn.Dropout(dropout))
            fusion_layers.append(nn.Linear(fusion_hidden_dim, output_dim))
            self.regression_head = nn.Sequential(*fusion_layers)

        def forward(
            self,
            market_features: Any,
            *,
            event_state_features: Any | None = None,
            company_features: Any | None = None,
            event_state_mask: Any | None = None,
            company_mask: Any | None = None,
        ) -> Any:
            market_repr = self.market_encoder(market_features)
            fused_parts = [market_repr]

            if self.use_event_state:
                if event_state_features is None:
                    raise MultimodalModelError("event_state_features must be provided when use_event_state=True.")
                event_repr = self.event_encoder(event_state_features)
                gate_input = torch.cat([market_repr, event_repr], dim=-1)
                gate = torch.sigmoid(self.event_gate(gate_input))
                if event_state_mask is not None:
                    gate = gate * event_state_mask.unsqueeze(-1)
                fused_parts.append(event_repr * gate)

            if self.use_company_profile:
                if company_features is None:
                    raise MultimodalModelError("company_features must be provided when use_company_profile=True.")
                company_repr = self.company_encoder(company_features)
                if company_mask is not None:
                    company_repr = company_repr * company_mask.unsqueeze(-1)
                fused_parts.append(company_repr)

            fused = torch.cat(fused_parts, dim=-1)
            return self.regression_head(fused)

    return MarketEventStateRegressor()
