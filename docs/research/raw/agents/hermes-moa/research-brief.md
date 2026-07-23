# Domain-agent harness research brief

Date: 2026-07-22

## Objective

Recommend how much existing agent-harness technology to adopt for a governed public-equity research layer. The result must preserve the repository's existing compatibility seam and safety architecture. This is a design decision, not a request to implement code.

## Approved constraints

1. Preserve `ResearchAgentPort.investigate(question) -> EvidencePacket | None`. Expected provider, tool, timeout, and validation failures become typed missing evidence packets; `None` is reserved for catastrophic infrastructure failure and must remain observable.
2. `corporate_event` is the first tracer domain. P0 uses recorded SEC 8-K fixtures plus NSE/BSE announcement adapters.
3. Agents never browse or fetch directly. `SourceWatcher` adapters ingest, normalize, and seal immutable `SourceRecord`s. Agents only receive read-only tools over a scoped frozen snapshot.
4. Required official sources are derived from effective-dated applicability. An NSE-only instrument is not degraded for lacking BSE; dual-listed issuers expect both; SEC is required only when issuer filing status makes it applicable.
5. One applicable official channel missing means degraded but usable. All mandatory primary channels missing means typed insufficient/missing evidence with no positive influence. Materially conflicting official channels preserve the contradiction and cannot positively influence the instrument until deterministic resolution or correction.
6. Source coverage is governed desired/observed state. Owner-approved immutable policy releases define desired state; receipts/statuses record observed state. Monitors may propose but cannot self-promote, weaken policy, or trade. New sources remain experimental and shadow-only until approved.
7. The entire agent layer follows the same desired/observed control plane. One immutable `AgentProfileRelease` references smaller versioned definitions: prompts, tool capabilities, source coverage, output schema, LLM routing, budgets, failure policy, evaluation policy, and trajectory.
8. There is one generic `DomainAgentHarness`, not ten domain-specific harnesses. Ten evidence domains differ through profiles, source policies, skills, read-only tools, and output constraints.
9. A profile references an immutable `TrajectoryRelease`. The harness is a bounded typed trajectory engine supporting registered node types such as agent loop, deterministic transform, schema validation, branch, fan-out/join, judge, admission, and explicit missing. Every node has typed I/O and hard iteration/token/cost/timeout/failure limits with replayable events.
10. Numeric intermediates may exist inside deterministic tools or the harness. The external evidence seam is categorical and non-executable: no prices, quantities, targets, returns, conviction multipliers, or orders.
11. Every tool is registered and versioned with typed I/O, frozen-snapshot scope, pure/read-only behavior, limits, a fixture adapter, and a profile allowlist. No network, filesystem mutation, policy mutation, or arbitrary execution is available to an agent. The harness owns logging and the event ledger.
12. The relational retrieval champion remains permanently available and continues when agent research is missing, degraded, contradictory, or unavailable.
13. Tests must be offline and deterministic. Cost, latency, token use, model/provider identity, tool calls, releases, source snapshot, and failure outcomes must be observable.

## Candidates to assess

- Hermes Agent
- OpenAI Agents SDK/current Responses-era agent APIs
- Anthropic Messages/tool use and MCP integration
- LangGraph
- LangChain Deep Agents
- Pydantic AI
- DSPy
- MCP as a protocol boundary
- A thin repository-owned harness with narrowly scoped provider adapters

## Updated user direction

As of 2026-07-23, do not dispose of LangGraph, DSPy, or remote MCP merely by deferring them. Evaluate each as an active part of the design and state the bounded role and controls that would make adoption compatible. Also evaluate LangChain Deep Agents as a candidate harness or pattern source. A negative recommendation is allowed only when supported by a concrete constitutional conflict that cannot be contained behind an internal boundary.

## Decision standard

Distinguish between adopting a runtime, borrowing patterns, using a library behind an internal port, and rejecting a component from the constitutional core. Prefer the smallest dependency surface that satisfies typed trajectories, strict capability isolation, replay, provider substitution, deterministic fixtures, observability, and compatibility with the existing evidence/admission seam.
