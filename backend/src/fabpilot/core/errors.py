"""Error model.

Modules raise `AppError` subclasses with domain meaning; adapters translate infrastructure
exceptions (e.g. SQLAlchemy) into them. The API layer renders every error the same way:
RFC 9457 `application/problem+json`, so clients handle one shape.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status: int = 500
    code: str = "internal_error"
    title: str = "Internal error"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.title)
        self.detail = detail


class NotFoundError(AppError):
    status, code, title = 404, "not_found", "Resource not found"


class DependencyUnavailableError(AppError):
    status, code, title = 503, "dependency_unavailable", "A dependency is unavailable"


def _problem(status: int, code: str, title: str, detail: str | None) -> JSONResponse:
    body = {"type": f"urn:fabpilot:error:{code}", "title": title, "status": status, "code": code}
    if detail:
        body["detail"] = detail
    return JSONResponse(body, status_code=status, media_type="application/problem+json")


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_req: Request, exc: AppError) -> JSONResponse:
        return _problem(exc.status, exc.code, exc.title, exc.detail)

    @app.exception_handler(Exception)
    async def _unhandled(_req: Request, _exc: Exception) -> JSONResponse:
        # Never leak internals (stack traces, SQL) to clients; details go to the log.
        return _problem(500, "internal_error", "Internal error", None)
