# Changelog

All notable changes are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [SemVer](https://semver.org/).

## [Unreleased]

### Added
- P0 foundation: modular-monolith FastAPI backend (`core`, `modules/{health,fabdata,llm}`,
  `devtools`) with import-linter boundary rules.
- `/health`, `/health/ready`, `GET /api/v1/fab/overview`; RFC 9457 problem+json errors.
- Committed OpenAPI contract (`contracts/openapi.json`) with drift checks in backend and frontend.
- PostgreSQL: read-only synthetic fab business DB, app DB with pgvector; bootstrap script.
- Deterministic synthetic fab data generator with two injected scenarios.
- SECOM / WM-811K download tooling.
- Blazor Web App shell with system status page, `IFabPilotApi` client, xUnit tests.
- Docker Compose, GitHub Actions CI, VS Code settings, ADRs 0001–0006, workflow docs.
