"""Final exhaustive edge case testing for grading bounds."""
from typing import Dict, Any, List
import sys

try:
    from traffic_control_env.models import TaskId, TrafficControlAction, TrafficCommand, TaskScenario
    from traffic_control_env.server import TrafficControlEnvironment
    from traffic_control_env.task_bank import list_tasks
except ImportError:
    from models import TaskId, TrafficControlAction, TrafficCommand, TaskScenario
    from server import TrafficControlEnvironment
    from task_bank import list_tasks


def check_bounds(scores: Dict[str, float], label: str) -> bool:
    """Check if all scores are strictly in (0, 1)."""
    all_valid = True
    for key, value in scores.items():
        if not (0.0 < value < 1.0):
            print(f"  ✗ {label}: {key} = {value} OUT OF BOUNDS")
            all_valid = False
    return all_valid

def test_scenario(task_id: TaskId, control_strategy: str, strategy_func) -> bool:
    """Test a specific scenario."""
    env = TrafficControlEnvironment(default_task_id=task_id)
    obs = env.reset(task_id=task_id.value)
    
    step_count = 0
    while not obs.done and step_count < 1000:
        cmd = strategy_func(obs)
        obs = env.step(TrafficControlAction(command=cmd))
        step_count += 1
    
    state = env.state
    all_scores = {"final_score": state.final_score, **state.score_breakdown}
    
    valid = check_bounds(all_scores, f"{task_id.value}/{control_strategy}")
    return valid

def all_red_strategy(obs):
    return TrafficCommand.SET_ALL_RED

def ns_green_strategy(obs):
    return TrafficCommand.SET_NS_GREEN

def ew_green_strategy(obs):
    return TrafficCommand.SET_EW_GREEN

def hold_strategy(obs):
    return TrafficCommand.HOLD_CURRENT_PHASE

def random_strategy(obs):
    import random
    return random.choice([
        TrafficCommand.SET_NS_GREEN,
        TrafficCommand.SET_EW_GREEN,
        TrafficCommand.HOLD_CURRENT_PHASE,
        TrafficCommand.SET_ALL_RED,
    ])

def smart_strategy(obs):
    """Balance NS/EW traffic."""
    if obs.emergency_present:
        if obs.emergency_direction.value in ("north", "south"):
            return TrafficCommand.SET_NS_GREEN
        else:
            return TrafficCommand.SET_EW_GREEN
    
    ns_pressure = obs.queue_north + obs.queue_south + obs.avg_wait_north + obs.avg_wait_south
    ew_pressure = obs.queue_east + obs.queue_west + obs.avg_wait_east + obs.avg_wait_west
    
    if ns_pressure >= ew_pressure:
        return (TrafficCommand.HOLD_CURRENT_PHASE 
                if obs.current_phase.value == "ns_green" 
                else TrafficCommand.SET_NS_GREEN)
    else:
        return (TrafficCommand.HOLD_CURRENT_PHASE 
                if obs.current_phase.value == "ew_green" 
                else TrafficCommand.SET_EW_GREEN)

strategies = [
    ("all_red", all_red_strategy),
    ("ns_green_only", ns_green_strategy),
    ("ew_green_only", ew_green_strategy),
    ("hold_only", hold_strategy),
    ("random", random_strategy),
    ("smart", smart_strategy),
]

def main():
    print("="*70)
    print("EXHAUSTIVE EDGE CASE GRADING BOUNDS TEST")
    print("="*70)
    print()
    
    test_count = 0
    pass_count = 0
    
    for task_id in [TaskId.EASY, TaskId.MEDIUM, TaskId.HARD]:
        print(f"\n{'='*70}")
        print(f"TASK: {task_id.value.upper()}")
        print(f"{'='*70}")
        
        for strategy_name, strategy_func in strategies:
            try:
                test_count += 1
                print(f"\n  [{test_count}] Testing {strategy_name:20s} ...", end=" ")
                sys.stdout.flush()
                
                passed = test_scenario(task_id, strategy_name, strategy_func)
                
                if passed:
                    pass_count += 1
                    print("✓ PASS")
                else:
                    print("✗ FAIL")
                    
            except Exception as e:
                print(f"✗ EXCEPTION: {e}")
    
    print()
    print("="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Passed: {pass_count}/{test_count}")
    
    if pass_count == test_count:
        print("\n✓ ALL EDGE CASE TESTS PASSED!")
        print("Scores are strictly bounded to (0, 1) across all scenarios.")
        return 0
    else:
        print(f"\n✗ {test_count - pass_count} test(s) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
