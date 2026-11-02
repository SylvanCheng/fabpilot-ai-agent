"""Test doubles for ports. Shared by unit and API tests."""

from datetime import UTC, datetime

from fabpilot.core.health import CheckResult
from fabpilot.modules.fabdata import FabOverview


class StaticCheck:
    def __init__(self, name: str, ok: bool = True) -> None:
        self.name = name
        self._ok = ok

    def check(self) -> CheckResult:
        return CheckResult(
            ok=self._ok,
            latency_ms=1.0 if self._ok else None,
            error=None if self._ok else "OperationalError",
        )


class InMemoryFabDataRepository:
    def __init__(self, overview: FabOverview | None = None) -> None:
        self._overview = overview or FabOverview(
            lots_by_status={"FINISHED": 3, "WIP": 1},
            wafer_count=100,
            equipment_count=27,
            first_lot_start=datetime(2026, 9, 1, tzinfo=UTC),
            last_lot_start=datetime(2026, 10, 30, tzinfo=UTC),
        )

    def overview(self) -> FabOverview:
        return self._overview
