# FabPilot

**Self-hosted LLM agent for industrial process & quality data (semiconductor fab first).**

Engineers in a fab spend hours clicking through fixed IT query screens, exporting to Excel and
stitching results together. FabPilot lets a process, integration or yield engineer ask in natural
language ("why did POLY_CD drift last week?") and have an agent query a governed, read-only data
layer, run analysis tools, and answer with evidence.

> **Data & provenance.** FabPilot is an independent, from-scratch project. It uses only
> **public datasets** ([SECOM](https://archive.ics.uci.edu/dataset/179/secom),
> [WM-811K](https://www.kaggle.com/datasets/qingyi/wm811k-wafer-map)) and **synthetic data**
> produced by the generator in this repo. It contains no code, data, schemas, recipes, specs
> or documents from any employer, past or present. All product, tool and step names are generic
> and invented.

## Status

| Phase | Scope | State |
|---|---|---|
| **P0** | Architecture & process foundation: modular backend, contracts, DB schemas, synthetic data, dataset tooling, Blazor shell, CI | ✅ |
| P1 | Minimal agent loop (LangChain + Qwen via OpenAI-compatible API) | next |
| P2 | Token streaming over SSE to Blazor | |
| P3 | Tools: governed SQL, SPC/stats, wafer-map classifier, Excel export | |
| P4 | RAG over SOP/FMEA-style documents (pgvector) | |
| P5 | Engineering: auth (JWT), RBAC, audit, structured logs, timeouts, error handling | |
| P6 | Cloud deployment + evals | |

See [docs/roadmap.md](docs/roadmap.md) for detail.

## Architecture

```
 Browser ──► Blazor Web App (.NET 8, Interactive Server)  :5080      thin UI, depends on IFabPilotApi
                 │  HTTP /api/v1   (contract: contracts/openapi.json)
                 ▼
            FastAPI backend (Python 3.12)  :8000 ──► LLM (Qwen) on rented cloud GPU
            modular monolith                          Ollama (dev) / vLLM (prod),
            core ◄─ modules ◄─ main ◄─ devtools       OpenAI-compatible, chosen in .env
                 │
        ┌────────┴─────────┐
        ▼                  ▼
  fab_business DB     fabpilot_app DB
  (synthetic fab,     (chats, tool-call audit,
   read-only role)     RAG chunks with pgvector)
```

Engineering principles, each enforced by a tool rather than by discipline alone:

| Principle | How |
|---|---|
| High cohesion | One module per capability (`health`, `fabdata`, `llm`, later `chat`, `tools`, `rag`), each with its own settings, ports, adapters and API. |
| Low coupling | Modules never import each other; framework-free domain code. Checked by **import-linter** in CI. |
| Explicit interfaces | Python `Protocol` ports inside the backend; versioned HTTP API with a committed **OpenAPI contract**, verified by backend *and* frontend tests. |
| One error shape | RFC 9457 `application/problem+json` everywhere. |
| Config, not code | All environment differences (DB, LLM backend) are env vars. |
| Decisions written down | [Architecture Decision Records](docs/adr/). |

More: [docs/architecture.md](docs/architecture.md) · [workflow](docs/process/workflow.md) ·
[backlog](docs/backlog.md) · [synthetic data](docs/synthetic-data.md).

## Repository layout

```
backend/                 FastAPI app (uv, ruff, pytest, import-linter)
  src/fabpilot/
    core/                shared kernel: settings, errors, logging, DB factory, HealthCheck port
    modules/             health · fabdata · llm   (one folder = one module)
    main.py              composition root: wires modules together
    devtools/            datagen (`fabpilot-datagen`), datasets, OpenAPI export
  tests/                 unit (fakes) · contract · integration (real Postgres)
frontend/
  FabPilot.Web/          Blazor Web App; Api/ = IFabPilotApi + contract DTOs
  FabPilot.Web.Tests/    xUnit: API client + contract tests
contracts/openapi.json   generated API contract (committed, checked in CI)
db/                      init script, business schema, app schema
docs/                    architecture, ADRs, workflow, backlog, roadmap
data/raw/                downloaded public datasets (git-ignored)
Makefile                 `make help` lists common tasks
```

## Quickstart

### 0. Install the tools (one time)

You need: **Git**, **Docker Desktop**, **VS Code**, **uv** (Python), **.NET 8 SDK**.

<details>
<summary><b>Windows (recommended: WSL2)</b></summary>

1. Open PowerShell as Administrator: `wsl --install` → reboot → finish the Ubuntu setup
   (pick a Linux username/password).
2. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/). In
   *Settings → Resources → WSL integration*, enable your Ubuntu distro.
3. Install [VS Code](https://code.visualstudio.com/) on Windows, then the **WSL** extension.
4. In the Ubuntu terminal:
   ```bash
   sudo apt update && sudo apt install -y git dotnet-sdk-8.0
   curl -LsSf https://astral.sh/uv/install.sh | sh     # then open a new terminal
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```
5. Clone **inside the Linux file system** (much faster than `/mnt/c/...`):
   ```bash
   mkdir -p ~/code && cd ~/code
   git clone https://github.com/SylvanCheng/fabpilot-ai-agent.git
   cd fabpilot-ai-agent && code .
   ```
   `code .` opens VS Code on Windows, connected to WSL (bottom-left shows *WSL: Ubuntu*).
</details>

<details>
<summary><b>macOS</b></summary>

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git uv
brew install --cask visual-studio-code
# Docker Desktop: https://www.docker.com/products/docker-desktop/
# .NET 8 SDK installer: https://dotnet.microsoft.com/download/dotnet/8.0
git clone https://github.com/SylvanCheng/fabpilot-ai-agent.git
cd fabpilot-ai-agent && code .
```
If `code` is not found: in VS Code press `Cmd+Shift+P` → *Shell Command: Install 'code' command in PATH*.
</details>

When VS Code opens the folder it offers to install the **recommended extensions**
(`.vscode/extensions.json`): accept. Useful keys: `Ctrl+`` ` (terminal), `Ctrl+Shift+P`
(command palette), `F5` (run the selected launch config). On macOS use `Cmd` instead of `Ctrl`.

### 1. Run everything in Docker

```bash
cp .env.example .env                       # then change the passwords
docker compose up -d --build               # postgres + backend + frontend
docker compose --profile tools run --rm datagen   # load synthetic fab data
```

- Frontend: <http://localhost:5080> (System status page shows DB checks)
- API docs: <http://localhost:8000/docs>

Reset the databases: `docker compose down -v` (deletes the volume), then `up` again.

### 2. Develop locally (hot reload)

Keep only Postgres in Docker and run the apps on your machine:

```bash
docker compose up -d postgres

cd backend
uv sync                                    # creates backend/.venv
uv run fabpilot-datagen                    # load synthetic data (uses FAB_LOADER_DSN from ../.env)
uv run uvicorn fabpilot.main:create_app --factory --reload  # http://localhost:8000/docs

# second terminal
cd frontend/FabPilot.Web
dotnet watch                               # http://localhost:5080
```

Or use VS Code's *Run and Debug* panel: **Backend: FastAPI** and **Frontend: Blazor**.

### 3. LLM endpoint (from P1 on)

Models run on a rented cloud GPU, never locally. Point `.env` at it:

```bash
# Ollama on the GPU box, reached through an SSH tunnel
ssh -N -L 11434:localhost:11434 user@gpu-box
LLM_PROVIDER=ollama  LLM_BASE_URL=http://localhost:11434/v1  LLM_MODEL=qwen3:8b

# vLLM
LLM_PROVIDER=vllm    LLM_BASE_URL=http://gpu-box:8000/v1     LLM_MODEL=Qwen/Qwen3-8B
```

### 4. Public datasets (optional in P0)

```bash
cd backend
uv run fabpilot-datasets status
uv run fabpilot-datasets secom     # direct download from UCI (~5 MB)
uv run fabpilot-datasets wm811k    # needs Kaggle CLI + API token, or manual download
```

Files land in `data/raw/` and are never committed.

## Quality checks

```bash
make check      # ruff format/lint, import-linter, dotnet format, pytest, dotnet test
make contract   # after changing the API: regenerate contracts/openapi.json
```

DB integration tests run automatically when a Postgres initialised by `db/init` is reachable
(CI always provides one) and are skipped otherwise. How work flows from story to release is in
[docs/process/workflow.md](docs/process/workflow.md).

## License

[MIT](LICENSE). Dataset licenses are those of their publishers.
