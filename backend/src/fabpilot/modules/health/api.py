"""Health endpoints (unversioned: an operational convention, not part of the product API).

- `GET /health`        liveness: the process is up. Never touches dependencies.
- `GET /health/ready`  readiness: aggregated module checks; 503 if any check fails.
"""

from typing import Any, Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from fabpilot import __version__
from fabpilot.modules.health.service import HealthService


class LivenessOut(BaseModel):
    status: Literal["ok"] = "ok"
    version: str = __version__


class CheckOut(BaseModel):
    ok: bool
    latency_ms: float | None = None
    error: str | None = None
    detail: dict[str, Any] = {}


class ReadinessOut(BaseModel):
    status: Literal["ok", "degraded"]
    version: str = __version__
    checks: dict[str, CheckOut]


def build_router(service: HealthService) -> APIRouter:
    router = APIRouter(prefix="/health", tags=["health"])

    @router.get("", response_model=LivenessOut)
    def liveness() -> LivenessOut:
        return LivenessOut()

    @router.get(
        "/ready",
        response_model=ReadinessOut,
        responses={503: {"model": ReadinessOut, "description": "One or more checks failed"}},
    )
    def readiness(response: Response) -> ReadinessOut:
        report = service.readiness()
        if not report.ok:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessOut(
            status="ok" if report.ok else "degraded",
            checks={
                name: CheckOut(
                    ok=r.ok, latency_ms=r.latency_ms, error=r.error, detail=dict(r.detail)
                )
                for name, r in report.checks.items()
            },
        )

    return router
