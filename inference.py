from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    from traffic_control_env.models import (
        TaskId,
        TrafficCommand,
        TrafficControlAction,
        TrafficControlObservation,
    )
    from traffic_control_env.server import TrafficControlEnvironment
except ModuleNotFoundError:
    from models import TaskId, TrafficCommand, TrafficControlAction, TrafficControlObservation
    from server import TrafficControlEnvironment

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
ENV_BASE_URL = os.getenv("ENV_BASE_URL")
MAX_EXTRA_STEPS = 5


@dataclass
class EpisodeResult:
    task_id: str
    total_reward: float
    final_score: float
    steps: int
    strategy: str


def heuristic_policy(observation: TrafficControlObservation) -> TrafficCommand:
    if observation.emergency_direction is not None:
        direction = observation.emergency_direction.value
        if direction in ("north", "south"):
            if observation.current_phase.value == "ns_green":
                return TrafficCommand.HOLD_CURRENT_PHASE
            return TrafficCommand.SET_NS_GREEN
        if direction in ("east", "west"):
            if observation.current_phase.value == "ew_green":
                return TrafficCommand.HOLD_CURRENT_PHASE
            return TrafficCommand.SET_EW_GREEN

    ns_pressure = (
        observation.queue_north
        + observation.queue_south
        + observation.avg_wait_north
        + observation.avg_wait_south
    )
    ew_pressure = (
        observation.queue_east
        + observation.queue_west
        + observation.avg_wait_east
        + observation.avg_wait_west
    )

    if ns_pressure >= ew_pressure:
        return (
            TrafficCommand.HOLD_CURRENT_PHASE
            if observation.current_phase.value == "ns_green"
            else TrafficCommand.SET_NS_GREEN
        )

    return (
        TrafficCommand.HOLD_CURRENT_PHASE
        if observation.current_phase.value == "ew_green"
        else TrafficCommand.SET_EW_GREEN
    )


def llm_policy(observation: TrafficControlObservation) -> Optional[TrafficCommand]:
    if not (MODEL_NAME and HF_TOKEN):
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    prompt = f"""
You control one 4-way traffic intersection.
Choose exactly one command from:
- set_ns_green
- set_ew_green
- hold_current_phase
- set_all_red

Current state:
- current_phase: {observation.current_phase.value}
- current_timestep: {observation.current_timestep}
- queue_north: {observation.queue_north}
- queue_south: {observation.queue_south}
- queue_east: {observation.queue_east}
- queue_west: {observation.queue_west}
- avg_wait_north: {observation.avg_wait_north:.2f}
- avg_wait_south: {observation.avg_wait_south:.2f}
- avg_wait_east: {observation.avg_wait_east:.2f}
- avg_wait_west: {observation.avg_wait_west:.2f}
- emergency_present: {observation.emergency_present}
- emergency_direction: {observation.emergency_direction.value if observation.emergency_direction else "none"}
- time_since_last_phase_change: {observation.time_since_last_phase_change}

Reply with only the command text.
""".strip()

    try:
        response = client.responses.create(model=MODEL_NAME, input=prompt)
        output_text = getattr(response, "output_text", "").strip().lower()
        if not output_text:
            return None
        first_line = output_text.splitlines()[0].strip()
        allowed = {command.value: command for command in TrafficCommand}
        return allowed.get(first_line)
    except Exception:
        return None


def choose_action(observation: TrafficControlObservation) -> tuple[TrafficCommand, str]:
    llm_choice = llm_policy(observation)
    if llm_choice is not None:
        return llm_choice, "llm"
    return heuristic_policy(observation), "heuristic"


def run_local_episode(task_id: TaskId) -> EpisodeResult:
    env = TrafficControlEnvironment()
    observation = env.reset(task_id=task_id.value)
    total_reward = float(observation.reward or 0.0)
    strategy = "heuristic"

    safety_limit = env._task.horizon_steps + MAX_EXTRA_STEPS
    while not observation.done and env.state.step_count < safety_limit:
        command, strategy = choose_action(observation)
        observation = env.step(TrafficControlAction(command=command))
        total_reward += float(observation.reward or 0.0)

    return EpisodeResult(
        task_id=task_id.value,
        total_reward=total_reward,
        final_score=float(env.state.final_score or 0.0),
        steps=env.state.step_count,
        strategy=strategy,
    )


def main() -> None:
    if ENV_BASE_URL:
        print("ENV_BASE_URL is set, but this baseline currently runs against the local environment class.")
        print("Unset ENV_BASE_URL to use the local baseline mode.")
        return

    results = [run_local_episode(task_id) for task_id in TaskId]
    average_score = sum(result.final_score for result in results) / len(results)

    print("Traffic Control baseline results")
    print("=" * 44)
    for result in results:
        print(
            f"{result.task_id:>6} | steps={result.steps:>2} | "
            f"score={result.final_score:.3f} | total_reward={result.total_reward:.3f} | "
            f"strategy={result.strategy}"
        )
    print("-" * 44)
    print(f"average_score={average_score:.3f}")


if __name__ == "__main__":
    main()
