from fabpilot.config import Settings


def test_llm_backend_switch_via_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "vllm")
    monkeypatch.setenv("LLM_BASE_URL", "http://gpu-box:8000/v1")
    monkeypatch.setenv("LLM_MODEL", "Qwen/Qwen2.5-14B-Instruct")
    s = Settings(_env_file=None)
    assert s.llm_provider == "vllm"
    assert s.llm_base_url == "http://gpu-box:8000/v1"
    assert s.llm_model == "Qwen/Qwen2.5-14B-Instruct"


def test_cors_origin_list(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a, http://b,")
    assert Settings(_env_file=None).cors_origin_list == ["http://a", "http://b"]
