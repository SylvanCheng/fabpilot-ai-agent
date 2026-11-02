# Common tasks. Run `make help`. (Windows: use from WSL2.)
.DEFAULT_GOAL := help
BACKEND := backend
FRONTEND := frontend

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Install backend/frontend deps and git hooks
	cd $(BACKEND) && uv sync
	cd $(FRONTEND) && dotnet restore FabPilot.sln
	uvx pre-commit install

check: lint test ## Everything CI runs, except image builds

lint: ## Format check, lint, architecture rules
	cd $(BACKEND) && uv run ruff format --check . && uv run ruff check . && uv run lint-imports
	cd $(FRONTEND) && dotnet format FabPilot.sln --verify-no-changes

test: ## Backend + frontend tests (DB tests auto-skip without Postgres)
	cd $(BACKEND) && uv run pytest
	cd $(FRONTEND) && dotnet test FabPilot.sln

fmt: ## Auto-format all code
	cd $(BACKEND) && uv run ruff format . && uv run ruff check --fix .
	cd $(FRONTEND) && dotnet format FabPilot.sln

contract: ## Regenerate contracts/openapi.json after API changes
	cd $(BACKEND) && uv run fabpilot-export-openapi

up: ## Start the full stack in Docker
	docker compose up -d --build

down: ## Stop the stack (keeps data)
	docker compose down

db: ## Start only PostgreSQL
	docker compose up -d postgres

data: ## Load synthetic fab data (needs Postgres)
	cd $(BACKEND) && uv run fabpilot-datagen

api: ## Run the backend with hot reload
	cd $(BACKEND) && uv run uvicorn fabpilot.main:create_app --factory --reload

web: ## Run the frontend with hot reload
	cd $(FRONTEND)/FabPilot.Web && dotnet watch

.PHONY: help setup check lint test fmt contract up down db data api web
