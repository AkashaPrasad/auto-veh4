"""FastAPI application entrypoint for the traffic-control environment."""

import os

try:
    from openenv.core.env_server import create_app
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "openenv-core is required to run the traffic-control environment server."
    ) from exc

try:
    from ..models import TrafficControlAction, TrafficControlObservation
    from .traffic_control_environment import TrafficControlEnvironment
except ImportError:
    from models import TrafficControlAction, TrafficControlObservation
    from server.traffic_control_environment import TrafficControlEnvironment

# Make the local debugging UI available by default during development.
os.environ.setdefault("ENABLE_WEB_INTERFACE", "true")


app = create_app(
    TrafficControlEnvironment,
    TrafficControlAction,
    TrafficControlObservation,
    env_name="traffic_control_env",
    max_concurrent_envs=1,
)


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(host=args.host, port=args.port)
