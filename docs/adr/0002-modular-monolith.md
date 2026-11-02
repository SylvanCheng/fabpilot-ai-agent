# ADR-0002: Modular monolith with ports & adapters

- Status: Accepted
- Date: 2026-11-02

## Context
The product will grow features (chat loop, tools, RAG, auth, evals) iteratively. Past projects
degraded into tightly coupled code that was hard to change. Microservices would add deployment,
networking and data-consistency cost that a one-person team cannot justify.

## Decision
One backend process, split into modules under `fabpilot.modules`. Each module has a public API
(`__init__.py`), a framework-free core (`service.py`, `ports.py`) and adapters. Modules never
import each other; the composition root (`fabpilot.main`) wires them. Boundaries are enforced
by import-linter in CI.

## Alternatives considered
- *Layered by technical type* (`routers/`, `models/`, `services/`): simple, but every feature
  touches every folder, and nothing stops cross-feature coupling.
- *Microservices*: strong isolation, but premature for one developer and one database server.

## Consequences
- A little more ceremony per module (ports, wiring).
- Business logic is unit-testable without DB or HTTP.
- A module can be extracted into a service later by swapping its in-process port for an HTTP one.
