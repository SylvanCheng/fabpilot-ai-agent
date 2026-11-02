"""Health-check contract shared by all modules.

The health module only knows this Protocol. Each module contributes its own checks, and the
composition root (`fabpilot.main`) registers them, so adding a module never touches health code.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    latency_ms: float | None = None
    error: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


class HealthCheck(Protocol):
    name: str

    def check(self) -> CheckResult: ...
