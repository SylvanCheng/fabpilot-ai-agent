# ADR-0005: Generated OpenAPI contract, checked in CI

- Status: Accepted
- Date: 2026-11-02

## Context
Backend (Python) and frontend (C#) are different languages. Silent drift between them is a
classic source of runtime bugs.

## Decision
FastAPI response models are the source of truth. `uv run fabpilot-export-openapi` writes
`contracts/openapi.json`, which is committed. CI fails if the file is stale (backend contract
test) or if a frontend DTO uses a field the contract doesn't have (frontend contract test).
Product endpoints are versioned under `/api/v1`.

## Alternatives considered
Generating the C# client (NSwag/Kiota): worth revisiting when the API grows; for a handful of
endpoints, hand-written DTOs plus a contract test are simpler to read.

## Consequences
Every API change shows up as a reviewable diff of `contracts/openapi.json`.
