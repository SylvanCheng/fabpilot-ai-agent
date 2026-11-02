from fabpilot.core.errors import DependencyUnavailableError
from fabpilot.modules.fabdata import FabDataService

from ...conftest import make_client
from ...fakes import InMemoryFabDataRepository


def test_service_returns_repository_overview():
    overview = FabDataService(InMemoryFabDataRepository()).overview()
    assert overview.lot_count == 4


def test_overview_endpoint_contract():
    resp = make_client().get("/api/v1/fab/overview")
    assert resp.status_code == 200
    body = resp.json()
    assert body["lot_count"] == 4
    assert body["lots_by_status"] == {"FINISHED": 3, "WIP": 1}
    assert body["first_lot_start"].startswith("2026-09-01")


class _DownRepository:
    def overview(self):
        raise DependencyUnavailableError("business database unreachable")


def test_domain_error_rendered_as_problem_json():
    resp = make_client(repo=_DownRepository()).get("/api/v1/fab/overview")
    assert resp.status_code == 503
    assert resp.headers["content-type"] == "application/problem+json"
    assert resp.json()["code"] == "dependency_unavailable"


class _BuggyRepository:
    def overview(self):
        raise RuntimeError("SELECT secret FROM internals")


def test_unexpected_error_does_not_leak_details():
    resp = make_client(repo=_BuggyRepository()).get("/api/v1/fab/overview")
    assert resp.status_code == 500
    assert "secret" not in resp.text
