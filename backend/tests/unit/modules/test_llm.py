from fabpilot.modules.llm import LlmConfigCheck, LlmSettings


def test_backend_switch_is_env_only(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "vllm")
    monkeypatch.setenv("LLM_BASE_URL", "http://gpu-box:8000/v1")
    monkeypatch.setenv("LLM_MODEL", "Qwen/Qwen3-8B")
    s = LlmSettings(_env_file=None)
    assert (s.provider, s.base_url, s.model) == ("vllm", "http://gpu-box:8000/v1", "Qwen/Qwen3-8B")


def test_config_check_reports_without_probing():
    result = LlmConfigCheck(LlmSettings(_env_file=None)).check()
    assert result.ok
    assert result.detail["probed"] is False
    assert "api_key" not in result.detail
