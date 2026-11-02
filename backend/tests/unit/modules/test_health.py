import pytest

from fabpilot import __version__
from fabpilot.modules.health import HealthService

from ...conftest import make_client
from ...fakes import StaticCheck


def test_liveness():
    resp = make_client().get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "version": __version__}


def test_readiness_ok_aggregates_all_checks():
    resp = make_client(checks=[StaticCheck("a"), StaticCheck("b")]).get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert set(body["checks"]) == {"a", "b"}


def test_readiness_degraded_returns_503():
    resp = make_client(checks=[StaticCheck("a"), StaticCheck("b", ok=False)]).get("/health/ready")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["b"]["error"] == "OperationalError"


def test_duplicate_check_names_rejected():
    with pytest.raises(ValueError):
        HealthService([StaticCheck("x"), StaticCheck("x")])
