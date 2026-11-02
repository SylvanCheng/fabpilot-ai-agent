"""PostgreSQL implementation of `FabDataRepository`."""

from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError

from fabpilot.core.errors import DependencyUnavailableError
from fabpilot.modules.fabdata.ports import FabOverview


class PostgresFabDataRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def overview(self) -> FabOverview:
        try:
            with self._engine.connect() as conn:
                by_status = dict(
                    conn.execute(text("SELECT status, count(*) FROM fab.lot GROUP BY status")).all()
                )
                wafers = conn.execute(text("SELECT count(*) FROM fab.wafer")).scalar_one()
                tools = conn.execute(text("SELECT count(*) FROM fab.equipment")).scalar_one()
                first, last = conn.execute(
                    text("SELECT min(start_time), max(start_time) FROM fab.lot")
                ).one()
        except OperationalError as exc:
            # Translate infrastructure errors into the domain error model.
            raise DependencyUnavailableError("business database unreachable") from exc
        return FabOverview(
            lots_by_status={str(k): int(v) for k, v in by_status.items()},
            wafer_count=int(wafers),
            equipment_count=int(tools),
            first_lot_start=first,
            last_lot_start=last,
        )
