import os

import psycopg
import pytest

READER_DSN = os.environ.get(
    "TEST_READER_DSN", "postgresql://fab_reader:fab_reader@localhost:5432/fab_business"
)
LOADER_DSN = os.environ.get(
    "TEST_LOADER_DSN", "postgresql://fab_loader:fab_loader@localhost:5432/fab_business"
)


def _db_available() -> bool:
    try:
        with psycopg.connect(LOADER_DSN, connect_timeout=2):
            return True
    except psycopg.OperationalError:
        return False


def pytest_collection_modifyitems(config, items):
    if _db_available():
        return
    skip = pytest.mark.skip(reason="PostgreSQL with FabPilot schema not reachable")
    for item in items:
        if "db" in item.keywords:
            item.add_marker(skip)
