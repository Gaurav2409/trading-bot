# Trading OS — developer workflow entry points.
# `make verify` is the one-command gate every later task depends on.

.DEFAULT_GOAL := verify
COMPOSE := docker compose -f deploy/compose.yml

.PHONY: sync services-up services-down lint typecheck test verify

sync:
	uv sync --extra dev

services-up:
	$(COMPOSE) up -d

services-down:
	$(COMPOSE) down

lint:
	uv run ruff check src tests

typecheck:
	uv run mypy src/trading_os

test:
	uv run pytest

# verify runs Ruff, then mypy, then pytest, in that order.
verify: lint typecheck test
