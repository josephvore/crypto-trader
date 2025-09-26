# Variables
PY=poetry run
UVICORN=$(PY) uvicorn
API_MODULE=crypto_trader.api.main:app
API_HOST?=0.0.0.0
API_PORT?=8080
FRONTEND_DIR=frontend

# --- Setup & Quality ---

install:
	poetry install

setup:
	poetry install
	pre-commit install
	cd $(FRONTEND_DIR) && npm i

lint:
	poetry run ruff check

fmt:
	poetry run ruff check --fix
	poetry run ruff format

type:
	poetry run mypy src

test:
	poetry run pytest

checks: lint type test

# --- Backend ---

api:
	API_PASSWORD=$${API_PASSWORD} $(UVICORN) $(API_MODULE) --host $(API_HOST) --port $(API_PORT) --reload

api-prod:
	API_PASSWORD=$${API_PASSWORD} $(UVICORN) $(API_MODULE) --host $(API_HOST) --port $(API_PORT)

# --- Frontend ---

frontend:
	cd $(FRONTEND_DIR) && npm run dev

frontend-build:
	cd $(FRONTEND_DIR) && npm run build

frontend-preview:
	cd $(FRONTEND_DIR) && npm run preview

# --- Dev convenience ---

dev:
	( API_PASSWORD=$${API_PASSWORD} $(UVICORN) $(API_MODULE) --host $(API_HOST) --port $(API_PORT) --reload ) & \
	( cd $(FRONTEND_DIR) && npm run dev )

.PHONY: install setup lint fmt type test checks api api-prod frontend frontend-build frontend-preview dev
