"""Debug script to check all score values exported."""
try:
    from traffic_control_env.models import TaskId
    from traffic_control_env.server import TrafficControlEnvironment
    from traffic_control_env.models import TrafficControlAction, TrafficCommand
except ImportError:
    from models import TaskId
    from server import TrafficControlEnvironment
    from models import TrafficControlAction, TrafficCommand

import json

# Test what data might be returned to HF validator
env = TrafficControlEnvironment(default_task_id=TaskId.EASY)
obs = env.reset(task_id=TaskId.EASY.value)

while not obs.done:
    obs = env.step(TrafficControlAction(command=TrafficCommand.HOLD_CURRENT_PHASE))

# Get the state at the end
state = env.state
obs_metadata = env._build_observation(reward=0.5, done=True, status_message='test')

print('='*70)
print('State object attributes:')
print('='*70)
print(f'final_score: {state.final_score}')
print(f'score_breakdown: {state.score_breakdown}')

print()
print('='*70)
print('Observation metadata:')
print('='*70)
print(f'metadata final_score: {obs_metadata.metadata.get("final_score")}')
print(f'metadata score_breakdown: {obs_metadata.metadata.get("score_breakdown")}')

print()
print('='*70)
print('Checking all values for range (0, 1):')
print('='*70)

all_scores = {
    'final_score': state.final_score,
    **state.score_breakdown
}

print(f'Total scores to check: {len(all_scores)}')
print()

any_invalid = False
for key, value in all_scores.items():
    valid = 0.0 < value < 1.0
    status = '✓' if valid else '✗'
    print(f'{status} {key:25s} = {value:.10f} (valid: {valid})')
    if not valid:
        any_invalid = True

print()
if any_invalid:
    print('✗ SOME SCORES ARE OUT OF RANGE')
else:
    print('✓ ALL SCORES ARE STRICTLY IN (0, 1)')
