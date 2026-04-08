"""Comprehensive test for grading score bounds verification.

Tests that all grading paths produce scores strictly within (0, 1).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Dict, List

try:
    from traffic_control_env.models import TaskId, TrafficControlAction, TrafficCommand
    from traffic_control_env.server import TrafficControlEnvironment
except ImportError:
    from models import TaskId, TrafficControlAction, TrafficCommand
    from server import TrafficControlEnvironment


@dataclass
class TestResult:
    task_id: str
    test_name: str
    passed: bool
    scores: Dict[str, float]
    errors: List[str]


def validate_score_range(scores: Dict[str, float]) -> tuple[bool, List[str]]:
    """Validate that all scores are strictly in (0, 1).
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    for key, value in scores.items():
        if not isinstance(value, (int, float)):
            errors.append(f"  {key} = {value!r} (not a number)")
        elif value <= 0.0 or value >= 1.0:
            errors.append(f"  {key} = {value:.10f} (out of range (0, 1))")
        elif value < 0.01 or value > 0.99:
            errors.append(f"  {key} = {value:.10f} (outside strict bounds [0.01, 0.99])")
    return len(errors) == 0, errors


def test_perfect_performance(task_id: TaskId) -> TestResult:
    """Test scenario where everything goes perfectly."""
    test_name = "perfect_performance"
    env = TrafficControlEnvironment(default_task_id=task_id)
    observation = env.reset(task_id=task_id.value)
    errors = []

    # Run for all steps with optimal control (prioritize highest pressure)
    while not observation.done:
        queue_north = observation.queue_north
        queue_south = observation.queue_south
        queue_east = observation.queue_east
        queue_west = observation.queue_west

        # Handle emergency first
        if observation.emergency_present:
            if observation.emergency_direction.value in ("north", "south"):
                command = TrafficCommand.SET_NS_GREEN
            else:
                command = TrafficCommand.SET_EW_GREEN
        else:
            # Balance traffic
            ns_pressure = queue_north + queue_south
            ew_pressure = queue_east + queue_west
            if ns_pressure >= ew_pressure:
                command = (
                    TrafficCommand.HOLD_CURRENT_PHASE
                    if observation.current_phase.value == "ns_green"
                    else TrafficCommand.SET_NS_GREEN
                )
            else:
                command = (
                    TrafficCommand.HOLD_CURRENT_PHASE
                    if observation.current_phase.value == "ew_green"
                    else TrafficCommand.SET_EW_GREEN
                )

        action = TrafficControlAction(command=command)
        observation = env.step(action)

    # Get final scores
    final_score = env.state.final_score
    score_breakdown = env.state.score_breakdown
    
    if final_score is None:
        errors.append("final_score is None")
        return TestResult(task_id.value, test_name, False, {}, errors)

    all_scores = {"final_score": final_score, **score_breakdown}
    is_valid, range_errors = validate_score_range(all_scores)
    errors.extend(range_errors)

    return TestResult(
        task_id.value,
        test_name,
        is_valid and len(errors) == 0,
        all_scores,
        errors,
    )


def test_poor_performance(task_id: TaskId) -> TestResult:
    """Test scenario with poor control."""
    test_name = "poor_performance"
    env = TrafficControlEnvironment(default_task_id=task_id)
    observation = env.reset(task_id=task_id.value)
    errors = []

    # Run for all steps with poor control (random phase)
    import itertools
    phases = itertools.cycle([
        TrafficCommand.SET_NS_GREEN,
        TrafficCommand.SET_EW_GREEN,
        TrafficCommand.HOLD_CURRENT_PHASE,
    ])

    while not observation.done:
        command = next(phases)
        action = TrafficControlAction(command=command)
        observation = env.step(action)

    # Get final scores
    final_score = env.state.final_score
    score_breakdown = env.state.score_breakdown

    if final_score is None:
        errors.append("final_score is None")
        return TestResult(task_id.value, test_name, False, {}, errors)

    all_scores = {"final_score": final_score, **score_breakdown}
    is_valid, range_errors = validate_score_range(all_scores)
    errors.extend(range_errors)

    return TestResult(
        task_id.value,
        test_name,
        is_valid and len(errors) == 0,
        all_scores,
        errors,
    )


def test_hold_current_phase(task_id: TaskId) -> TestResult:
    """Test scenario where we always hold current phase."""
    test_name = "hold_current_phase"
    env = TrafficControlEnvironment(default_task_id=task_id)
    observation = env.reset(task_id=task_id.value)
    errors = []

    # Always hold current phase
    while not observation.done:
        command = TrafficCommand.HOLD_CURRENT_PHASE
        action = TrafficControlAction(command=command)
        observation = env.step(action)

    # Get final scores
    final_score = env.state.final_score
    score_breakdown = env.state.score_breakdown

    if final_score is None:
        errors.append("final_score is None")
        return TestResult(task_id.value, test_name, False, {}, errors)

    all_scores = {"final_score": final_score, **score_breakdown}
    is_valid, range_errors = validate_score_range(all_scores)
    errors.extend(range_errors)

    return TestResult(
        task_id.value,
        test_name,
        is_valid and len(errors) == 0,
        all_scores,
        errors,
    )


def test_early_termination(task_id: TaskId) -> TestResult:
    """Test scenario where we terminate early."""
    test_name = "early_termination"
    env = TrafficControlEnvironment(default_task_id=task_id)
    observation = env.reset(task_id=task_id.value)
    errors = []

    # Do just a few steps then check if scores are computed
    for _ in range(3):
        if observation.done:
            break
        command = TrafficCommand.HOLD_CURRENT_PHASE
        action = TrafficControlAction(command=command)
        observation = env.step(action)

    final_score = env.state.final_score
    score_breakdown = env.state.score_breakdown

    # Only validate if episode ended early
    if not observation.done:
        return TestResult(task_id.value, test_name, True, {}, ["Episode did not end early"])

    if final_score is None:
        errors.append("final_score is None")
        return TestResult(task_id.value, test_name, False, {}, errors)

    all_scores = {"final_score": final_score, **score_breakdown}
    is_valid, range_errors = validate_score_range(all_scores)
    errors.extend(range_errors)

    return TestResult(
        task_id.value,
        test_name,
        is_valid and len(errors) == 0,
        all_scores,
        errors,
    )


def print_result(result: TestResult, verbose: bool = True) -> bool:
    """Print test result. Returns True if passed."""
    status = "✓ PASS" if result.passed else "✗ FAIL"
    print(f"\n{status}: {result.task_id} - {result.test_name}")

    if verbose and result.scores:
        for key, value in sorted(result.scores.items()):
            if 0.0 < value < 1.0:
                marker = "✓"
            else:
                marker = "✗"
            print(f"  {marker} {key:20s} = {value:.6f}")

    if result.errors:
        for error in result.errors:
            print(f"  ✗ ERROR: {error}")

    return result.passed


def main() -> int:
    """Run all tests."""
    print("=" * 70)
    print("GRADING SCORE BOUNDS VERIFICATION TEST")
    print("=" * 70)
    print(f"\nValidating that all grading scores are strictly in (0, 1) exclusive.\n")

    results: List[TestResult] = []
    test_funcs = [
        test_perfect_performance,
        test_poor_performance,
        test_hold_current_phase,
        test_early_termination,
    ]

    for task_id in [TaskId.EASY, TaskId.MEDIUM, TaskId.HARD]:
        print(f"\n{'─' * 70}")
        print(f"Testing: {task_id.value.upper()}")
        print(f"{'─' * 70}")

        for test_func in test_funcs:
            try:
                result = test_func(task_id)
                results.append(result)
                print_result(result, verbose=True)
            except Exception as e:
                print(f"\n✗ EXCEPTION: {test_func.__name__}")
                print(f"  Error: {e}")
                import traceback
                traceback.print_exc()
                results.append(
                    TestResult(task_id.value, test_func.__name__, False, {}, [str(e)])
                )

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)
    print(f"Passed: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("\n✓ All tests passed! Scores are strictly bounded to (0, 1).")
        return 0
    else:
        print(f"\n✗ {total_count - passed_count} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
