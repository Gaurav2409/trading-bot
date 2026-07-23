# Trading OS — Roadmap & Status Tracker

**Purpose:** the single authoritative entry point for what is built, what is pending, and where every governing decision lives. Hand this file to a planning agent to continue the work. It points to the ADRs, specs, and plans that are the real source of truth — it does not duplicate them.

**Last updated:** 2026-07-24 (after PR #10, merge `ecf4c36`).

**Read-me-first for any planner:**
- Core invariant everywhere: **LLMs propose categorical labels; deterministic code disposes all numbers.** No executable number crosses the evidence seam; the relational champion is permanent; RDF/Neo4j are rebuildable projections; nothing goes live without a broker-scoped `LiveAuthorityReceipt`.
- Where locked decisions live: the finalized **specs + ADRs + plans** in §3 are the operative source of truth. The root `CLAUDE.md` references a `docs/research/RESEARCH-STATE.md` (decisions D1–D30) as "source of truth", but **that file is not committed to `main`** — treat the specs/ADRs/plans below as authoritative and reconcile any D-numbered reference against them. (Flagged for the planner: either restore RESEARCH-STATE.md or update CLAUDE.md to drop the stale pointer.)

---

## 1. Shipped (merged to `main`)

| Workstream | What | Governing docs | PRs |
|---|---|---|---|
| Live V1 safety spine | Kernel, event ledger, brokers (Kite/Alpaca read+write), portfolio, sizing/risk, compliance, execution, kill states, reconciliation, operator console, two-broker T0 readiness | spec `2026-07-22-live-v1-architecture-amendment.md`; plan `2026-07-22-nine-day-live-v1-implementation.md`; ADRs 0001–0003 | #1–#4 |
| Ontology hardening P0–P2 | Split schema/instance validation, modular reasoning ontology + SHACL safety shapes, prove-usefulness layer (competency, challenger vs relational champion, governed promotion/demotion) | plan `2026-07-22-ontology-hardening-implementation.md`; ADRs 0004–0005 | #5–#8 |
| Domain-agent P0 tracer | One governed `DomainAgentHarness` behind the unchanged `ResearchAgentPort`; `corporate_event` profile: gather→normalize→judge→reconcile→categorical-seam→admission; LangGraph contained; canonical run ledger; closed-vocabulary seam; shadow-only | spec `2026-07-23-domain-agent-architecture.md`; plan `2026-07-23-domain-agent-p0-tracer.md`; ADRs 0006–0010 | #9 |
| Live NSE/BSE SourceWatcher | Tier-1 official announcement connector (evidence-bearing) + Tier-2 early-signal calendar (`WatchScheduled`, never evidence); `SourceFetchPort` (fixture + integration-tagged HTTP); credible-source catalog | spec `2026-07-24-live-source-watcher-design.md`; plan `2026-07-24-live-source-watcher.md` | #10 |

## 2. Pending / next (hand these to the planner)

Ordered roughly by dependency and value. Each names its governing doc and current status.

### 2a. `fundamental` domain profile — DESIGN NEEDED
Read the numbers *inside* a results/filing (revenue, margin, YoY, balance-sheet items) as a **categorical** assessment — reported-vs-derived distinction, period/vintage, missing fields — never emitting a target, price, or size.
- **Why now:** a results announcement is both a `corporate_event` (built) and a `fundamental` read (not built). This is the other half of the Tanla case.
- **Governing docs:** architecture spec §18 (profile table row `fundamental`) + [`docs/research/18-domain-agent-source-tool-profiles.md`](../research/18-domain-agent-source-tool-profiles.md) (starting source classes, tools, good-packet criteria, fail-closed traps). One of the nine P1 profiles.
- **Constraints inherited:** same generic harness (a profile, not a new harness); categorical output only; every citation ⊆ `ResearchQuestion.source_record_ids`; SEC/XBRL + exchange-filing spans as sources.
- **Status:** deferred at P0; recorded in the P0 plan's "P1 gaps identified after P0" note. **No spec yet — start with brainstorming → design → plan.**

### 2b. Live-wire aggregator / wire early-signal sources — DESIGN NEEDED
Onboard the catalog's Tier-2/3 sources (Trendlyne, Screener, Tickertape, MoneyControl calendars; PTI/Reuters/Bloomberg wires) as *additional early-signal* inputs — `WatchScheduled` intents only, never evidence.
- **Governing docs:** live-source-watcher spec `2026-07-24-live-source-watcher-design.md` §8 + catalog [`docs/research/19-india-event-source-catalog.md`](../research/19-india-event-source-catalog.md) (each source already tiered with endpoint, authority, latency, entitlement, parser difficulty).
- **Constraints inherited:** governed onboarding per architecture spec §14.3 (EXPERIMENTAL → shadow → owner-approved `SourceCoveragePolicyRelease`); the `SourceFetchPort` + `CalendarWatcher` + tier-boundary types already exist and must be reused, not widened; entitlement/legal per source; no secrets committed.
- **Status:** catalog complete; official announcements + board-meeting calendar already wired. Aggregators/wires are ranked candidates, not yet wired. **Reuses existing seams — likely a plan directly, light design.**

### 2c. Domain-agent framework spikes — PLAN READY (not executed)
Evaluate remote MCP, Pydantic AI, Deep Agents, DSPy against the completed P0 seams; passing ones become replaceable adapters, failing ones stay pattern sources. No framework gets source/policy/ledger/activation authority.
- **Governing doc:** plan `2026-07-23-domain-agent-framework-spikes.md` (task-by-task, ready to execute). Prereq (P0 Tasks 1–10) is **met**.
- **Status:** ready to execute when prioritized.

### 2d. Remaining eight domain profiles + graphical workbench — DESIGN NEEDED (P1 subprojects)
`technical`, `macro`, `economic_relationship`, `governance`, `liquidity`, `portfolio`, `market_mechanics`, `sentiment`, plus the non-technical operator workbench.
- **Governing docs:** architecture spec §18 (profile table) + §21 (workbench) + `docs/research/18-domain-agent-source-tool-profiles.md`. Each profile is its own spec→plan→implement cycle on the same harness.
- **Status:** deferred; each needs its own design.

### 2e. Live testing (paper-first) — SEPARATE GATE
Exercise the merged spine + live watcher on paper/small-disposable balances. Governed by the live-authority + evaluation gates already built (post-cutoff forward-paper, permanent rule-based null benchmark). **This is an operational activity, not new code** — see the operator runbook `docs/operations/domain-agent-shadow-runbook.md`.

## 3. Governing documents index

**ADRs** (`docs/adr/`): 0001 evidence-gated two-broker live · 0002 custody vs OS intention · 0003 product vs semantic activation · 0004 split ontology schema/instance validation · 0005 time-scoped IssuerRole · 0006 own the harness / contain LangGraph · 0007 LLMRole as the only provider boundary · 0008 node-scoped tool capabilities / gateway remote MCP · 0009 canonical run ledger over framework checkpoints · 0010 govern agent evolution by proposals, not runtime self-modification.

**Specs** (`docs/superpowers/specs/`): live-v1 architecture amendment · trading-world ontology · domain-agent architecture · live-source-watcher.

**Plans** (`docs/superpowers/plans/`): nine-day live-v1 · ontology-hardening · domain-agent P0 tracer · domain-agent framework spikes · live-source-watcher. (The two `2026-07-21` plans are SUPERSEDED.)

**Research** (`docs/research/`): `RESEARCH-STATE.md` (locked decisions) · `17-domain-agent-harness-evaluation.md` · `18-domain-agent-source-tool-profiles.md` · `19-india-event-source-catalog.md`.

## 4. Process for the planner

Every new subproject follows: **brainstorming → design spec (`docs/superpowers/specs/`) → user review → writing-plans (`docs/superpowers/plans/`) → subagent-driven execution → whole-branch review → PR (user merges).** Work in an isolated worktree. TDD, one focused commit per task, offline-deterministic tests in the default gate, live/network tests `@pytest.mark.integration` out of the gate. Do not push/PR/merge on assumptions — the user merges PRs.

## 5. Change log
- 2026-07-24: Tracker created. Consolidates the P0-plan P1-gap note, architecture-spec rollout, and framework-spikes plan into one entry point. Pending items 2a (fundamental profile) and 2b (aggregator/wire early-signal onboarding) flagged for immediate handoff.
