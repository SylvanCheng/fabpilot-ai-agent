from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from fabpilot import __version__
from fabpilot.api import health
from fabpilot.main import app

client = TestClient(app)


def test_liveness():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "version": __version__}


def test_readiness_ok(monkeypatch):
    monkeypatch.setattr(health, "ping", lambda _engine: None)
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert set(body["checks"]) == {"business_db", "app_db"}
    assert {"provider", "base_url", "model"} <= set(body["llm"])


def test_readiness_degraded_when_db_down(monkeypatch):
    def boom(_engine):
        raise OperationalError("SELECT 1", {}, Exception("down"))

    monkeypatch.setattr(health, "ping", boom)
    resp = client.get("/health/ready")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["business_db"] == {
        "ok": False,
        "latency_ms": None,
        "error": "OperationalError",
    }
