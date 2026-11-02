"""HTTP adapter for fabdata.

Response models are the public contract, exported to contracts/openapi.json.
"""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from fabpilot.modules.fabdata.service import FabDataService


class FabOverviewOut(BaseModel):
    lot_count: int
    lots_by_status: dict[str, int]
    wafer_count: int
    equipment_count: int
    first_lot_start: datetime | None
    last_lot_start: datetime | None


def build_router(service: FabDataService) -> APIRouter:
    router = APIRouter(prefix="/fab", tags=["fab data"])

    @router.get("/overview", response_model=FabOverviewOut, summary="Size of the fab dataset")
    def overview() -> FabOverviewOut:
        o = service.overview()
        return FabOverviewOut(
            lot_count=o.lot_count,
            lots_by_status=o.lots_by_status,
            wafer_count=o.wafer_count,
            equipment_count=o.equipment_count,
            first_lot_start=o.first_lot_start,
            last_lot_start=o.last_lot_start,
        )

    return router
