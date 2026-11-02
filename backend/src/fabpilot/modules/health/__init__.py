"""Health module: liveness and readiness endpoints, aggregated from registered checks."""

from fabpilot.modules.health.api import build_router
from fabpilot.modules.health.service import HealthService

__all__ = ["HealthService", "build_router"]
