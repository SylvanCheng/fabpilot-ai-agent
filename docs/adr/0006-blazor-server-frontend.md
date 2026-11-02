# ADR-0006: Blazor Web App (Interactive Server) as a thin UI

- Status: Accepted
- Date: 2026-11-02

## Context
Manufacturing IT is often .NET-centric; the target users work on intranet desktops.

## Decision
.NET 8 Blazor Web App with Interactive Server render mode. It holds no business logic: pages
depend on `IFabPilotApi`, implemented by an HTTP client to the backend.

## Consequences
The LLM and databases are never exposed to the browser. UI logic is testable against a fake
`IFabPilotApi`. Needs a persistent SignalR connection per user, which is fine at intranet scale.
