"""Wiring for the fabdata module: the only place that picks concrete adapters."""

from dataclasses import dataclass

from fabpilot.core.db import DatabaseHealthCheck, make_engine
from fabpilot.core.health import HealthCheck
from fabpilot.modules.fabdata.adapters.postgres import PostgresFabDataRepository
from fabpilot.modules.fabdata.service import FabDataService
from fabpilot.modules.fabdata.settings import FabDataSettings


@dataclass(frozen=True)
class FabDataModule:
    service: FabDataService
    health_checks: list[HealthCheck]


def build_fabdata_module(settings: FabDataSettings) -> FabDataModule:
    engine = make_engine(settings.business_db_url, read_only=True)
    return FabDataModule(
        service=FabDataService(PostgresFabDataRepository(engine)),
        health_checks=[DatabaseHealthCheck("business_db", engine)],
    )
