---
title: Autonomous Traffic Control Environment
emoji: 🚦
colorFrom: yellow
colorTo: green
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - reinforcement-learning
  - traffic-control
---

# Autonomous Traffic Control Environment

A lightweight OpenEnv environment where an agent controls a single 4-way intersection and learns to balance traffic flow with emergency vehicle prioritization.

## What This Environment Simulates

The agent manages one intersection with four incoming directions:
- North
- South
- East
- West

The environment tracks:
- vehicle queues
- signal phase
- waiting time
- throughput
- emergency vehicles

The goal is to:
- reduce queue length
- reduce average waiting time
- increase throughput
- prioritize emergency vehicles

## OpenEnv Interface

This environment follows the standard OpenEnv pattern:
- `reset()` starts a new traffic scenario
- `step(action)` applies one traffic-light command
- `state()` returns full episode state

## Action Space

Allowed commands:
- `set_ns_green`
- `set_ew_green`
- `hold_current_phase`
- `set_all_red`

These are defined in `models.py`.

## Observation Space

Each observation contains:
- current phase
- current timestep
- steps remaining
- time since last phase change
- queue lengths for all four directions
- average waiting times for all four directions
- emergency presence and direction
- total vehicles passed
- status message

## Task Set

The environment includes three deterministic tasks:

### Easy: Normal Traffic Flow
- balanced traffic
- no emergency vehicles

### Medium: Emergency Priority
- moderate traffic
- one emergency vehicle appears mid-episode

### Hard: Heavy Congestion With Late Emergency
- heavy congestion first
- multiple emergency vehicles appear after congestion has already formed

Task definitions live in `task_bank.py`.

## Reward Design

Per-step reward combines:
- positive reward for vehicles passing
- penalty for queue size
- penalty for average waiting time
- strong penalty for emergency delay
- penalty for switching phases too often
- penalty for invalid actions

This gives dense reward signals instead of only a final pass/fail score.

## Deterministic Grading

At episode end, the environment computes a score in `[0.0, 1.0]`.

The score uses weighted components such as:
- throughput
- average wait quality
- emergency handling
- fairness across directions
- stability of control

Weights vary slightly by difficulty level.

## Project Structure

```text
traffic_control_env/
├── __init__.py
├── client.py
├── inference.py
├── models.py
├── openenv.yaml
├── pyproject.toml
├── README.md
├── task_bank.py
├── outputs/
│   ├── evals/
│   └── logs/
└── server/
    ├── __init__.py
    ├── app.py
    ├── Dockerfile
    └── traffic_control_environment.py
```

## Local Setup

Use Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
```

## Run Locally

Start the OpenEnv server:

```bash
cd traffic_control_env
python -m server.app --host 0.0.0.0 --port 8000
```

If the web interface is available, open:

`http://localhost:8000/web`

To list the available tasks for quick local testing:

```bash
curl http://localhost:8000/tasks
```

Run the baseline script:

```bash
cd traffic_control_env
HF_TOKEN=dummy python inference.py
```

To run just one task instead of all three:

```bash
HF_TOKEN=dummy TASK_ID=hard python inference.py
```

## LLM Baseline Variables

`inference.py` always expects `HF_TOKEN` to exist because that is part of the
hackathon contract.

For local heuristic-only testing, you can safely use:

```bash
HF_TOKEN=dummy python inference.py
```

For real LLM-backed inference, set:
- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`

The script uses the OpenAI client with the Hugging Face router. If `HF_TOKEN`
is set to `dummy`, `test`, or `local`, it skips network model calls and falls
back to the built-in deterministic heuristic baseline.

## Baseline Scores

Current deterministic heuristic baseline after the latest hard-task tightening:
- easy: `0.950`
- medium: `0.936`
- hard: `0.676`

This is intentionally no longer a near-perfect hard-task result, which makes the
benchmark more credible for evaluation.

## Docker

Build locally:

```bash
cd traffic_control_env
docker build -t traffic-control-env:latest .
docker run -p 8000:8000 traffic-control-env:latest
```

If `docker --version` works but `docker build` fails with `docker.sock: no such file or directory`,
that means the Docker CLI is installed but the Docker daemon is not running yet.
On macOS, start Docker Desktop or another Docker runtime before retrying.

## Deployment

For Hugging Face Spaces:
- the repo front-matter is already configured for `sdk: docker`
- the repo now includes a root `Dockerfile`, which Docker Spaces expects
- secrets should be set in the Space settings, not in code

Basic deployment flow:

```bash
cd traffic_control_env
source .venv/bin/activate
./.venv/bin/openenv --help
export HF_TOKEN=your_real_hugging_face_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=openai/gpt-4.1-mini
openenv push
```

After the Space is live, test:
- `/health`
- `/web`
- `POST /reset`
- reset
- one or two manual steps

See `DEPLOYMENT.md` for the short manual checklist.

## Live Space URL

Add your final deployed Space URL here before submission:

`https://huggingface.co/spaces/<your-username>/<your-space-name>`

Space app base URL:

`https://<your-username>-<your-space-name>.hf.space`

## Local Smoke-Test Checklist

- `openenv validate` passes
- `HF_TOKEN=dummy python inference.py` runs all tasks
- `HF_TOKEN=dummy TASK_ID=hard python inference.py` runs the hard task only
- `python -m server.app --host 0.0.0.0 --port 8000` starts the local server
- `curl http://localhost:8000/health` returns `200`
- `curl http://localhost:8000/tasks` returns the task list
- `docker build -t traffic-control-env:latest .` succeeds
- `docker run -p 8000:8000 traffic-control-env:latest` boots cleanly

## Hosted Smoke-Test Checklist

- Hugging Face Space status is `Running`
- live `/health` returns `200`
- live `/web` loads correctly
- live `POST /reset` returns a valid response
- live `reset()` works
- one or two live `step()` calls work
- no secrets are hard-coded in the repo
- the submitted Space URL matches the deployed environment

## Why This Design

This project stays intentionally lightweight:
- fixed deterministic scenarios
- no external traffic simulator
- no custom frontend
- easy local debugging
- easy grading

That makes it well suited for hackathon validation and iterative improvement.
