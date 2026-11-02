import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from fabpilot.core.settings import AppSettings
from fabpilot.main import build_app
from fabpilot.modules.fabdata import FabDataService

from .fakes import InMemoryFabDataRepository, StaticCheck

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


def make_client(*, checks=None, repo=None) -> TestClient:
    """App wired with fakes: no DB, no network."""
    app = build_app(
        settings=AppSettings(_env_file=None),
        health_checks=checks if checks is not None else [StaticCheck("business_db")],
        fab_service=FabDataService(repo or InMemoryFabDataRepository()),
    )
    return TestClient(app, raise_server_exceptions=False)
