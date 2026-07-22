# Domain-agent harness research synthesis

Date: 2026-07-23

Inputs:

- Hermes MoA `deep-research` assessment over a sanitized design brief and public primary sources
- Independent primary-source assessment
- Approved compatibility, source-governance, profile, trajectory, capability, evidence-seam, and workbench constraints

## Resolved recommendation

Build one repository-owned `DomainAgentHarness`. Use selected ecosystem components inside explicit containment boundaries:

1. **LangGraph executes immutable trajectories.** A project-owned compiler validates each `TrajectoryRelease` and builds a graph of registered, typed, bounded nodes. LangGraph checkpoints are recovery state; the repository's append-only run ledger is canonical business/audit state.
2. **An `AgenticLoopNode` has a replaceable loop strategy.** The default strategy is the smallest provider-neutral tool loop. LangChain Deep Agents receives a bounded spike as another strategy, not another harness. It starts with filesystem, execution, REPL, persistent memory, automatic general-purpose subagents, direct MCP discovery, and mutation-capable middleware disabled.
3. **Pydantic AI and direct vendor SDKs sit behind `LLMRole`.** The spike compares lower-level Pydantic AI model/provider abstractions with narrow OpenAI and Anthropic adapters. Provider capability differences fail closed; vendor tracing and hosted/server tools are not constitutional controls.
4. **DSPy is active from P0, offline.** Typed signatures and optimizers propose prompt/module candidates against recorded SEC/NSE/BSE fixtures and explicit abstention, entailment, coverage, cutoff, contradiction, schema, cost, and latency metrics. A candidate cannot activate itself; it must become an evaluated, owner-approved immutable release.
5. **Remote MCP is active from P0 through `MCPCapabilityAdapter`.** The host—not the model—selects a pinned server and frozen tool/schema release. The adapter enforces audience-bound auth, network allowlists, local typed validation, frozen-snapshot scope, fixture replay, timeouts, result limits, and deny-by-default permissions. Remote annotations and runtime tool-list changes never grant authority.
6. **Hermes, OpenAI Agents SDK, and Deep Agents are pattern/runtime sources, not policy authorities.** Their registries, lifecycle hooks, provider routing, permission patterns, typed outputs, and observability are useful. Their broad tools, state, memory, tracing destinations, and autonomous behaviors remain outside the constitutional core.

## Agreement between Hermes MoA and independent research

Both assessments agree on the following:

- the repository-owned thin harness remains the core;
- LangGraph can be adopted behind `TrajectoryEngine` if its checkpointer does not replace the canonical ledger;
- Pydantic AI is the strongest provider-normalization and deterministic-test candidate behind `LLMRole`;
- DSPy belongs in an offline, release-governed evaluation/optimization path;
- remote MCP is viable only as a bounded internal transport behind the capability registry;
- hosted web/fetch/code tools, arbitrary shell/filesystem mutation, persistent agent memory, direct policy changes, and trading actions remain prohibited;
- the relational retrieval champion remains available regardless of agent outcome.

## Material disagreement and resolution

### LangGraph API shape

Hermes MoA named the LangGraph Functional API because its task-result replay is attractive. The independent assessment prefers the Graph API because a `TrajectoryRelease` is explicitly a visual, immutable node/edge definition with deterministic and agentic nodes.

Resolution: use a project-owned `TrajectoryCompiler` targeting LangGraph's graph runtime. Functional tasks may be used inside registered node implementations where replay semantics help, but Python control flow never becomes the source-of-truth trajectory definition.

### Deep Agents

Hermes MoA recommends borrowing patterns and rejecting the runtime. The independent assessment sees enough configurable restriction to justify a spike as an `AgenticLoopNode` strategy.

Resolution: do not select Deep Agents as the default runtime yet. Run a pass/fail spike. It is admissible only if every child loop receives an explicit capability set, mutation-capable defaults are absent from the model-visible surface and execution backend, outputs remain typed, budgets are enforced by the outer harness, and offline replay is deterministic. Failure of any gate reduces it to a pattern source.

### Trace ownership

Hermes highlights that OpenAI tracing is enabled by default and Deep Agents commonly uses LangSmith. The project requires one canonical, redactable event record.

Resolution: framework tracing may export only from a project-owned redaction/export layer and is never the sole record. P0 defaults external trace export off; internal OpenTelemetry correlation IDs may link framework spans to canonical run events.

## Present-tense roles

| Component | P0 role | Cannot own |
|---|---|---|
| Repository harness | Profile binding, budgets, outcomes, ledger, compatibility seam | Source or policy self-promotion |
| LangGraph | Typed graph execution, checkpoints, interrupts, bounded fan-out/join | Business truth, admission, release activation |
| Deep Agents | Candidate implementation for bounded agentic loop nodes | Harness policy, unrestricted tools, persistent memory |
| Pydantic AI / vendor SDKs | `LLMRole` implementations and deterministic fixture models | Trajectory, capability authorization, admission |
| DSPy | Offline evaluation and prompt/module proposal | Runtime self-tuning or activation |
| Remote MCP | Transport for pre-approved read-only capabilities | Discovery-based authorization or direct agent networking |
| SourceWatcher | Official-source ingestion and immutable sealing | Positive evidence/admission decisions |
| Admission layer | Final compatibility and non-executable evidence validation | Fetching or agent orchestration |

## Spike gates before final dependency selection

1. Compile one corporate-event gather → deterministic normalize → judge → admission trajectory to LangGraph and reproduce it offline.
2. Crash and resume at each node boundary without refetching, changing releases, duplicating calls, or disagreeing with the canonical ledger.
3. Run OpenAI, Anthropic, and Pydantic test/fake adapters through one `LLMRole` contract suite.
4. Run a stripped Deep Agents worker and prove that main and child agents can see only injected read-only capability proxies.
5. Connect one recorded remote MCP fixture server through `MCPCapabilityAdapter`; reject server identity drift, schema drift, `listChanged`, unapproved tools, oversized results, and token pass-through.
6. Use DSPy against the recorded event fixtures and show improvement on held-out cases without reducing abstention or contradiction safety.
7. Demonstrate categorical output rejection for every prohibited executable field.
8. Show that missing, degraded, contradictory, timeout, budget, and catastrophic outcomes preserve the existing `EvidencePacket | None` compatibility contract.

## Primary sources

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview), [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), and [functional API](https://docs.langchain.com/oss/python/langgraph/functional-api)
- [LangChain Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview), [permissions](https://docs.langchain.com/oss/python/deepagents/permissions), [backends](https://docs.langchain.com/oss/python/deepagents/backends), and [subagents](https://docs.langchain.com/oss/python/deepagents/subagents)
- [Pydantic AI models](https://pydantic.dev/docs/ai/models/overview/) and [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/)
- [DSPy](https://dspy.ai/)
- [MCP tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) and [authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OpenAI Agents SDK guardrails](https://openai.github.io/openai-agents-python/guardrails/) and [tracing](https://openai.github.io/openai-agents-python/tracing/)
- [Anthropic tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Hermes Agent architecture](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/architecture.md)
