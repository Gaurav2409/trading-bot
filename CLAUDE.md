# Trading Bot — Agent Instructions

> **STATUS: live-V1 safety spine + ontology hardening + domain-agent P0 tracer + live NSE/BSE source watcher are merged.**
> The single source of truth for scope and status is **`docs/V1-LEDGER.md`** (all 52 original tasks: shipped/partial/deferred, deliberate divergences, and the deferred workstreams WS-1…WS-11). Start at **`docs/README.md`** for the full doc map. Where older prose drifts, the ledger + the specs in `docs/superpowers/specs/` + the ADRs in `docs/adr/` win.
> This file was rewritten 2026-07-24 to match the merged design. The prior version (12-agent LangGraph / 3-market NSE-BSE-XETRA / Angel One + IBKR / broker-MCP-ports / Kelly) was **SUPERSEDED and wrong — ignore any copy that still shows it.**

Autonomous **swing/positional** cash-equity trading OS for **two markets**: India (NSE/BSE via
Zerodha Kite, INR sleeve) and US (NYSE/NASDAQ via Alpaca, USD sleeve). Built and validated
**paper-first**, then live on **small disposable balances** behind a `LiveAuthorityReceipt`.
**Long-only, cash-only, daily-bar/EOD.** No shorting, leverage, derivatives, options, futures,
crypto, FX trading, intraday alpha, Angel One, IBKR, or European venues.

## Core invariant (read first)

**"LLMs propose categorical labels; deterministic code disposes all numbers."**
- A **slow research path** (calendar-scheduled) produces categorical `EvidencePacket`s — an
  assessment label + citations + eligibility effect. **No number crosses the evidence seam:** no
  price, quantity, target, expected return, position weight, or conviction multiplier. The seam is
  enforced structurally in `research/seam.py` (closed-vocabulary allowlist + numeric-run rejection)
  and re-enforced at `admit_packet` (`research/orchestrator.py`).
- A **fast deterministic hot path** (versioned, unit-tested Python, no LLM): sizing, VaR/CVaR,
  correlation, drawdown, compliance, execution, kill-switch. Evidence only **gates and ranks**
  candidates — it **never scales size**.
- The **relational retrieval champion is permanent** (`ontology/relational.py`). RDF (Fuseki) and
  Neo4j are **rebuildable projections** that never own truth; on disagreement the relational answer
  wins and the disagreement is recorded.
- Every LLM role is **provider-swappable** behind one `LLMRole` seam (`agents/llm.py`,
  `agents/providers.py`); provider specifics never cross it (ADR-0007).

## Architecture (as merged)

**Ports-and-adapters around an append-only event core.** Orchestration is **calendar-aware
scheduled jobs** (`app/scheduler.py`), not a continuous agent loop. LangGraph is **contained inside
one agent node** behind `ResearchAgentPort` — it is not the orchestrator (ADR-0006). The canonical
append-only run ledger is authoritative over framework checkpoints (ADR-0009).

Real module map (`src/trading_os/`):

```
kernel/        immutable IDs, values, event envelope
ledger/        append-only Postgres event store + replay
identity/      legal parties, account authority
policy/        immutable policy releases, capability, compliance, live-authority
market_data/   validated multi-clock snapshots
discovery/     broad discovery, coverage receipts
tradability/   account tradability packets
research/      ResearchAgentPort, EvidencePacket, categorical seam, admit_packet,
               source watchers (live NSE/BSE + early-signal calendar), source coverage
agents/        DomainAgentHarness (corporate_event profile), LLMRole, contained
               LangGraph engine, capabilities, canonical run ledger, releases
ontology/      relational champion, releases, competency, challenger, promotion, projections
decision/      conviction-blind sizing, risk (tighten-only overlay), compliance (India/US), eligibility
portfolio/     account-partitioned snapshots, completeness, analysis gate
execution/     durable-intent coordinator, reservations, kill state, protection supervisor, reconciliation
retrospective/ outcome linking + diagnosis
app/           settings, container, scheduler, api, cli, readiness
```

**Account-partitioned, not global:** `AccountPortfolioSnapshot` + `OwnerPortfolioCut`; kill is
account-generation-scoped; reservations are CAS-row-keyed `(account, cas_version)`. Do not
reintroduce global-stream shapes (ledger §4).

**Permanent parallel rule-based null** (deferred, WS-6): a pure rule-based benchmark runs live
forever; the LLM/semantic path earns capital only if it beats the null net of cost on
post-cutoff forward paper.

## Broker Integration

In-process `BrokerPort` ABC + `capabilities()` flags (`brokers/ports.py`) — **not** per-broker MCP
servers. Canonical `OrderRequest`. Adapters: `brokers/kite.py` (Zerodha NSE/BSE, no sandbox → sim
mandatory), `brokers/alpaca.py` (US cash account, PDT-exempt, identical-API paper), `brokers/fake.py`
(offline). Every broker write is preceded by a durable intent and gated by a current
`LiveAuthorityReceipt` (`policy/live_authority.py`, ADR-0001).

| Broker | Market | Library | Status |
|--------|--------|---------|--------|
| Zerodha Kite Connect | NSE/BSE | kiteconnect | live V1 primary. No sandbox → SimulatedBroker mandatory (deferred, WS-8). |
| Alpaca | NYSE/NASDAQ | alpaca-py | live V1 US sleeve. Cash account (PDT-exempt). |

## Sizing & Risk

Conviction-blind **fixed-fractional** sizing (`decision/sizing.py`, integer minor-units). Conviction
**only gates/ranks**, never scales size. Risk overlay is **tighten-only** — multiplier in (0,1] and/or
a veto (`research/models.py RiskOverlaySet`). Kill-switch: `ACTIVE/REDUCING/HALTED` with monotonic
generation fencing (`execution/kill_state.py`).

## Evaluation & promotion

Nothing goes live from narrative. Deferred science (WS-9): CPCV + Deflated Sharpe + post-cost sim +
post-model-cutoff forward-paper gate + frozen configs/prompt-hash/model-ID logging + a 90-day
campaign. Semantic features influence economics only via a governed, owner-approved
`DecisionFeatureActivation` with cooldown and auto-demotion on safety regression
(`ontology/promotion.py`, ADR-0010). Largest failure mode = believing false alpha.

## Data & State

TimescaleDB (OHLCV, deferred WS-3) + Postgres (events + LLM outputs) + Valkey (hot cache). The
**append-only event log is the source of truth**; Valkey is a rebuildable projection; broker custody
is reconciled into new append-only observations, never silently merged (ADR-0002). Fixed-point
`Decimal` for money/qty/price; binary float only inside stat arrays, converted at boundaries.

## Key Conventions

- **Python 3.11+**, `uv` for deps. One-command check: `make verify` (= `lint` + `typecheck` + `test`).
- **pytest**; markers: `integration` (local services), `contract` (broker contract), `live_readiness`
  (needs broker creds). Live/network tests are marked and **out of the default gate**.
- **`mypy --strict`** and **ruff** enforced. Type hints everywhere. Frozen Pydantic v2 models;
  `typing.Protocol` ports.
- **Async-first** for broker/DB/market-data/provider I/O; pure calculations synchronous.
- **Secrets**: from macOS Keychain / encrypted env; **never commit** keys, tokens, cookies, or
  account numbers.
- **TDD** red→green; one focused commit per task; PR per phase; **the user merges PRs** — do not
  push/PR/merge on assumptions.

## Compliance Constraints

- **SEBI (India)**: retail algo trading requires broker approval + tagging/static-IP via Zerodha;
  limit/protected order types only (never assume algo market orders are permitted). Broker is the
  gatekeeper (`decision/compliance.py evaluate_india`).
- **US PDT**: cash account avoids it. **FEMA/LRS**: US sleeve is cash-only, no shorting/derivatives
  as a legal invariant; TCS + Schedule FA disclosure apply (LRS/idle-FX accounting deferred, WS-7).
- Compliance gate is deterministic and gates every order before submission
  (`decision/compliance.py evaluate_us`).

## Working on this repo

Before implementing anything, read **`docs/README.md`** (doc map) and **`docs/V1-LEDGER.md`**
(scope/status + the WS-1…WS-11 work-list). Each deferred workstream is its own subproject:
**brainstorm → design spec → user review → writing-plans → subagent-driven execution →
whole-branch review → PR**. Work in an isolated worktree. Keep **`CONTEXT.md`** (the glossary) live —
update it inline as domain terms crystallize. ADRs (`docs/adr/`) are numbered through 0010; next is
**0011**. Treat `docs/trading-bot-research.md` as background corpus only — it predates the finalized
design and contradicts it in places.
