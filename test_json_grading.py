"""Detailed test to verify grading bounds and JSON serialization."""
import json
from typing import Dict, Any

try:
    from traffic_control_env.models import TaskId, TrafficControlAction, TrafficCommand
    from traffic_control_env.server import TrafficControlEnvironment
except ImportError:
    from models import TaskId, TrafficControlAction, TrafficCommand
    from server import TrafficControlEnvironment


def run_episode_and_verify(task_id: TaskId, test_name: str) -> bool:
    """Run an episode and verify all scores strictly in (0, 1) including JSON."""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name} - {task_id.value.upper()}")
    print(f"{'='*70}")
    
    env = TrafficControlEnvironment(default_task_id=task_id)
    obs = env.reset(task_id=task_id.value)
    
    # Run episode with heuristic
    while not obs.done:
        if obs.emergency_present:
            if obs.emergency_direction.value in ("north", "south"):
                cmd = TrafficCommand.SET_NS_GREEN
            else:
                cmd = TrafficCommand.SET_EW_GREEN
        else:
            ns_q = obs.queue_north + obs.queue_south + obs.avg_wait_north + obs.avg_wait_south
            ew_q = obs.queue_east + obs.queue_west + obs.avg_wait_east + obs.avg_wait_west
            if ns_q >= ew_q:
                cmd = (TrafficCommand.HOLD_CURRENT_PHASE 
                       if obs.current_phase.value == "ns_green" 
                       else TrafficCommand.SET_NS_GREEN)
            else:
                cmd = (TrafficCommand.HOLD_CURRENT_PHASE 
                       if obs.current_phase.value == "ew_green" 
                       else TrafficCommand.SET_EW_GREEN)
        
        obs = env.step(TrafficControlAction(command=cmd))
    
    # Get scores
    final_score = env.state.final_score
    score_breakdown = env.state.score_breakdown
    
    print(f"\nFinal Score: {final_score}")
    print(f"Score Breakdown: {score_breakdown}")
    
    # Check final_score
    if final_score is None:
        print(f"✗ FAIL: final_score is None")
        return False
    
    if not (0.0 < final_score < 1.0):
        print(f"✗ FAIL: final_score = {final_score} is NOT in (0, 1)")
        return False
    else:
        print(f"✓ PASS: final_score = {final_score} is in (0, 1)")
    
    # Check all scores in breakdown
    print(f"\nChecking score_breakdown values:")
    all_valid = True
    for key, value in score_breakdown.items():
        if not isinstance(value, (int, float)):
            print(f"  ✗ {key} = {value!r} (NOT a number)")
            all_valid = False
        elif not (0.0 < value < 1.0):
            print(f"  ✗ {key} = {value} is out of range (0, 1)")
            all_valid = False
        else:
            print(f"  ✓ {key} = {value:.10f}")
    
    if not all_valid:
        print(f"✗ FAIL: Some scores out of range")
        return False
    
    # Test JSON serialization
    print(f"\nTesting JSON serialization:")
    try:
        scores_to_serialize = {
            "final_score": final_score,
            **score_breakdown
        }
        json_str = json.dumps(scores_to_serialize)
        print(f"  Serialized: {json_str}")
        
        # Deserialize and check
        deserialized = json.loads(json_str)
        print(f"  Deserialized: {deserialized}")
        
        all_valid_after_json = True
        for key, value in deserialized.items():
            if not (0.0 < value < 1.0):
                print(f"  ✗ After JSON: {key} = {value} is out of range")
                all_valid_after_json = False
        
        if all_valid_after_json:
            print(f"  ✓ All scores valid after JSON round-trip")
        else:
            print(f"  ✗ FAIL: Some scores invalid after JSON")
            return False
            
    except Exception as e:
        print(f"  ✗ JSON serialization error: {e}")
        return False
    
    # Test metadata from observation
    print(f"\nTesting observation metadata:")
    obs_after_done = env.state
    if obs_after_done.final_score != final_score:
        print(f"  ✗ State final_score mismatch: {obs_after_done.final_score} vs {final_score}")
        return False
    else:
        print(f"  ✓ State final_score matches: {obs_after_done.final_score}")
    
    if obs_after_done.score_breakdown != score_breakdown:
        print(f"  ✗ State score_breakdown mismatch")
        print(f"    Expected: {score_breakdown}")
        print(f"    Got:      {obs_after_done.score_breakdown}")
        return False
    else:
        print(f"  ✓ State score_breakdown matches")
    
    print(f"\n✓ ALL CHECKS PASSED FOR {test_name} - {task_id.value.upper()}")
    return True


def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE GRADING VERIFICATION TEST WITH JSON SERIALIZATION")
    print("="*70)
    
    results = []
    
    for task_id in [TaskId.EASY, TaskId.MEDIUM, TaskId.HARD]:
        result = run_episode_and_verify(task_id, "Heuristic Control")
        results.append((task_id.value, result))
    
    print(f"\n\n{'='*70}")
    print("FINAL RESULTS")
    print(f"{'='*70}")
    
    all_passed = True
    for task_id, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {task_id}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
