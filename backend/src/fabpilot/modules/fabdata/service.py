from fabpilot.modules.fabdata.ports import FabDataRepository, FabOverview


class FabDataService:
    """Use cases over fab data. Grows with P3 (lot history, SPC, commonality, ...)."""

    def __init__(self, repo: FabDataRepository) -> None:
        self._repo = repo

    def overview(self) -> FabOverview:
        return self._repo.overview()
