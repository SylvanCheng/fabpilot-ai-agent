"""Runs only when a PostgreSQL initialised by db/init is reachable (CI provides one)."""

import psycopg
import pytest

from fabpilot.core.db import make_engine
from fabpilot.devtools.datagen.generator import GeneratorConfig, generate
from fabpilot.devtools.datagen.writers import write_postgres
from fabpilot.modules.fabdata.adapters.postgres import PostgresFabDataRepository

from ..conftest import LOADER_DSN, READER_DSN

pytestmark = pytest.mark.db


@pytest.fixture(scope="module")
def loaded():
    rows = generate(GeneratorConfig(lots_per_product=10))
    write_postgres(rows, LOADER_DSN)
    return rows


def test_reader_sees_loaded_data(loaded):
    with psycopg.connect(READER_DSN) as conn:
        n = conn.execute("SELECT count(*) FROM fab.lot").fetchone()[0]
    assert n == len(loaded["lot"])


def test_reader_cannot_write(loaded):
    with psycopg.connect(READER_DSN) as conn, pytest.raises(psycopg.errors.Error):
        conn.execute("DELETE FROM fab.lot")


def test_postgres_repository_overview(loaded):
    url = READER_DSN.replace("postgresql://", "postgresql+psycopg://")
    overview = PostgresFabDataRepository(make_engine(url, read_only=True)).overview()
    assert overview.lot_count == len(loaded["lot"])
    assert overview.wafer_count == len(loaded["wafer"])
