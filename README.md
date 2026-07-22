# Trading OS

Evidence-gated, two-broker, long-only cash-equity Trading OS.

- **Zerodha Kite Connect** — NSE/BSE cash equities, INR strategy sleeve.
- **Alpaca** — supported US venues, USD strategy sleeve.

Built as a modular Python event-ledger application: account-partitioned broker observations,
current-portfolio projections, immutable policy releases, deterministic decisioning, and
ports-and-adapters broker integration. Postgres is the authoritative relational path; Valkey is
disposable coordination state; OWL/SHACL, Fuseki and Neo4j are rebuildable research projections.

The controlling documents are:

- Spec: `docs/superpowers/specs/2026-07-22-live-v1-architecture-amendment.md`
- Plan: `docs/superpowers/plans/2026-07-22-nine-day-live-v1-implementation.md`
- ADRs: `docs/adr/0001..0003`

> The `2026-07-21` plans (paper-first, EOD-only, ontology-sequenced) are superseded and marked
> "do not execute." The raw MoA extension drafts returned NO-GO and are not specifications.

## Core invariants

- Research agents never emit quantity, price, target weight, broker order, or executable command.
- Every exposure-increasing decision binds fresh, partitioned, current portfolio state.
- Broker custody observations and OS intention/history stay distinct; reconciliation never silently
  chooses a winner.
- Each order belongs to one Brokerage Account, capital envelope, policy set and kill generation.
- Policy changes create immutable, effective-dated releases; they never reset loss, drawdown or
  history.
- Relational retrieval is the permanent decision champion; RDF and Neo4j are rebuildable projections.
- Family and non-equity execution are deny-by-default in V1.

## Live activation is a policy operation, not a config edit

Enabling live trading is **not** achieved by editing a base URL or setting `ALPACA_PAPER=false`.
A live write requires a broker-scoped, current `LiveAuthorityReceipt` matching the account, policy
release versions, readiness checks and current kill generation. Kite interactive login and session
renewal are operator-owned steps (there is no automated TOTP login in this system).

## Running locally

```bash
make sync            # uv sync --extra dev
make services-up     # Postgres/TimescaleDB, Valkey, Fuseki, Neo4j (localhost only)
cp config/env.example .env
make verify          # ruff -> mypy -> pytest, in that order
```

## Repository map

```
docs/            research, controlling spec/plan, ADRs, runbooks
src/trading_os/  application packages (kernel, identity, policy, ledger, brokers, portfolio,
                 market_data, discovery, tradability, research, ontology, decision, execution,
                 retrospective, app)
tests/           unit, contract, integration, replay and live-readiness tests
deploy/          Compose service stack and operator configuration
web/             React operator console with TradingView Lightweight Charts
```
