# Roadmap

| Phase | Deliverable | Done when |
|---|---|---|
| **P0 Environment & mock data** | Repo layout, Compose, business + app schemas, synthetic generator with injected scenarios, SECOM/WM-811K downloaders, `/health` + `/health/ready`, Blazor status page, CI | `docker compose up` shows green checks; CI green |
| P1 Minimal loop | `POST /chat`: LangChain agent, Qwen through OpenAI-compatible client, one read-only SQL tool on `fab_business`, conversation persisted in app DB | Ask "how many lots are on hold?" and get a correct answer with the SQL shown |
| P2 Streaming | SSE endpoint, Blazor chat UI renders tokens and tool-call steps live | First token < 2 s on the dev GPU |
| P3 Tools | Governed query layer (fixed tools first, guarded Text-to-SQL second), SPC / trend / tool-commonality analysis, WM-811K wafer-map classifier as a tool, Excel/ZIP export | Agent finds the ETCH-03 drift from a vague question |
| P4 RAG | Ingest SOP / FMEA / OCAP-style documents (written from scratch), pgvector retrieval with citations | Answers cite document + chunk |
| P5 Engineering | JWT auth, per-role data permissions, audit log of every tool call, structured logging, timeouts, global error handling, Alembic migrations | Security review checklist passes |
| P6 Deploy & evals | Cloud deployment (vLLM), eval set built from the injected scenarios, regression in CI | Eval score tracked per commit |

A second, non-fab demo (general discrete manufacturing) reuses the same engine with a different
schema and generator once P3 is stable.
