# Crypto-Trader

Production-grade, low-latency crypto trading platform focusing on risk-adjusted returns.

- Python 3.11+, asyncio-first with CCXT and Freqtrade
- Plugin system for strategies, risk, execution
- Backtesting, tuning, paper, and live trading
- Postgres/TimescaleDB, Redis, FastAPI, Prometheus
- Docker and CI ready

Quickstart:
- Install Poetry and run: make setup
- Copy .env.example to .env and adjust
- Run CLI: poetry run python -m crypto_trader.cli --help

Safety:
- Paper/dry-run first
- API keys via .env or secret stores
- No profitability promises
