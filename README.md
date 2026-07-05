# trading-bot

Intelligent multi-market equity trading bot for Indian (NSE/BSE), US (NYSE/NASDAQ), and European (XETRA) markets.

Built on a **12-agent LangGraph architecture** with broker MCP integrations for Zerodha Kite Connect, Angel One SmartAPI, and Interactive Brokers (IBKR).

## Markets

| Market | Exchange | Broker | Data Feed |
|--------|----------|--------|-----------|
| India | NSE / BSE | Zerodha Kite Connect, Angel One | Kite WebSocket, NSE bhavcopy |
| US | NYSE / NASDAQ | IBKR ib_insync | Polygon.io, Alpaca, IEX Cloud |
| Europe | XETRA | IBKR (IBIS routing) | Deutsche Börse MDS, IBKR |

## Agent Roster

12 LangGraph nodes: Market Scanner → Fundamental / Technical / Macro / Sentiment / Alt Data Analysts → Signal Aggregator + Red Team → Portfolio Manager → Risk Manager → Execution Agent → Compliance Agent.

## Status

Research complete. Implementation pending — see `docs/trading-bot-research.md` for the full design.

## Quick Start

```bash
uv sync
cp config/env.example .env
pytest tests/unit/
python -m src.main --market india --mode paper
```

## Docs

- [Research & Design](docs/trading-bot-research.md) — MoA-synthesized research covering all aspects of the system
