"""Domain types and the repository port. Pure Python: no SQLAlchemy, no FastAPI."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class FabOverview:
    lots_by_status: dict[str, int]
    wafer_count: int
    equipment_count: int
    first_lot_start: datetime | None
    last_lot_start: datetime | None

    @property
    def lot_count(self) -> int:
        return sum(self.lots_by_status.values())


class FabDataRepository(Protocol):
    def overview(self) -> FabOverview: ...
