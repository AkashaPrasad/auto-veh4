from __future__ import annotations

try:
    from .models import Direction, SignalPhase, TaskId, TaskScenario, VehicleSpawn, VehicleType
except ImportError:
    from models import Direction, SignalPhase, TaskId, TaskScenario, VehicleSpawn, VehicleType


EASY_TASK = TaskScenario(
    task_id=TaskId.EASY,
    name="Normal Traffic Flow",
    description=(
        "Balanced traffic without emergency vehicles. The controller should keep "
        "queues short and move vehicles steadily."
    ),
    horizon_steps=12,
    initial_phase=SignalPhase.NS_GREEN,
    pass_capacity_per_lane=1,
    spawn_schedule=[
        VehicleSpawn(arrival_step=0, direction=Direction.NORTH, count=2),
        VehicleSpawn(arrival_step=0, direction=Direction.SOUTH, count=1),
        VehicleSpawn(arrival_step=1, direction=Direction.EAST, count=2),
        VehicleSpawn(arrival_step=2, direction=Direction.WEST, count=2),
        VehicleSpawn(arrival_step=3, direction=Direction.NORTH, count=1),
        VehicleSpawn(arrival_step=4, direction=Direction.SOUTH, count=2),
        VehicleSpawn(arrival_step=5, direction=Direction.EAST, count=1),
        VehicleSpawn(arrival_step=7, direction=Direction.WEST, count=1),
        VehicleSpawn(arrival_step=8, direction=Direction.NORTH, count=1),
    ],
    grader_weights={
        "throughput": 0.5,
        "average_wait": 0.35,
        "stability": 0.15,
    },
)


MEDIUM_TASK = TaskScenario(
    task_id=TaskId.MEDIUM,
    name="Emergency Priority",
    description=(
        "Moderate traffic with one emergency vehicle appearing mid-episode. "
        "The controller should keep traffic moving while clearing the emergency lane quickly."
    ),
    horizon_steps=14,
    initial_phase=SignalPhase.EW_GREEN,
    pass_capacity_per_lane=1,
    spawn_schedule=[
        VehicleSpawn(arrival_step=0, direction=Direction.EAST, count=2),
        VehicleSpawn(arrival_step=0, direction=Direction.WEST, count=1),
        VehicleSpawn(arrival_step=1, direction=Direction.NORTH, count=2),
        VehicleSpawn(arrival_step=2, direction=Direction.SOUTH, count=2),
        VehicleSpawn(arrival_step=3, direction=Direction.WEST, count=2),
        VehicleSpawn(
            arrival_step=4,
            direction=Direction.NORTH,
            vehicle_type=VehicleType.EMERGENCY,
            count=1,
        ),
        VehicleSpawn(arrival_step=5, direction=Direction.EAST, count=1),
        VehicleSpawn(arrival_step=6, direction=Direction.SOUTH, count=2),
        VehicleSpawn(arrival_step=8, direction=Direction.WEST, count=1),
    ],
    grader_weights={
        "throughput": 0.35,
        "average_wait": 0.25,
        "emergency_handling": 0.3,
        "stability": 0.1,
    },
)


HARD_TASK = TaskScenario(
    task_id=TaskId.HARD,
    name="Heavy Congestion With Late Emergency",
    description=(
        "High congestion builds up before an emergency vehicle appears. The controller "
        "must recover flow and still prioritize the emergency lane."
    ),
    horizon_steps=16,
    initial_phase=SignalPhase.ALL_RED,
    pass_capacity_per_lane=1,
    spawn_schedule=[
        VehicleSpawn(arrival_step=0, direction=Direction.NORTH, count=3),
        VehicleSpawn(arrival_step=0, direction=Direction.SOUTH, count=2),
        VehicleSpawn(arrival_step=0, direction=Direction.EAST, count=3),
        VehicleSpawn(arrival_step=1, direction=Direction.WEST, count=3),
        VehicleSpawn(arrival_step=2, direction=Direction.NORTH, count=2),
        VehicleSpawn(arrival_step=2, direction=Direction.EAST, count=2),
        VehicleSpawn(arrival_step=3, direction=Direction.SOUTH, count=2),
        VehicleSpawn(arrival_step=4, direction=Direction.WEST, count=2),
        VehicleSpawn(arrival_step=5, direction=Direction.NORTH, count=2),
        VehicleSpawn(
            arrival_step=6,
            direction=Direction.WEST,
            vehicle_type=VehicleType.EMERGENCY,
            count=1,
        ),
        VehicleSpawn(arrival_step=7, direction=Direction.EAST, count=2),
        VehicleSpawn(arrival_step=8, direction=Direction.SOUTH, count=2),
        VehicleSpawn(arrival_step=10, direction=Direction.NORTH, count=1),
    ],
    grader_weights={
        "throughput": 0.25,
        "average_wait": 0.2,
        "emergency_handling": 0.35,
        "fairness": 0.2,
    },
)


TASK_BANK = {
    TaskId.EASY: EASY_TASK,
    TaskId.MEDIUM: MEDIUM_TASK,
    TaskId.HARD: HARD_TASK,
}

DEFAULT_TASK_ID = TaskId.EASY


def list_tasks() -> list[TaskScenario]:
    return [TASK_BANK[TaskId.EASY], TASK_BANK[TaskId.MEDIUM], TASK_BANK[TaskId.HARD]]


def get_task(task_id: str | TaskId) -> TaskScenario:
    normalized = TaskId(task_id)
    return TASK_BANK[normalized].model_copy(deep=True)
