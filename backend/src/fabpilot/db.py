"""Database engines. One engine per database; the business engine is read-only by design."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine, event, text

from fabpilot.config import get_settings


@lru_cache
def business_engine() -> Engine:
    engine = create_engine(get_settings().business_db_url, pool_pre_ping=True)

    # Defence in depth: the DB role only has SELECT, and every session is read-only too.
    @event.listens_for(engine, "connect")
    def _set_read_only(dbapi_conn, _record):  # pragma: no cover - needs a live DB
        with dbapi_conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only = on")
        dbapi_conn.commit()

    return engine


@lru_cache
def app_engine() -> Engine:
    return create_engine(get_settings().app_db_url, pool_pre_ping=True)


def ping(engine: Engine) -> None:
    """Raise if the database is unreachable."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
