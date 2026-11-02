"""Composition root: the only place that knows every module and wires them together.

`build_app` takes ready-made services (so tests can pass fakes); `create_app` does the
production wiring from settings. Run with `uv run uvicorn fabpilot.main:create_app --factory`.
"""

from collections.abc import Sequence

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fabpilot import __version__
from fabpilot.core.db import DatabaseHealthCheck, make_engine
from fabpilot.core.errors import install_error_handlers
from fabpilot.core.health import HealthCheck
from fabpilot.core.logging import configure_logging
from fabpilot.core.settings import AppSettings, get_app_settings
from fabpilot.modules import fabdata, health, llm

API_V1 = "/api/v1"


def build_app(
    *,
    settings: AppSettings,
    health_checks: Sequence[HealthCheck],
    fab_service: fabdata.FabDataService,
) -> FastAPI:
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
    install_error_handlers(app)

    app.include_router(health.build_router(health.HealthService(health_checks)))
    v1 = APIRouter(prefix=API_V1)
    v1.include_router(fabdata.build_router(fab_service))
    app.include_router(v1)
    return app


def create_app() -> FastAPI:
    settings = get_app_settings()
    configure_logging(settings.log_level)

    fab = fabdata.build_fabdata_module(fabdata.FabDataSettings())
    app_db = make_engine(settings.app_db_url)
    checks: list[HealthCheck] = [
        *fab.health_checks,
        DatabaseHealthCheck("app_db", app_db),
        llm.LlmConfigCheck(llm.LlmSettings()),
    ]
    return build_app(settings=settings, health_checks=checks, fab_service=fab.service)
