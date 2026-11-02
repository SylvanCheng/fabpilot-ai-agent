"""SQLAlchemy engine factory and a generic database health check."""

import time

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError

from fabpilot.core.health import CheckResult


def make_engine(url: str, *, read_only: bool = False) -> Engine:
    engine = create_engine(url, pool_pre_ping=True)
    if read_only:
        # Defence in depth: the DB role should already be SELECT-only.
        @event.listens_for(engine, "connect")
        def _set_read_only(dbapi_conn, _record):  # pragma: no cover - needs a live DB
            with dbapi_conn.cursor() as cur:
                cur.execute("SET default_transaction_read_only = on")
            dbapi_conn.commit()

    return engine


class DatabaseHealthCheck:
    """`HealthCheck` implementation that runs `SELECT 1`."""

    def __init__(self, name: str, engine: Engine) -> None:
        self.name = name
        self._engine = engine

    def check(self) -> CheckResult:
        start = time.perf_counter()
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            return CheckResult(ok=False, error=type(exc).__name__)
        return CheckResult(ok=True, latency_ms=round((time.perf_counter() - start) * 1000, 1))
