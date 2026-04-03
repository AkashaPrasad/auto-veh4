# Deployment Guide

This project is ready for local validation and Docker-based Hugging Face Space deployment.

## 1. Set your Hugging Face token

Do not hard-code tokens in the repository.

```bash
export HF_TOKEN=your_real_hugging_face_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=openai/gpt-4.1-mini
```

For local heuristic-only testing, you can use:

```bash
export HF_TOKEN=dummy
```

## 2. Validate locally

```bash
cd /Users/saichaitu/Desktop/Traffic_Control/traffic_control_env
source .venv/bin/activate
./.venv/bin/openenv --help
openenv validate
HF_TOKEN=dummy python inference.py
docker build -t traffic-control-env:latest .
docker run --rm -p 8000:8000 traffic-control-env:latest
```

## 3. Deploy to Hugging Face Spaces

Run:

```bash
cd /Users/saichaitu/Desktop/Traffic_Control/traffic_control_env
source .venv/bin/activate
./.venv/bin/openenv --help
openenv push
```

Follow the prompts to create or update your Hugging Face Space.

## 4. Test after the Space is live

Verify:
- `/health` returns `200`
- `/web` loads
- `POST /reset` works
- one or two manual `step()` calls work
- Space is in the `Running` state

Typical live URLs:

```text
https://<your-username>-<your-space-name>.hf.space/health
https://<your-username>-<your-space-name>.hf.space/web
https://<your-username>-<your-space-name>.hf.space/reset
https://<your-username>-<your-space-name>.hf.space/state
```

## 5. Verify before final submission

Check all of these:
- latest code is pushed to GitHub
- Hugging Face Space is built and running
- the live Space responds correctly
- `inference.py` is still in the repo root
- `README.md`, `openenv.yaml`, and `Dockerfile` are present
- Hugging Face Space Secrets contain `HF_TOKEN`
- Hugging Face Space Variables contain `API_BASE_URL` and `MODEL_NAME`
- the team leader is ready to submit the final Space URL
