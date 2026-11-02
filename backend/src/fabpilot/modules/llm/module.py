from fabpilot.core.health import CheckResult
from fabpilot.modules.llm.settings import LlmSettings


class LlmConfigCheck:
    """Reports the configured endpoint without calling it: the GPU box may be off during dev."""

    name = "llm"

    def __init__(self, settings: LlmSettings) -> None:
        self._settings = settings

    def check(self) -> CheckResult:
        s = self._settings
        return CheckResult(
            ok=True,
            detail={
                "provider": s.provider,
                "base_url": s.base_url,
                "model": s.model,
                "probed": False,
            },
        )
