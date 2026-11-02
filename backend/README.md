# FabPilot backend

Python 3.12 + FastAPI. See the [root README](../README.md) for the quickstart.

```bash
uv sync                                  # install deps into .venv
uv run uvicorn fabpilot.main:create_app --factory --reload   # http://localhost:8000/docs
uv run ruff check . && uv run ruff format --check .
uv run pytest
```
