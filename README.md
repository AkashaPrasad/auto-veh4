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

These are defined in [`TrafficControlAction`](/Users/saichaitu/Desktop/Traffic_Control/traffic_control_env/models.py).

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
- emergency vehicle appears later

Task definitions live in [task_bank.py](/Users/saichaitu/Desktop/Traffic_Control/traffic_control_env/task_bank.py).

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
cd /Users/saichaitu/Desktop/Traffic_Control/traffic_control_env
uv run server --host 0.0.0.0 --port 8000
```

If the web interface is available, open:

`http://localhost:8000/web`

Run the baseline script:

```bash
cd /Users/saichaitu/Desktop/Traffic_Control/traffic_control_env
python inference.py
```

## LLM Baseline Variables

`inference.py` supports OpenAI-compatible model calls when these variables are set:
- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`

Without those variables, it falls back to a deterministic heuristic baseline.

## Docker

Build locally:

```bash
cd /Users/saichaitu/Desktop/Traffic_Control/traffic_control_env
docker build -t traffic-control-env:latest -f server/Dockerfile .
docker run -p 8000:8000 traffic-control-env:latest
```

If `docker --version` works but `docker build` fails with `docker.sock: no such file or directory`,
that means the Docker CLI is installed but the Docker daemon is not running yet.
On macOS, start Docker Desktop or another Docker runtime before retrying.

## Why This Design

This project stays intentionally lightweight:
- fixed deterministic scenarios
- no external traffic simulator
- no custom frontend
- easy local debugging
- easy grading

That makes it well suited for hackathon validation and iterative improvement.
