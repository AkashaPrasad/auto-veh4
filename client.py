from __future__ import annotations

from typing import Dict

try:
    from openenv.core.client_types import StepResult
    from openenv.core.env_client import EnvClient
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "openenv-core is required to use the TrafficControlEnv client."
    ) from exc

from .models import TrafficControlAction, TrafficControlObservation, TrafficControlState


class TrafficControlEnv(
    EnvClient[TrafficControlAction, TrafficControlObservation, TrafficControlState]
):
    """Typed client for a running traffic-control environment server."""

    def _step_payload(self, action: TrafficControlAction) -> Dict:
        return action.model_dump(exclude_none=True)

    def _parse_result(self, payload: Dict) -> StepResult[TrafficControlObservation]:
        observation = TrafficControlObservation(**payload.get("observation", {}))
        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> TrafficControlState:
        return TrafficControlState(**payload)
