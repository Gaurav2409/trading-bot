# Domain Agent Harness Evaluation

**Date:** 2026-07-23

## Executive conclusion

The Trading OS should own a thin `DomainAgentHarness`, immutable profile and trajectory definitions, the capability registry, compatibility mapping, and the canonical run ledger. LangGraph should execute compiled trajectories behind a project interface. Pydantic AI and direct vendor SDKs should be evaluated behind `LLMRole`; DSPy should optimize definitions offline; remote MCP should enter through a pinned host-controlled gateway; and Deep Agents should receive a strict pass/fail spike as one internal agent-loop strategy.

This conclusion combines an independent primary-source review with a Hermes `deep-research` MoA review over a sanitized constraints brief and the public source corpus. The two reviews agreed on the owned core, bounded LangGraph, offline DSPy, governed MCP, and provider boundary. They differed only on whether Deep Agents deserves a contained runtime spike; the architecture permits the spike without making it a dependency.

## Evaluation matrix

| Candidate | Strongest verified capability | Main fit problem | Decision |
|---|---|---|---|
| Hermes Agent | One core across entry points, provider routing, tool registry, iteration limits, callbacks, profile isolation | Broad terminal, file, browser, memory, delegation, plugin, and mutable session authority | Borrow patterns; do not embed runtime |
| OpenAI Agents SDK | Typed output, hooks, guardrails, tools, tracing, and model integration | Provider feature parity varies; tool guardrails do not cover every hosted/handoff surface; tracing may capture sensitive inputs | Adapter/pattern source behind `LLMRole` |
| Anthropic Messages/tool use | Strict client-tool schemas and a clear client-versus-server execution model | Server web/fetch/code tools bypass frozen project capabilities | Direct client-tool adapter behind `LLMRole` |
| Pydantic AI | Provider-neutral model abstractions, capability profiles, Pydantic output, `TestModel` and `FunctionModel` | Its agent, tool, and durable-state layers could become a second authority | Bounded `LLMRole` and fixture-model spike |
| LangGraph | Typed graph execution, checkpoints, interrupts, persistence, recovery, fan-out and human review | Checkpoint/replay state can be mistaken for canonical evidence history | Adopt behind project compiler and ledger |
| LangChain Deep Agents | LangGraph-based harness with model routing, subagents, context management, permissions, backends, and typed streams | Defaults include filesystem, execution, memory, and subagent behavior; restriction inheritance requires care | Pass/fail spike as an internal loop strategy |
| DSPy | Typed signatures, modular programs, ReAct, metrics, and optimizers | Runtime self-tuning would violate immutable releases and may overfit fixtures | Adopt offline as proposal engine |
| Remote MCP | Standard tool listing/calling, schemas, errors, and OAuth resource binding | Tool annotations are not trust; runtime discovery, server drift, and token handling add authority and injection surface | Adopt only through `MCPCapabilityAdapter` |
| Repository-owned harness | Exact compatibility, policy, failure, replay, and workbench semantics | More compiler, adapter, and contract-test work | Adopt as constitutional core |

## Why the harness remains project-owned

The existing caller needs one operation: investigate a question and return categorical evidence or catastrophic absence. Framework sessions, graphs, provider objects, tool clients, and checkpoints add no value at that seam. Hiding them creates a deep module: deleting the harness would force profile resolution, capability authorization, provider normalization, trajectory recovery, failure mapping, ledger emission, seam validation, and admission into the orchestrator.

Hermes' official architecture demonstrates both the value of a shared core and the mismatch of a broad personal-agent runtime: its tool and session system includes persistent memory, terminal and file capabilities, plugins, browsers, and agent-level tools that sometimes bypass normal registry dispatch. These are useful product features, but they are not evidence-boundary controls. See [Hermes architecture](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/architecture.md), [agent loop](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/agent-loop.md), and [tools runtime](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/tools-runtime.md).

## Why LangGraph is adopted but contained

LangGraph is a low-level orchestration runtime with graph execution, persistence, checkpoints, interrupts, time travel, and fault recovery. Its replay behavior also means later model and API steps may execute again unless work is placed in replay-aware tasks and made idempotent. The project therefore compiles immutable `TrajectoryRelease`s to LangGraph and treats checkpoints as recovery state only. The append-only `AgentRunLedger` remains canonical.

The Graph API is the primary target because the product definition is itself an inspectable node/edge graph. Functional tasks may be used within registered nodes, but Python control flow cannot replace the immutable visual definition. See the [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview), [persistence model](https://docs.langchain.com/oss/python/langgraph/persistence), and [functional replay guidance](https://docs.langchain.com/oss/python/langgraph/functional-api).

## Deep Agents evaluation

Deep Agents is explicitly an opinionated harness on LangGraph, adding planning, subagents, virtual filesystems, execution backends, context management, memory, permissions, middleware, and MCP-compatible tools. It also supports read-only filesystem subsets and configurable middleware. However, its documentation notes that filesystem permissions do not govern sandbox execution, and declarative subagents require their own restriction setup rather than automatically inheriting all main-agent middleware.

It will therefore be evaluated only as a replaceable `AgenticLoopStrategy`. The spike begins with filesystem, shell, execution, REPL, persistent memory, automatic general-purpose subagents, and direct MCP discovery absent. Every parent and child receives explicit immutable capability proxies and outer-harness budgets. See [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview), [permissions](https://docs.langchain.com/oss/python/deepagents/permissions), [backends](https://docs.langchain.com/oss/python/deepagents/backends), and [subagents](https://docs.langchain.com/oss/python/deepagents/subagents).

## Provider boundary

OpenAI's SDK supports structured `output_type`, lifecycle hooks, models, sessions, tracing, and guardrails, while documenting feature differences across non-OpenAI providers. Its tool guardrails do not cover every hosted-tool and handoff path, and tracing is enabled by default with configurable sensitive-data capture. These are reasons to wrap, not reject, the provider integration. See [OpenAI agents](https://openai.github.io/openai-agents-python/agents/), [model-provider limitations](https://openai.github.io/openai-agents-python/models/), [guardrails](https://openai.github.io/openai-agents-python/guardrails/), and [tracing](https://openai.github.io/openai-agents-python/tracing/).

Anthropic distinguishes client tools executed by the application from server tools executed on Anthropic infrastructure and supports strict custom-tool schemas. Domain profiles use client tools only through project proxies. See [Anthropic tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).

Pydantic AI provides vendor-neutral model classes, capability profiles, typed output, tool schemas, and deterministic test models. The spike will determine whether its lower-level abstractions can implement `LLMRole` without importing its graph or tool runtime as authority. See [Pydantic AI models](https://pydantic.dev/docs/ai/models/overview/), [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/), and [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/).

## DSPy role

DSPy exposes typed signatures, modules, ReAct, metrics, and optimizers. It enters P0 as an offline evaluation and definition-proposal tool. Training and held-out fixtures are separated; abstention, contradiction, cutoff, and executable-field safety remain hard floors. A compiled candidate cannot activate itself. See [DSPy](https://dspy.ai/).

## Remote MCP role

MCP tool schemas standardize transport but do not grant project authority. The specification says tool annotations should be treated as untrusted unless supplied by trusted servers, and the authorization specification forbids token passthrough. A host-controlled adapter therefore pins server identity and schema, uses audience-bound credentials, ignores runtime authority expansion, revalidates results locally, and supplies offline fixtures. See [MCP tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) and [MCP authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization).

## Adopted interface synthesis

Three independent interface designs were compared:

1. a minimal deep module with one operational method per seam;
2. a graph-native compiler and typed plugin design;
3. a compatibility-first P0 design with identical production and replay callers.

The synthesis keeps the existing one-method external port, uses identical production/replay caller paths, and adopts the graph-native model internally. Framework types never cross project seams. The initial registered nodes are bounded agent loop, deterministic transform, validation, branch, fan-out, join, judge, categorical seam, admission, and explicit missing.

## Required spikes

1. Compile and replay the corporate-event trajectory in LangGraph while reconciling every checkpoint with the canonical ledger.
2. Run OpenAI, Anthropic, and Pydantic test adapters through one structured `LLMRole` suite.
3. Prove a stripped Deep Agents parent and child can see only injected read-only capabilities.
4. Prove an MCP fixture server fails closed on identity, schema, tool-list, auth-audience, result-size, and citation drift.
5. Run DSPy on separated corporate-event fixtures and demonstrate held-out improvement without weakening safety floors.

## Recommendation

Proceed with the architecture in [the domain-agent specification](../superpowers/specs/2026-07-23-domain-agent-architecture.md). Dependency selection remains reversible because each external runtime sits behind an interface justified by at least two real implementations or by recovery requirements. Release, source, evidence, admission, and audit authority remain project-owned.
