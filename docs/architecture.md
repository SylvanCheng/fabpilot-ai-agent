# Architecture

FabPilot is a **modular monolith**: one deployable backend, split into modules with hard,
machine-checked boundaries. It gives most of the decoupling benefits of microservices without
their operational cost, and any module can be extracted later because it already talks to the
rest only through interfaces. See [ADR-0002](adr/0002-modular-monolith.md).

## System view

```
Blazor Web App ──HTTP /api/v1 (contract: contracts/openapi.json)──► FastAPI backend
 (UI only;                                                          │
  depends on IFabPilotApi)                                          ├─► fab_business (read-only)
                                                                    ├─► fabpilot_app (+pgvector)
                                                                    └─► LLM (OpenAI-compatible)
```

The frontend never touches a database or the LLM. The backend is the only owner of business
logic, so a second client (CLI, Teams bot, evaluation harness) reuses it unchanged.

## Backend layers

```
fabpilot/
  devtools/   data generator, dataset downloader, contract export      (outermost)
  main.py     composition root: builds adapters, wires modules, mounts routers
  modules/    vertical slices: health, fabdata, llm, (chat, tools, rag, ... later)
  core/       shared kernel: settings base, errors, logging, DB factory, HealthCheck port
```

Dependencies point **inwards only**: `devtools → main → modules → core`. Enforced by
[import-linter](https://import-linter.readthedocs.io) contracts in `backend/pyproject.toml`
and run in CI (`uv run lint-imports`):

| Contract | Why it matters |
|---|---|
| Layers `devtools → main → modules → core` | `core` stays generic; nothing depends on dev tooling. |
| Modules are independent | Changing `fabdata` can never break `llm`. Cross-module collaboration goes through the composition root, by passing interfaces. |
| `service` / `ports` don't import FastAPI, SQLAlchemy, psycopg, httpx | Business logic is testable with plain fakes and survives framework changes. |
| `api` doesn't import adapters or DB drivers | HTTP layer only translates HTTP ↔ use cases. |

## Inside a module

```
modules/fabdata/
  __init__.py      public API: the only import path other code may use
  ports.py         domain types + Protocols the service needs (FabDataRepository)
  service.py       use cases; depends on ports only
  adapters/        Postgres implementation of the ports; translates driver errors to AppError
  api.py           router + response models (the public HTTP contract)
  settings.py      the module's own env settings
  module.py        build_*_module(): picks concrete adapters, returns service + health checks
```

This is ports-and-adapters (hexagonal) at module scale. The rule of thumb:
**the service says *what* it needs (port), the adapter says *how* (SQL, HTTP).**

## Cross-cutting conventions

| Topic | Convention |
|---|---|
| API versioning | Product endpoints under `/api/v1`. Breaking change → `/api/v2` side by side. Ops endpoints (`/health`) unversioned. |
| Errors | Domain code raises `AppError` subclasses; one handler renders RFC 9457 `application/problem+json`. Internals never leak. |
| Contract | `contracts/openapi.json` is generated from code, committed, and checked in CI (backend test + frontend DTO test). |
| Config | Env vars only, typed with pydantic-settings, one settings class per module. |
| Health | Modules contribute `HealthCheck` objects; the health module just aggregates them. |
| Data access | Business DB through a SELECT-only role and read-only sessions ([ADR-0003](adr/0003-separate-read-only-business-db.md)). |

## Testing strategy

| Level | Where | Uses | Speed |
|---|---|---|---|
| Unit | `backend/tests/unit` | fakes for ports (`tests/fakes.py`), `build_app` with fakes | ms |
| Contract | `backend/tests/contract`, `frontend/FabPilot.Web.Tests/ContractTests.cs` | `contracts/openapi.json` | ms |
| Integration | `backend/tests/integration` (`@pytest.mark.db`) | real PostgreSQL from `db/init` | s |
| Architecture | `lint-imports` | import graph | s |
| Evals (P6) | `evals/` | injected scenarios as ground truth | min |

## Adding a module (checklist)

1. `modules/<name>/` with the files above; export the public API in `__init__.py`.
2. Add it to the *independence* contract in `pyproject.toml`.
3. Wire it in `main.py` (`create_app` for production, `build_app` parameter for tests).
4. Unit tests with fakes; integration tests if it has an adapter.
5. `uv run fabpilot-export-openapi` if it adds endpoints; commit the contract diff.
6. ADR if it introduces a significant technology or pattern.
