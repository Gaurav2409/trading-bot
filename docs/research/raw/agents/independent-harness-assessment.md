# Independent agent-harness assessment

Date: 2026-07-22

Status: independent primary-source assessment; Hermes MoA assessment pending explicit external-corpus approval.

## Executive conclusion

The constitutional core should be a small repository-owned `DomainAgentHarness` and typed `TrajectoryEngine`. Existing frameworks should be used selectively behind narrow ports or as pattern libraries, not allowed to become the authority for source access, policy, admission, replay, or evidence state.

Recommended disposition:

- **Own:** profile resolution, typed trajectory validation/execution, capability authorization, frozen-snapshot binding, budgets, append-only run events, typed missing outcomes, and the final `EvidencePacket` compatibility adapter.
- **Spike behind `LLMRole`:** Pydantic AI's lower-level model/provider abstractions because they are explicitly vendor-agnostic, expose model capability profiles, support structured validation, and include `TestModel`/`FunctionModel` for deterministic tests. Do not automatically adopt its agent loop, tools, durable execution, or state as authorities.
- **Keep direct provider adapters available:** OpenAI Responses/Agents-era APIs and Anthropic Messages/tool use are useful provider integrations, but neither vendor runtime should define the domain harness.
- **Borrow, do not embed in P0:** Hermes' shared core, provider resolver, tool registry, profile isolation, iteration budgets, and observable tool-loop patterns. Its broad personal-agent state and mutation surfaces conflict with this system's deny-by-default research boundary.
- **Adopt with containment:** compile immutable `TrajectoryRelease`s to LangGraph for node/edge execution, bounded fan-out, checkpoints, interrupts, and recovery. The repository's append-only run ledger remains canonical; LangGraph checkpoint state is recoverable execution state, never business truth.
- **Adopt offline:** use DSPy signatures and optimizers in the evaluation pipeline for prompt/module candidates. Results can propose a new immutable prompt or evaluation release but cannot self-promote.
- **Adopt through a gateway:** permit approved remote MCP servers only through `MCPCapabilityAdapter` behind the internal capability registry. Agents never discover or connect to arbitrary servers directly; all schemas, identities, auth scopes, outputs, and fixture behavior are locally governed.
- **Spike as a loop strategy:** evaluate LangChain Deep Agents inside a bounded `AgenticLoopNode`, with its filesystem, execution, persistent memory, automatic general-purpose subagent, and broad middleware defaults removed. This remains one `DomainAgentHarness`; Deep Agents would be a replaceable loop implementation, not another policy authority.

This recommendation is an inference from the official capabilities below, not a claim made by any framework vendor.

## Evidence and fit

### Hermes Agent

Hermes demonstrates the value of one agent core across entry points, provider resolution, centralized tool registration, iteration limits, callbacks, and profile isolation. Its official architecture also shows why it is too broad for the constitutional core: the runtime includes persistent memory, session mutation, file and terminal tools, plugins, MCP, delegation, compression, and direct agent-level state tools. Some tools bypass normal registry dispatch, and the tool runtime includes permanent command allowlisting. Those are legitimate personal-agent features but are the wrong default authority boundary for evidence production.

Recommendation: borrow architectural patterns and use Hermes MoA as an external research method; do not embed `AIAgent` as `DomainAgentHarness`.

Sources: [Hermes architecture](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/architecture.md), [agent loop](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/agent-loop.md), [provider runtime](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/provider-runtime.md), [tools runtime](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/tools-runtime.md).

### OpenAI Agents SDK

The SDK supports typed `output_type`, tools, handoffs, lifecycle hooks, models, sessions, tracing, and guardrails. It can use non-OpenAI providers, but its own documentation warns that structured output, tool calling, usage reporting, and Responses-specific behavior vary across provider backends. Tool guardrails cover function tools but not hosted tools or handoffs. Tracing is enabled by default and may capture sensitive model and function input/output unless configured otherwise.

Recommendation: use OpenAI's SDK or Responses adapter only behind `LLMRole`, with hosted tools disabled and project-owned event/cost records remaining canonical. Do not make SDK guardrails the sole security boundary.

Sources: [agents and structured output](https://openai.github.io/openai-agents-python/agents/), [models and non-OpenAI limitations](https://openai.github.io/openai-agents-python/models/), [guardrail scope](https://openai.github.io/openai-agents-python/guardrails/), [tracing and sensitive data](https://openai.github.io/openai-agents-python/tracing/).

### Anthropic Messages and tool use

Anthropic cleanly distinguishes client tools, which the application executes, from server tools executed on Anthropic infrastructure. Custom tools have JSON input schemas and may use strict schema conformance. This makes the Messages API a reasonable `LLMRole` adapter. Server web, fetch, code execution, tool search, and remote MCP must remain disabled because they would bypass `SourceWatcher` and the internal capability registry.

Recommendation: implement or adopt a narrow client-tool adapter; do not expose Anthropic server tools to domain profiles.

Source: [Anthropic tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).

### Pydantic AI

Pydantic AI explicitly provides vendor-SDK-agnostic model classes, provider abstractions, per-model capability profiles, structured outputs, typed dependency injection, tool schema generation, and deterministic `TestModel`/`FunctionModel` facilities. Its durable execution integrations deliberately add external workflow systems such as Temporal, DBOS, Prefect, and Restate.

Recommendation: it is the best candidate for a bounded spike as the implementation behind `LLMRole`, because provider normalization and deterministic fake models are valuable. Acceptance requires proving that the project can retain ownership of the trajectory, tool authorization, failure taxonomy, event ledger, and usage accounting without importing another state authority.

Sources: [Pydantic AI overview](https://pydantic.dev/docs/ai/overview/), [model/provider abstraction and capability profiles](https://pydantic.dev/docs/ai/models/overview/), [function tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/), [durable execution integrations](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/).

### LangGraph

LangGraph is a low-level orchestration runtime with state graphs, durable execution, persistence, human-in-the-loop support, and replay/time-travel facilities. Its checkpointers save graph state and task results; replay may re-execute later nodes, including LLM/API work, and its documentation stresses deterministic workflows, idempotent tasks, and careful treatment of side effects.

Recommendation: use LangGraph now as the contained execution substrate for the typed trajectory engine. A project-owned compiler validates registered node types and hard limits before producing a graph. Checkpoints support recovery and inspection, while every externally meaningful transition is also written to the canonical append-only ledger. Disable cross-thread memory and arbitrary state updates for research runs; replay must bind the original immutable releases and frozen source snapshot.

Sources: [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview), [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [functional API and replay constraints](https://docs.langchain.com/oss/python/langgraph/functional-api).

### DSPy

DSPy expresses typed signatures, composes modules such as prediction, chain-of-thought and ReAct, and optimizes programs against explicit metrics and examples. Its main value begins once a representative dataset and metric exist.

Recommendation: include DSPy in the initial offline evaluation workstream. Start with the recorded corporate-event fixture corpus, explicit metrics for schema validity, citation entailment, source completeness, cutoff safety, contradiction handling, and abstention. A DSPy compilation output is a proposal artifact; activation still requires evaluation gates and an owner-approved immutable release.

Source: [DSPy official overview](https://dspy.ai/).

### MCP

MCP standardizes tool discovery and invocation, including optional output schemas, but the specification treats tool annotations as untrusted unless they come from trusted servers and requires host-side confirmation and access control. Its authorization model explicitly forbids token passthrough. These are protocol-level safeguards, not the project's effective-dated applicability, frozen-source, fixture, or admission rules.

Recommendation: support remote MCP in P0 only through an outbound `MCPCapabilityAdapter` owned by the trusted host. Each remote server and tool must be pinned to an approved identity and immutable local capability release; remote annotations are ignored for authorization; OAuth tokens are audience-bound and never passed through; schemas are snapshotted; network egress is allowlisted; results are revalidated and recorded; and every capability has an offline fixture adapter. Remote MCP remains unavailable to `SourceWatcher`-bypassing profile definitions and cannot mutate policy, files, or execution state.

Sources: [MCP tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools), [MCP authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization).

### LangChain Deep Agents

Deep Agents is explicitly an opinionated agent harness built over LangChain agents and the LangGraph runtime. It provides planning, subagents, model routing, context summarization, virtual filesystems, sandbox execution, memory, permissions, middleware, typed streams, and MCP-compatible tools. The documentation allows filesystem tools to be restricted to a read-only subset or excluded, but permissions do not govern sandbox `execute`; declarative subagents also require careful middleware configuration rather than automatically inheriting every main-agent restriction.

Recommendation: evaluate it as one `AgentLoopRuntime` implementation inside the generic harness, not as the domain architecture itself. The spike must start deny-by-default: no filesystem middleware unless a read-only in-memory backend is demonstrably needed, no `execute`, no REPL, no persistent memory, no automatic general-purpose subagent, no direct MCP discovery, only project-issued capability proxies, project-owned budgets, and project-owned output/admission validation. Its strongest likely value is context-isolated gatherer workers and typed streamed visibility inside a bounded MoA trajectory.

Sources: [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview), [models](https://docs.langchain.com/oss/python/deepagents/models), [permissions](https://docs.langchain.com/oss/python/deepagents/permissions), [backends](https://docs.langchain.com/oss/python/deepagents/backends), [subagents](https://docs.langchain.com/oss/python/deepagents/subagents), [framework/runtime/harness distinction](https://docs.langchain.com/oss/python/concepts/products).

## Three viable approaches

| Approach | Benefit | Main risk | Verdict |
|---|---|---|---|
| Vendor SDK as the harness | Fastest first agent loop | Provider asymmetry and SDK-owned behavior leak into policy, tracing, tools, and failure semantics | Reject as core |
| LangGraph as the contained trajectory substrate | Durable graph execution while preserving project definitions | Checkpoints can accidentally become a second business-state authority | Adopt behind project compiler and ledger |
| Deep Agents as a replaceable loop strategy | Rich context isolation and subagent patterns inside agentic nodes | Broad default tools, memory, filesystem, and subagent inheritance | Bounded spike; never policy core |
| Repository-owned typed harness with LangGraph, DSPy, MCP and provider adapters | Exact compatibility and safety with selected ecosystem leverage | More boundary code and cross-library contract tests | Recommend |

## P0 proof obligations

1. The same recorded SEC/NSE/BSE snapshot produces byte-equivalent normalized tool results and semantically equivalent evidence across repeated offline runs.
2. OpenAI and Anthropic `LLMRole` adapters pass the same provider contract suite, including strict structured output, tool requests, timeout, refusal, malformed output, and usage accounting.
3. An unsupported provider capability is rejected before a run or converted to the approved typed missing outcome; it never silently downgrades semantics.
4. No profile can access network, filesystem mutation, policy mutation, arbitrary execution, or a tool absent from its immutable allowlist.
5. Every node is bounded by iterations, tokens, monetary budget, elapsed time, and declared failure policy.
6. Replay consumes the original frozen source snapshot and immutable releases; it never silently refetches or resolves newer definitions.
7. NSE-only, BSE-only, dual-listed, and SEC-applicable issuers derive the correct mandatory source set at the event cutoff.
8. One applicable channel missing yields degraded-but-usable evidence; all mandatory primary channels missing yields typed insufficient evidence.
9. Conflicting official announcements remain preserved as a contradiction and cannot create positive influence.
10. Evidence containing executable prices, quantities, targets, returns, conviction multipliers, or order instructions is rejected at the external seam.
11. Agent unavailability, degraded evidence, and contradiction do not disable the relational champion.
12. The canonical run ledger records profile, trajectory, prompt, tool, source policy, evaluation and model-routing releases; provider/model; tool I/O hashes; tokens; cost; latency; cutoff; status; and failure reason.

## Material unknowns for a bounded spike

- Whether Pydantic AI's lower-level model abstraction can satisfy the exact `LLMRole` contract without its agent graph or tool runtime becoming a hidden authority.
- Whether both initial providers preserve identical strict-schema and parallel-tool semantics for the chosen output schemas.
- Whether the LangGraph checkpointer can be made a pure recovery projection of the canonical run ledger without duplicate or contradictory lifecycle states.
- Whether Deep Agents can run with every mutation-capable default removed and propagate identical capability restrictions into every declared or dynamic subagent.
- Whether remote MCP reconnect, tool-list changes, and server schema drift can be made fail-closed while recorded fixtures remain replayable.
- Which DSPy metric/optimizer combination improves evidence quality without learning fixture-specific shortcuts or weakening abstention.
- The actual latency, token, and cost distribution for the corporate-event gather/judge trajectory over the recorded fixture suite.
