from fabpilot.core.settings import AppSettings


def test_cors_origin_list(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a, http://b,")
    assert AppSettings(_env_file=None).cors_origin_list == ["http://a", "http://b"]
