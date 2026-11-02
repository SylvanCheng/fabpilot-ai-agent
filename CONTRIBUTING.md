# Contributing

The full process is in [docs/process/workflow.md](docs/process/workflow.md). In short:

1. Pick a *ready* story from the backlog; create a branch `feat/<issue>-short-name`.
2. Read [docs/architecture.md](docs/architecture.md) before adding code; respect module boundaries.
3. `make check` must pass. If the API changed: `make contract` and commit `contracts/openapi.json`.
4. Commit with Conventional Commits; open a PR using the template; squash-merge when CI is green.

One-time setup: `make setup` (installs deps and pre-commit hooks).
