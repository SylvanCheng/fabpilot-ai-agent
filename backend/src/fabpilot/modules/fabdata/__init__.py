"""Fab data module: read-only access to the synthetic fab business database.

Later phases (agent tools) call `FabDataService`; they never touch SQL or the engine directly.
"""

from fabpilot.modules.fabdata.api import build_router
from fabpilot.modules.fabdata.module import FabDataModule, build_fabdata_module
from fabpilot.modules.fabdata.ports import FabDataRepository, FabOverview
from fabpilot.modules.fabdata.service import FabDataService
from fabpilot.modules.fabdata.settings import FabDataSettings

__all__ = [
    "FabDataModule",
    "FabDataRepository",
    "FabDataService",
    "FabDataSettings",
    "FabOverview",
    "build_fabdata_module",
    "build_router",
]
