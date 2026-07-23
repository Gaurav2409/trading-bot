# Trading OS — Repository Guide

## Repository map

```text
CONTEXT.md                         Canonical project glossary
docs/
  README.md                        Documentation map and reading order
  V1-LEDGER.md                     Canonical V1 scope, status, and workstreams
  audit/v1-ledger-tasks.json       Machine-readable task status
  adr/                             Accepted architecture decisions
  superpowers/specs/               Approved subsystem designs
  superpowers/plans/               Current plans and superseded references
  research/                        Evidence and design research
src/trading_os/
  agents/                          Governed domain-agent harness
  app/                             Configuration, composition, scheduling, API/CLI
  brokers/                         Normalized broker models and adapters
  decision/                        Deterministic eligibility, sizing, risk, compliance
  discovery/                       Deterministic opportunity discovery
  execution/                       Intents, kill state, reservations, protection
  identity/                        Account ownership and authority
  kernel/                          Shared IDs, values, and operational events
  ledger/                          Append-only event persistence and replay
  market_data/                     Market-data models, validation, and snapshots
  ontology/                        Semantic releases and rebuildable projections
  policy/                          Immutable policy and live-authority controls
  portfolio/                       Account-partitioned projections and snapshots
  research/                        Evidence models, watchers, and research seam
  retrospective/                   Outcome linking and diagnosis
  tradability/                     Account-specific tradability assessment
tests/
  unit/                            Offline deterministic unit tests
  contract/                        Shared adapter behavior contracts
  integration/                     Local-service integration tests
  live_readiness/                  Explicit credential/readiness probes
  replay/                          Deterministic replay tests
migrations/                        Alembic database migrations
ontology/                          RDF vocabulary, shapes, mappings, and policies
config/                            Versioned runtime policy configuration
deploy/                            Local and production deployment assets
web/                               Operator-facing web assets
```

## Canonical rules

1. Direct user instruction wins. Then follow `docs/V1-LEDGER.md`, approved
   specifications, accepted ADRs, `CONTEXT.md`, the current implementation plan,
   and finally research or superseded plans, in that order.
2. The purpose of reasoning is not to defend conclusions or merely maintain
   consistency. Maximize contact with reality and update conclusions in light of
   evidence.
3. Do not restore superseded designs. Preserve the deliberate divergences in
   `docs/V1-LEDGER.md` §4.
4. LLM output is categorical and non-executable. Deterministic code owns every
   price, quantity, weight, target, and order.
5. Preserve Brokerage Account partitions, account-generation kill state,
   CAS-row-keyed reservations, immutable history, provenance, and fail-closed
   behavior.
6. Use fixed-point `Decimal` for money, quantity, and price. Binary float is
   confined to statistical arrays and converted explicitly at their seams.
7. Use Python 3.11+, frozen Pydantic v2 models, `typing.Protocol`, strict mypy,
   Ruff, pytest, and TDD red → green.
8. Default-gate tests are offline and deterministic. Live or network tests use
   `@pytest.mark.integration` and stay outside that gate.
9. Keep `CONTEXT.md` a live glossary only. Record a new ADR only for a decision
   that is hard to reverse, surprising without context, and a genuine trade-off.
10. Every deferred workstream follows: isolated worktree → brainstorm → design
    spec → user review → implementation plan → execution approval → TDD with
    review gates → whole-branch review → PR. The user merges; never push, open a
    PR, or merge on assumptions.
