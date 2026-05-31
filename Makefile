.DEFAULT_GOAL := help

# Prefer project-local bootstrap, then PATH
ifeq ($(wildcard .tools/bin/uv),)
  UV := uv
else
  UV := .tools/bin/uv
endif

COMPOSE_FILE := docker/docker-compose.yml
# Avoid Docker Desktop credsStore when only Engine + compose-plugin are installed
export DOCKER_CONFIG := $(CURDIR)/docker/.docker
ALEMBIC_INI := src/core/database/alembic.ini
MIGRATE_MSG ?= schema change

.PHONY: help install test lint db-up db-down db-logs migrate migrate-new crawl-dry crawl

help: ## List available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies (uv sync)
	$(UV) sync

test: ## Run tests
	$(UV) run pytest

lint: ## Lint (reserved for future use)
	@echo "lint not configured yet"

db-up: ## Start local PostgreSQL
	docker compose -f $(COMPOSE_FILE) up -d

db-down: ## Stop local PostgreSQL
	docker compose -f $(COMPOSE_FILE) down

db-logs: ## Tail PostgreSQL logs
	docker compose -f $(COMPOSE_FILE) logs -f postgres

migrate: ## Apply database migrations
	$(UV) run alembic -c $(ALEMBIC_INI) upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new MIGRATE_MSG="description")
	$(UV) run alembic -c $(ALEMBIC_INI) revision --autogenerate -m "$(MIGRATE_MSG)"

crawl-dry: ## Run crawler without persisting
	$(UV) run python -m crawler.jobs.run --dry-run

crawl: ## Run crawler and persist observations
	$(UV) run python -m crawler.jobs.run --save
