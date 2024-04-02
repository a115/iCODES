.DEFAULT_GOAL := build
.EXPORT_ALL_VARIABLES:

PYTHONPATH=.

.PHONY: format
format:
	poetry run ruff format .
	poetry run ruff check --fix .

.PHONY: lint
lint:
	poetry run ruff check .

.PHONY: test
test:
	poetry run pytest tests/

.PHONY: build
build: lint test

