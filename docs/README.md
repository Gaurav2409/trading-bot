# Trading OS — Documentation Map

Start here. This indexes every doc on `main` and says what it's for. **The one source of truth for scope & status is [V1-LEDGER.md](V1-LEDGER.md).**

## Read-me-first order

1. **[V1-LEDGER.md](V1-LEDGER.md)** — canonical status of all 52 original V1 tasks (shipped / partial / deferred), the deliberate architecture divergences, and the nine dependency-ordered deferred workstreams (the planner's work-list). Machine-readable backing: [audit/v1-ledger-tasks.json](audit/v1-ledger-tasks.json).
2. The core invariant everywhere: **LLMs propose categorical labels; deterministic code disposes all numbers.** No executable number crosses the evidence seam; the relational champion is permanent; RDF/Neo4j are rebuildable projections; nothing goes live without a broker-scoped `LiveAuthorityReceipt`.

## Architecture Decision Records — `adr/`

The hard-to-reverse decisions. Next number is **0011**.

| ADR | Decision |
|-----|----------|
| [0001](adr/0001-evidence-gated-two-broker-live-v1.md) | Evidence-gated two-broker live V1 |
| [0002](adr/0002-separate-custody-observations-from-os-intention.md) | Separate broker custody observations from OS intention |
| [0003](adr/0003-separate-product-capability-from-semantic-activation.md) | Product/account capability ≠ semantic activation (independent gates) |
| [0004](adr/0004-split-ontology-schema-from-instance-validation.md) | Split ontology-schema validation from instance-snapshot validation |
| [0005](adr/0005-model-issuer-as-time-scoped-role.md) | Model issuer as a time-scoped role, not a subclass |
| [0006](adr/0006-own-the-domain-agent-harness-and-contain-langgraph.md) | Own the domain-agent harness; contain LangGraph inside a node |
| [0007](adr/0007-use-llm-role-as-the-only-provider-boundary.md) | `LLMRole` is the only provider boundary |
| [0008](adr/0008-sandbox-tools-as-node-scoped-capabilities-and-gateway-remote-mcp.md) | Node-scoped read-only tool capabilities; gateway remote MCP |
| [0009](adr/0009-keep-the-agent-run-ledger-canonical-over-framework-checkpoints.md) | Canonical run ledger over framework checkpoints |
| [0010](adr/0010-govern-agent-evolution-through-proposals-not-runtime-self-modification.md) | Govern agent evolution by proposals, not runtime self-modification |

## Design specs — `superpowers/specs/`

Approved designs. Each is the source of truth for its subsystem.

- [2026-07-22-live-v1-architecture-amendment.md](superpowers/specs/2026-07-22-live-v1-architecture-amendment.md) — the live-V1 safety-spine amendment (what re-scoped the original plan).
- [2026-07-21-trading-world-ontology-design.md](superpowers/specs/2026-07-21-trading-world-ontology-design.md) — the ontology / semantic-plane design.
- [2026-07-23-domain-agent-architecture.md](superpowers/specs/2026-07-23-domain-agent-architecture.md) — the LLM-backed domain-agent harness (profiles, seam, ledger).
- [2026-07-24-live-source-watcher-design.md](superpowers/specs/2026-07-24-live-source-watcher-design.md) — live NSE/BSE watcher + early-signal tier.

## Implementation plans — `superpowers/plans/`

Task-by-task plans. The two `2026-07-21-*` plans are the **original 52-task V1** — SUPERSEDED as executable, retained as detailed reference for the deferred tasks (the ledger maps their tasks to status).

- `2026-07-21-trading-os-v1-implementation.md` — original 37-task live-V1 (reference).
- `2026-07-21-trading-world-ontology-implementation.md` — original 15-task ontology (reference).
- `2026-07-22-nine-day-live-v1-implementation.md` — the live-V1 spine that shipped (PRs #1–#4).
- `2026-07-22-ontology-hardening-implementation.md` — ontology hardening P0–P2 (PRs #5–#8).
- `2026-07-23-domain-agent-p0-tracer.md` — domain-agent P0 tracer (PR #9); contains the P1-gap note.
- `2026-07-23-domain-agent-framework-spikes.md` — remote MCP / Pydantic AI / Deep Agents / DSPy spikes (ready, unexecuted).
- `2026-07-24-live-source-watcher.md` — live watcher (PR #10).

## Research — `research/`

- `11`–`14` — trading-world ontology + MoA reviews + live-domain opportunity audit + portfolio-family synthesis.
- `17` — domain-agent harness evaluation. `18` — per-domain source/tool/skill profiles. `19` — India event-source catalog.
- `raw/agents/` — raw harness synthesis, Hermes-MoA assessments, source captures (provenance).
- `../trading-bot-research.md` — original master MoA corpus (background; predates the finalized design).

## Operations & runbooks

- [operations/domain-agent-shadow-runbook.md](operations/domain-agent-shadow-runbook.md) — interpreting shadow-run outcomes.
- [runbooks/live-v1.md](runbooks/live-v1.md), [runbooks/incidents.md](runbooks/incidents.md), [runbooks/day-10-policy-change.md](runbooks/day-10-policy-change.md).

## Handoffs — `handoffs/`

- [2026-07-22-domain-agent-architecture-planning-handoff.md](handoffs/2026-07-22-domain-agent-architecture-planning-handoff.md).

## Process for new work

Every deferred workstream (ledger §5) is its own subproject: **brainstorm → design spec → user review → writing-plans → subagent-driven execution → whole-branch review → PR (user merges).** Isolated worktree; TDD; offline-deterministic default gate; live/network tests `@pytest.mark.integration` out of the gate. Keep [../CONTEXT.md](../CONTEXT.md) (the glossary) live — update it inline as terms crystallize.

> **Known stale:** the repo-root `CLAUDE.md` on `main` is an out-of-date 12-agent/3-market version that contradicts the shipped design, and references a `research/RESEARCH-STATE.md` not present on main. Treat the specs/ADRs/ledger above as authoritative until `CLAUDE.md` is refreshed.
