# Trading Bot — Agent Instructions

Intelligent multi-market equity trading bot for Indian (NSE/BSE), US (NYSE/NASDAQ), and European (XETRA) markets.

## Repository Map

```
docs/                       # Research, design docs, ADRs
  trading-bot-research.md   # Master MoA research document (2639 lines) — source of truth
src/
  agents/                   # LangGraph agent nodes (12-agent roster)
  brokers/                  # Broker MCP adapters (Zerodha, IBKR, Angel One)
  data/                     # Market data feed connectors (Polygon.io, Alpaca, Kite, MDS)
  risk/                     # Risk management (Kelly criterion, VaR, circuit breakers)
  execution/                # Order management and routing
  utils/                    # Shared utilities
tests/
  unit/                     # Unit tests (pytest)
  integration/              # Integration tests with broker sandboxes
config/                     # Environment configs (dev/staging/prod)
scripts/                    # One-off and ops scripts
notebooks/                  # Research and backtesting notebooks (vectorbt)
```

## Architecture

12-agent LangGraph system. Agent roster:
1. **Market Scanner** — filters universe by momentum/volume
2. **Fundamental Analyst** — P/E, DCF, earnings quality
3. **Technical Analyst** — MACD, RSI, Bollinger, order flow
4. **Macro Analyst** — rates, FX, inflation regime
5. **Sentiment Analyst** — news NLP, options skew
6. **Alt Data Analyst** — satellite, web scraping, insider filings
7. **Signal Aggregator** — weighted ensemble, confidence scoring
8. **Red Team (Cynical Advisor)** — adversarial bear case, bias detection
9. **Portfolio Manager** — Kelly sizing, correlation-adjusted allocation
10. **Risk Manager** — VaR/CVaR, drawdown limits, circuit breakers
11. **Execution Agent** — order routing, slippage minimization
12. **Compliance Agent** — SEBI/MiFID II/PDT rule gating

Orchestration framework: **LangGraph** (state persistence, conditional branching, parallel node execution).

## Broker Integrations

| Broker | Market | Library | MCP Port |
|--------|--------|---------|----------|
| Zerodha Kite Connect | NSE/BSE | kiteconnect | 8001 |
| Angel One SmartAPI | NSE/BSE | smartapi-python | 8002 |
| IBKR ib_insync | NYSE/NASDAQ/XETRA | ib_insync | 8003 |

## Key Conventions

- **Python 3.11+**, `uv` for dependency management
- **pytest** for all tests; integration tests tagged `@pytest.mark.integration`
- **Environment variables** in `.env` (never commit); see `config/env.example`
- **Type hints** everywhere; `mypy --strict` enforced in CI
- **Async-first**: all broker calls and data fetches are `async`
- **Logging**: structured JSON via `structlog`; every trade action logged at INFO

## Research Reference

Before implementing any agent, risk model, or broker integration, read the relevant section of `docs/trading-bot-research.md`:
- §1 Equity Price Determinants → `src/agents/`
- §2 Market Data Feeds → `src/data/`
- §3 Multi-Agent Architecture → `src/agents/`
- §4 Framework Recommendation (LangGraph) → root orchestration
- §5 Broker MCP Integration → `src/brokers/`
- §6 Risk Management → `src/risk/`
- §7 Red Team Analysis → `src/agents/red_team.py`
- §8 Implementation Roadmap → project milestones

## Compliance Constraints

- **SEBI (India)**: Algo trading requires broker approval; API keys restricted per SEBI 2022 circular
- **US PDT Rule**: < $25K account cannot make 4+ round trips in 5 days on margin
- **MiFID II (EU)**: Best execution obligation; pre/post-trade transparency requirements
- Compliance agent must gate every order before submission

## Running Locally

```bash
uv sync
cp config/env.example .env   # fill in API keys
pytest tests/unit/           # run unit tests
python -m src.main --market india --mode paper
```
