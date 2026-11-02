"""Business modules. Each module is a vertical slice with the same internal shape:

    __init__.py   public API of the module (the only thing other code may import)
    api.py        FastAPI router + request/response schemas (HTTP adapter)
    service.py    use cases; depends only on ports, never on frameworks or drivers
    ports.py      Protocols + domain types the service needs
    adapters/     implementations of the ports (Postgres, HTTP, ...)
    settings.py   the module's own configuration

Modules never import each other; the composition root (`fabpilot.main`) wires them together.
Enforced by import-linter (see `[tool.importlinter]` in pyproject.toml).
"""
