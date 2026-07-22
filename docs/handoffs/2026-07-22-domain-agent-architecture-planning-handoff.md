# Handoff — Plan the LLM-Backed Expert Domain Agent Architecture

**Type:** Planning + web-research handoff. **Produce a design spec, an implementation plan, and
ADRs. Do NOT write implementation code.** A separate handoff will execute the approved plan.

**Repository:** `/Users/I321170/Documents/Projects/trading-bot`
**Base branch:** `main` (the merged nine-day live-V1 slice + ontology hardening PR #5).

---

## 1. Why this exists

The nine-day V1 built the **safety and contract spine** of the Trading OS but deliberately left the
research **intelligence layer stubbed**. Today a deterministic fake sits behind the research port;
there are no LLM-backed agents, no LLM client, no provider router, no running harness, and the
scheduler only *describes* jobs. Your job is to design — not yet build — the architecture that fills
that gap: a set of **expert domain agents**, each with a purpose-built harness, domain-specific
tools, and skills, feeding the existing typed non-executable evidence seam.

This is explicitly the "grow evidence depth" work the architecture always intended to be additive.
It must not weaken any existing safety invariant.

## 2. Read first (in order)

1. `CONTEXT.md` — Trading World glossary (Observation, Claim, Admitted Assertion, Evidence Packet,
   Instrument Hypothesis, Instrument Belief State, Semantic Snapshot).
2. `docs/superpowers/specs/2026-07-22-live-v1-architecture-amendment.md` — controlling spec; note §3
   non-negotiable boundaries, §8 discovery/research coverage, §12 retrospective loop, §16
   first-iteration-vs-final.
3. `docs/research/13-live-domain-opportunity-audit.md` — the cross-domain opportunity/trap matrix and
   the domain list; sentiment-is-risk-only rule; data-feed limitations as policy inputs.
4. `docs/research/16-core-ttl-schema-audit.md` — ontology status and the P1 modular reasoning plan
   the agents will eventually consume.
5. `docs/adr/0001`–`0005` — evidence-gated live; custody vs OS intention; product vs semantic
   activation; split schema/instance validation; time-scoped issuer role.
6. Existing code seam (do not change it without an ADR):
   - `src/trading_os/research/models.py` — `EvidenceDomain` (10 domains), `EvidencePacket`,
     `DecisionFeatureSet`, `RiskOverlaySet`.
   - `src/trading_os/research/orchestrator.py` — `ResearchQuestion`, `ResearchAgentPort` (Protocol
     with `async investigate(question) -> EvidencePacket | None`), `admit_packet()`,
     `ResearchOrchestrator`.
   - `src/trading_os/research/watchers.py` — `SourceRecord`, `SourceWatcher` Protocol.

## 3. Required skills and method

- `superpowers:brainstorming` FIRST — this is a "let's design X" task; do not enter planning before
  brainstorming.
- `superpowers:using-git-worktrees` if you produce anything on disk (docs go on a `codex/…` branch).
- `mattpocock-skills:codebase-design` and `design-an-interface` for the `LLMRole` / agent / tool
  boundaries (they have multiple credible shapes — this is exactly their trigger).
- `mattpocock-skills:domain-modeling` — keep `CONTEXT.md` authoritative; propose new terms there.
- Web research: use the **`web-fetch-guardrail`** skill's `fetch-sources` for ALL fetching/search
  (never `hermes chat -s browser-harness`). Store raw sources under `docs/research/raw/agents/` and
  synthesize into a numbered `docs/research/NN-*.md` doc. Cite every external claim.
- `mattpocock-skills:to-tickets` at the end to produce a dependency-ordered, tracer-bullet task list.
- Get explicit **granularity approval** before writing ticket files. Produce **no implementation
  code**.

## 4. Web research mandate (broad)

Research and synthesize, with citations, into `docs/research/`:

### 4a. Agent harness architectures (evaluate; do not presume a winner)
Evaluate at least these against our constraints (§5), with an explicit trade-off table and a
recommendation:
- **Nous Research `hermes-agent`** — https://github.com/nousresearch/hermes-agent (the user's cited
  reference; study its tool-calling loop, harness shape, and skill model).
- OpenAI Agents SDK / Assistants tool-use loop; Anthropic tool-use + MCP; LangGraph; DSPy; and any
  current strong open harness you find.
Assess each on: provider-swappability, structured/typed output enforcement, tool-call safety,
prompt-injection isolation, determinism/replayability, cost/latency control, offline testability,
and fit with our append-only event ledger. **Hermes is a reference, not a mandate.**

### 4b. Per-domain tools, data sources, and skills — for ALL 10 `EvidenceDomain`s
For each of `technical, fundamental, corporate_event, sentiment, macro, economic_relationship,
governance, liquidity, portfolio, market_mechanics`, research and specify:
- authoritative primary data sources/APIs (prefer official NSE/BSE, SEC EDGAR/XBRL, exchange feeds;
  note entitlement limits like Alpaca IEX-vs-SIP already recorded in doc 13);
- the domain-specific tools/skills the agent needs (calculators, filing parsers, calendar lookups,
  relationship-graph queries, liquidity/microstructure probes) — as typed tool interfaces, not code;
- what a good `EvidencePacket.assessment` + `support`/`contradictions`/`missing` looks like for that
  domain, and its `eligibility_effect` semantics;
- domain-specific failure/traps from doc 13 (e.g. corporate-action-distorted bars, syndicated-copy
  sentiment overcounting, stale macro vintages) and how the harness guards them.

## 5. Non-negotiable constraints the design MUST honor

These are constitutional; a design that breaks any of them is rejected:

1. **No number crosses the seam.** Agents emit only the typed `EvidencePacket` /
   `DecisionFeatureSet` — never quantity, price, target weight/position, order, or executable
   command. `RiskOverlaySet` may only tighten or veto.
2. **Admission is mandatory.** Every packet passes `admit_packet()` (instrument/domain/cutoff match,
   citation-scope subset, sentiment-risk-only). Agents cite only `ResearchQuestion.source_record_ids`.
3. **Provider-swappable.** A single `LLMRole`-style interface: `invoke(role, prompt, schema) ->
   structured`. Model/provider is config, not code. Cheap models gather; a synthesis/judge tier
   (MoA-style) may combine — but still emits only typed evidence.
4. **Relational champion is permanent.** LLM/agent/graph failure produces an explicit *missing*
   packet and NEVER blocks relational operation. Semantic features influence economics only via an
   effective `DecisionFeatureActivation`.
5. **Cutoff & temporal safety.** No future-data leakage; packets respect the decision cutoff and the
   `data_snapshot_id`. Reproducible from immutable versions.
6. **Deny-by-default, injection-isolated.** Untrusted source text can never escalate to tool calls
   with side effects; the agent path has no order/execution authority.
7. **Offline-testable & deterministic in tests.** A fake/replay agent must remain the test default;
   real agents must be exercisable against recorded fixtures without network or credentials.
8. **Cost/observability.** Structured logging of model id, prompt hash, tokens, latency per invoke;
   frozen configs for evaluation.

## 6. Deliverables

1. **Web-research synthesis doc(s)** in `docs/research/` (harness evaluation + per-domain sources/
   tools), raw sources under `docs/research/raw/agents/`.
2. **Design spec** `docs/superpowers/specs/<date>-domain-agent-architecture.md`: the `LLMRole`
   interface, the agent/tool/skill model, the harness recommendation with rationale, per-domain agent
   profiles, MoA-synthesis stance, prompt-injection isolation model, eval/calibration approach, and
   how it all plugs into the existing `ResearchAgentPort` + scheduler without changing the seam.
3. **ADRs** for the genuinely hard-to-reverse decisions, e.g.:
   - choice of base harness (build-vs-adopt);
   - the `LLMRole` provider-abstraction boundary;
   - MoA synthesis vs single-model per domain;
   - how domain tools are sandboxed from execution authority.
4. **Implementation plan** `docs/superpowers/plans/<date>-domain-agent-implementation.md` — staged
   (P0 interface + one tracer-bullet domain agent behind the port; P1 remaining domains + MoA; P2
   calibration/promotion), each task tracer-bullet and TDD-shaped, with a tracer-bullet first agent
   identified.
5. A short **risk register**: cost blowup, injection, false-alpha belief, provider lock-in, data
   entitlement gaps, latency vs decision-window fit.

## 7. Explicitly out of scope for this handoff

- Writing any implementation code (interfaces, agents, tools).
- Changing the existing research seam, ADRs 0001–0005, or the relational champion.
- Enabling any live economic influence from agents (that remains gated by `DecisionFeatureActivation`
  and is a much later, separately-evaluated step).

## 8. Definition of done (for the plan, not the build)

- All 8 constraints in §5 are explicitly addressed in the design.
- Harness recommendation is justified by the §4a evaluation with a trade-off table, not asserted.
- All 10 domains have a research-backed source/tool/skill profile.
- ADRs cover each hard-to-reverse decision; plan is dependency-ordered and tracer-bullet.
- A first tracer-bullet agent is identified for the execution handoff.
- Every external claim is cited; raw sources are captured for provenance.
