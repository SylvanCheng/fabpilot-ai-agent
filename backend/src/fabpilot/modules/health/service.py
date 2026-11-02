from collections.abc import Sequence
from dataclasses import dataclass

from fabpilot.core.health import CheckResult, HealthCheck


@dataclass(frozen=True)
class ReadinessReport:
    ok: bool
    checks: dict[str, CheckResult]


class HealthService:
    def __init__(self, checks: Sequence[HealthCheck]) -> None:
        names = [c.name for c in checks]
        if len(names) != len(set(names)):
            raise ValueError(f"duplicate health check names: {names}")
        self._checks = list(checks)

    def readiness(self) -> ReadinessReport:
        results = {c.name: c.check() for c in self._checks}
        return ReadinessReport(ok=all(r.ok for r in results.values()), checks=results)
