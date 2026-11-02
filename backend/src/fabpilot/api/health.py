"""Health endpoints.

- `/health`        liveness: the process is up. Never touches dependencies.
- `/health/ready`  readiness: can we reach both databases? LLM settings are reported, not called,
                   because the GPU box may legitimately be switched off while developing.
"""

import time
from typing import Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from fabpilot import __version__
from fabpilot.config import get_settings
from fabpilot.db import app_engine, business_engine, ping

router = APIRouter(prefix="/health", tags=["health"])


class Liveness(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = __version__


class CheckResult(BaseModel):
    ok: bool
    latency_ms: float | None = None
    error: str | None = None


class LlmInfo(BaseModel):
    provider: str
    base_url: str
    model: str


class Readiness(BaseModel):
    status: Literal["ok", "degraded"]
    version: str = __version__
    checks: dict[str, CheckResult]
    llm: LlmInfo


def _check(fn) -> CheckResult:
    start = time.perf_counter()
    try:
        fn()
    except SQLAlchemyError as exc:
        return CheckResult(ok=False, error=type(exc).__name__)
    return CheckResult(ok=True, latency_ms=round((time.perf_counter() - start) * 1000, 1))


@router.get("", response_model=Liveness)
def liveness() -> Liveness:
    return Liveness()


@router.get("/ready", response_model=Readiness)
def readiness(response: Response) -> Readiness:
    settings = get_settings()
    checks = {
        "business_db": _check(lambda: ping(business_engine())),
        "app_db": _check(lambda: ping(app_engine())),
    }
    all_ok = all(c.ok for c in checks.values())
    if not all_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return Readiness(
        status="ok" if all_ok else "degraded",
        checks=checks,
        llm=LlmInfo(
            provider=settings.llm_provider, base_url=settings.llm_base_url, model=settings.llm_model
        ),
    )
