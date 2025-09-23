.PHONY: setup lint type test fmt precommit install

install:
	poetry install

setup:
	poetry install
	poetry run pre-commit install

lint:
	poetry run ruff check

fmt:
	poetry run ruff check --fix
	poetry run ruff format

type:
	poetry run mypy src

test:
	poetry run pytest
