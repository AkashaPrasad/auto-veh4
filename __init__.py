"""Traffic control OpenEnv environment package."""

from .models import (
    Direction,
    SignalPhase,
    TaskId,
    TaskScenario,
    TrafficCommand,
    TrafficControlAction,
    TrafficControlObservation,
    TrafficControlState,
    TrafficMetrics,
    VehicleRecord,
    VehicleSpawn,
    VehicleType,
)
from .server import TrafficControlEnvironment
from .task_bank import DEFAULT_TASK_ID, TASK_BANK, get_task, list_tasks

try:  # Optional until openenv-core is installed.
    from .client import TrafficControlEnv
except ImportError:  # pragma: no cover
    TrafficControlEnv = None  # type: ignore[assignment]

__all__ = [
    "DEFAULT_TASK_ID",
    "TASK_BANK",
    "Direction",
    "SignalPhase",
    "TaskId",
    "TaskScenario",
    "TrafficCommand",
    "TrafficControlAction",
    "TrafficControlEnv",
    "TrafficControlEnvironment",
    "TrafficControlObservation",
    "TrafficControlState",
    "TrafficMetrics",
    "VehicleRecord",
    "VehicleSpawn",
    "VehicleType",
    "get_task",
    "list_tasks",
]
