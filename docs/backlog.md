# Product backlog

Ordered by priority. Move items to GitHub Issues (template: *User story*) once the repo is set up.
Must = needed for the MVP demo; Should = strong value; Could = nice to have.

## MVP goal (P1–P3)
> A yield engineer asks "Why did POLY_CD go up last week?" and FabPilot answers with the right
> tool, the evidence (query + chart/table) and a suspected cause (ETCH-03), without writing SQL.

## P1 – minimal agent loop (next iteration)

| # | Story | Priority | Acceptance criteria |
|---|---|---|---|
| 1 | As an engineer I want to ask a question in plain language and get an answer, so that I don't need SQL. | Must | `POST /api/v1/chat` with a question returns an answer from the LLM; LLM endpoint chosen via `.env`; unit-tested with a fake `ChatModel`. |
| 2 | As an engineer I want the agent to look up lot facts (status, route, holds), so that answers are grounded in data. | Must | One read-only tool in `fabdata` (e.g. `get_lot_summary(lot_id)`); agent calls it for "status of lot X"; result shown with the answer. |
| 3 | As an engineer I want my conversation kept, so that I can ask follow-ups. | Must | New `chat` module stores conversation + messages in `fabpilot_app`; follow-up question uses history. |
| 4 | As an engineer I want a chat page, so that I can use FabPilot without tools like curl. | Must | Blazor `/chat` sends questions via `IFabPilotApi` and renders answers. |
| 5 | As an admin I want each tool call logged, so that answers are auditable. | Should | `tool_call` rows with arguments, duration, row count. |

## P2 – streaming

| # | Story | Priority | Acceptance criteria |
|---|---|---|---|
| 6 | As an engineer I want to see the answer appear token by token and which tool is running. | Must | SSE endpoint; Blazor renders tokens and tool steps; first token < 2 s. |


## P3 – analysis tools

| # | Story | Priority | Acceptance criteria |
|---|---|---|---|
| 7 | As a yield engineer I want the trend of a parameter over time by tool (SPC-style). | Must | Finds the ETCH-03 drift from a vague question. |
| 8 | Tool commonality for a set of bad lots. | Must | Ranks ETCH-03 first for drift lots. |
| 9 | Export the evidence to Excel. | Should | `.xlsx` download with query and data. |
| 10 | Wafer-map pattern classifier (WM-811K) as a tool. | Could | Classifies Edge-Ring maps. |
| 11 | Guarded Text-to-SQL for questions no fixed tool covers. | Should | SELECT-only, allow-listed schema, row limit, timeout. |

## Later
RAG over SOP/FMEA docs (P4) · JWT auth + RBAC (P5) · evals from injected scenarios (P6) ·
second, non-fab manufacturing demo.
