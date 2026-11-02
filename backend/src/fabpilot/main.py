"""FastAPI entrypoint: `uv run uvicorn fabpilot.main:app --reload`."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fabpilot import __version__
from fabpilot.api import health
from fabpilot.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    app = FastAPI(
        title="FabPilot API",
        version=__version__,
        description="Self-hosted LLM agent for industrial process & quality data.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    return app


app = create_app()
