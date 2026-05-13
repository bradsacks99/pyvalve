# Makefile for pyvalve project with uv

.PHONY: help install dev test lint type format clean lock check integration

help:
	@echo "Common make targets:"
	@echo "  install   - Install project with uv"
	@echo "  dev       - Install project with dev dependencies"
	@echo "  lint      - Run pre-commit hooks"
	@echo "  type      - Run mypy type checks"
	@echo "  test      - Run tests with pytest"
	@echo "  integration - Run clamd integration tests"
	@echo "  check     - Lint, type check, and test"
	@echo "  format    - Run formatters (via pre-commit)"
	@echo "  lock      - Update uv.lock"
	@echo "  clean     - Remove caches and local venv"

check: lint type test

install:
	uv pip install .

dev:
	uv pip install .[dev]

test:
	uv run --extra dev pytest

integration:
	PYVALVE_RUN_INTEGRATION=1 uv run --extra dev pytest -m integration

lint:
	uv run --extra dev pre-commit run --all-files

type:
	uv run --extra dev mypy src/pyvalve

format:
	uv run --extra dev pre-commit run --all-files

lock:
	uv lock

clean:
	rm -rf .venv __pycache__ */__pycache__
