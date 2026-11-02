# Architecture Decision Records

Short documents that capture one significant decision, its context and its consequences
([Michael Nygard's format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)).
They answer "why is it like this?" months later. Never edit an accepted ADR's decision; supersede
it with a new one.

| # | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-modular-monolith.md) | Modular monolith with ports & adapters | Accepted |
| [0003](0003-separate-read-only-business-db.md) | Separate, read-only business database | Accepted |
| [0004](0004-openai-compatible-llm-endpoint.md) | LLM behind an OpenAI-compatible endpoint | Accepted |
| [0005](0005-contract-first-http-api.md) | Generated OpenAPI contract, checked in CI | Accepted |
| [0006](0006-blazor-server-frontend.md) | Blazor Web App (Interactive Server) as a thin UI | Accepted |

New ADR: copy [template.md](template.md) to the next number.
