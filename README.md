# Crypto-Trader GUI

A desktop-optimized trading dashboard for the Crypto-Trader system with:
- FastAPI backend exposing control surfaces (strategies, orders, positions/portfolio, market data, config, backtesting)
- Native WebSocket for real-time prices, orders, positions, equity, and events
- React/TypeScript frontend (Vite + MUI + Chart.js)
- Simple password auth for single-user local use

## Prerequisites

- Python 3.12 (managed by Poetry)
- Node.js (via nvm) and npm
- Make (optional but recommended)

## Quick Start

1) Install dependencies
- make setup

2) Configure auth
- export API_PASSWORD="your-password"

3) Start backend API
- make api
- Health: http://localhost:8080/healthz
- OpenAPI: http://localhost:8080/docs

4) Start frontend (new terminal)
- make frontend
- Dev URL: http://localhost:5173

5) Login
- Use the same password you set in API_PASSWORD

## Make Targets

- make setup: Poetry install, pre-commit install, and npm install in frontend/
- make lint: Ruff lint
- make fmt: Ruff autofix and format
- make type: Mypy type checks
- make test: Pytest suite
- make checks: lint + type + test

Backend:
- make api: Run FastAPI (reload) on http://localhost:8080
- make api-prod: Run FastAPI without reload

Frontend:
- make frontend: Vite dev server at http://localhost:5173
- make frontend-build: Build production frontend (dist/)
- make frontend-preview: Preview built frontend

Dev combo:
- make dev: Run backend (reload) and frontend dev server together

Notes:
- Override backend host/port: make api API_HOST=127.0.0.1 API_PORT=9000
- API_PASSWORD must be exported before starting backend or connecting frontend

## Configuration

Core settings and app config live in src/crypto_trader/core/config.py.
- Example config: templates/configs/example.yaml

Auth:
- Header: X-API-Password: $API_PASSWORD
- WebSocket: ws://localhost:8080/ws?token=$API_PASSWORD

## API Overview

Base: http://localhost:8080

Public:
- GET /healthz
- GET /metrics

WebSocket:
- /ws (topics: prices, orders, positions, portfolio, logs)

Protected (X-API-Password required):
- Strategies:
  - GET /api/strategies
  - GET /api/strategies/active
  - POST /api/strategies/config
- Orders:
  - GET /api/orders[?status=open|history]
  - POST /api/orders
  - POST /api/orders/{id}/cancel
- Positions / Portfolio:
  - GET /api/positions
  - GET /api/portfolio
- Market Data:
  - GET /api/market-data/ohlcv?symbol=&timeframe=&limit=
- Config:
  - GET /api/config/settings
  - GET /api/config/app
  - PUT /api/config/app
- Backtest:
  - POST /api/backtest

## Frontend

Tech:
- React 18 + TypeScript + Vite
- Material-UI (MUI), Zustand
- Chart.js (+ chartjs-adapter-date-fns)
- Native WebSocket

Structure:
- frontend/src/ui/App.tsx: App shell and routing
- frontend/src/ui/pages: Dashboard, Portfolio, Orders, Backtest, Settings, Login
- frontend/src/utils/http.ts: Axios client with password header
- frontend/src/utils/realtime.ts: WebSocket connection and topic handling
- frontend/src/utils/store.ts: Zustand stores

Environment:
- Frontend expects API at http://localhost:8080 by default
- Login stores the password for the session

## Usage Flows

- Place simulated orders on Orders page; watch open orders and fills on Dashboard
- Monitor positions/portfolio and equity on Portfolio and Dashboard
- Run Backtests and view equity curve on Backtest page
- Adjust strategy params and app settings on Settings page
- Observe real-time events via WebSocket

## Testing & Quality

- Lint: make lint
- Type: make type
- Tests: make test

Pre-commit hooks run on commit; CI mirrors these checks.

## Troubleshooting

401 Unauthorized:
- Ensure API is running and API_PASSWORD is exported
- Use the same password in the frontend login

Frontend build issues:
- make frontend-build
- Re-run make setup if dependencies changed

Port conflicts:
- Override backend with API_PORT
- Adjust Vite dev server port via frontend config if needed

## Safety

- Start in paper/dry-run modes
- Store API keys in .env or a secret manager
- No profitability guarantees

Link to Devin run: https://app.devin.ai/sessions/a15304c9a28b497d90c2bc3a77f65175
Requester: Joseph Vore (@josephvore)
