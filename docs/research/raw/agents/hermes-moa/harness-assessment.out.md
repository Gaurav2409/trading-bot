## 1. Executive verdict

- **ADOPT — repository-owned thin `DomainAgentHarness` as the core.** It owns the ledger, limits, profile binding, failure→typed-packet mapping, and the evidence/admission seam; external frameworks never own tool authority, memory, policy, or admission.
- **ADAPT BEHIND PORT — Pydantic AI plus direct OpenAI Responses/Chat and Anthropic Messages SDKs as `LLMRole` adapters.** Typed output, fixture models, capability gating, internal OTel only; disable vendor cloud tracing; reject web/server/durable capabilities.
- **ADOPT — LangGraph Functional API behind `TrajectoryEngine` only, version-pinned.** Use `@entrypoint`/`@task` replay, but the Hermes ledger stays canonical.
- **ADOPT — remote MCP as a bounded, harness-controlled internal transport to approved read-only sealed-snapshot tools.** No live fetch, no model-selected endpoints, freeze tool lists per release, ignore `listChanged`.
- **ADOPT — DSPy for offline eval/prompt optimization only.** Optimized prompts become candidates for immutable releases; no runtime self-tuning.
- **BORROW PATTERN — Hermes Agent, OpenAI Agents SDK, LangChain Deep Agents:** registry/check gating, lifecycle hooks, typed structured-output patterns, permission rules.
- **REJECT FROM CORE — broad personal-agent runtimes:** browser, shell, code execution, file mutation, persistent memory, autonomous subagents, hosted/server tools, prompt/policy mutation, trading.

## 2. Candidate decision matrix

"Strongest fit" cites verified source capability; "conflict/role" is project-fit inference.

| Candidate | Strongest fit | Constitutional conflict | Recommended role | Confidence |
|---|---|---|---|---|
| Hermes Agent | Provider resolver; self-registering registry; `check_fn` | Terminal/browser/code tools; sessions+memory; lossy compression | BORROW PATTERN; reject runtime | High |
| OpenAI Agents SDK | `output_type`; hooks; guardrails; provider swap | Cloud tracing default; hosted multi-agent state; Responses/Chat asymmetry | ADAPT BEHIND PORT; tracing off | High |
| Anthropic tool runner/Messages API | Client `tool_use`; strict schemas | Server tools run off-snapshot (web/fetch/code) | ADAPT BEHIND PORT; client tools only | High |
| LangGraph | `@task` replay; interrupts; fixture savers | Checkpointer/Store → hidden memory; replay ≠ Hermes events | ADOPT; bounded trajectory substrate | Med-High |
| LangChain Deep Agents | Permission rules; typed backends; subagent structure | Shell/execute; mutable files/memory; autonomous subagents | BORROW PATTERN; reject runtime | High |
| Pydantic AI | Typed output; `TestModel`; profiles; fallback; OTel | Web/MCP/durable features add state/bypass policy | ADAPT BEHIND PORT; `LLMRole`/fixtures | High |
| DSPy | Signatures; typed fields; metric optimizers | `ReAct`/interpreter exec; prompt mutation outside releases | ADOPT; bounded offline eval only | Med |
| Remote MCP | `tools/list`/`call`; schemas; `isError`; OAuth audience | Network discovery; untrusted annotations; `listChanged` injection | ADOPT; bounded internal transport | Med |
| Repository-owned thin harness | Exact seam; releases; sealed snapshots; deterministic tests | Build cost; must implement replay/observability | ADOPT as core | High |

## 3. Critical disagreements and traps

1. **Harness marketing hides authority.** Hermes and Deep Agents bundle memory, sessions, filesystem, browser, terminal, code exec, subagents, and compression — useful patterns, unconstitutional as core runtime powers.
2. **Structured output is asymmetric.** OpenAI Responses, Anthropic strict client tools, and Pydantic AI express schemas; many OpenAI-compatible providers only approximate JSON. Provider substitution must be capability-gated and fail closed.
3. **Tracing can exfiltrate sealed evidence.** OpenAI Agents traces to OpenAI by default and Deep Agents assumes LangSmith; only Pydantic AI OTel routes to an internal collector cleanly. Hermes must own trace export and redaction.
4. **Replay is not just checkpointing.** LangGraph resumes by replaying entrypoints and restoring task results; Hermes also needs immutable profile IDs, snapshot IDs, tool calls, model identity, costs, failures, and admission decisions in its own ledger. Confusing the checkpointer with the ledger is the primary upgrade risk.
5. **MCP schema is not trust.** MCP annotations are untrusted and authorization is optional. Tool discovery must be frozen by `AgentProfileRelease`; runtime list changes cannot expand agent capability.

## 4. Minimal target boundary

- **`DomainAgentHarness`** implements `ResearchAgentPort.investigate(question) -> EvidencePacket | None`. It loads one immutable `AgentProfileRelease`, binds `TrajectoryRelease`, `LLMRole`, and allowlisted tools, owns limits and ledger events, and maps expected provider/tool/timeout/validation/budget failures to typed missing/degraded/insufficient/contradictory packets. `None` is reserved for observable catastrophic infrastructure failure.
- **`TrajectoryEngine`** runs typed nodes — agent loop, deterministic transform, schema validation, branch, fan-out/join, judge, admission, explicit-missing — each with typed I/O, hard limits, fixture mode, and ledger events. A LangGraph implementation is optional and replaceable behind this port.
- **`LLMRole`** is the only vendor-SDK boundary: `complete(prompt, schema) -> typed output | LLMRoleFailure`, carrying provider/model/API surface, usage, finish reason, and validation status. It never executes tools, fetches sources, persists memory, or mutates policy.
- **`ToolCapabilityRegistry`** registers versioned pure read-only tools with typed I/O, frozen-snapshot scope, fixture adapter, limits, and profile allowlist. MCP is admitted only here as a fixed internal transport to approved sealed-snapshot tools; dispatch returns typed results/failures.
- **Evidence/admission seam** validates categorical non-executable output, rejects prices/quantities/targets/returns/conviction multipliers/orders, applies effective-dated SEC/NSE/BSE applicability, preserves contradictions, and emits positive/degraded/insufficient/contradictory packets. The relational retrieval champion remains independently available.

## 5. P0 proof obligations

All offline against SEC 8-K plus NSE/BSE recorded fixtures; no live network.

1. Identical profile, snapshot, tool fixtures, and model fixture produce identical packet and ledger.
2. Provider timeout, tool error, schema failure, and budget exhaustion return typed missing/degraded packets, never exceptions or `None`.
3. Simulated catastrophic ledger failure returns observable `None`.
4. Complete non-conflicting applicable official channels produce a positive `EvidencePacket`.
5. Applicability: NSE-only not degraded for missing BSE; dual-listed expects both; SEC required only when filing status applies.
6. One missing mandatory channel degrades but stays usable; all mandatory channels missing yields typed insufficient evidence with no positive influence.
7. Materially conflicting SEC/NSE/BSE records preserve the contradiction and cannot positively influence before deterministic resolution.
8. Non-allowlisted tools and browse/web-fetch/server-tool/shell/file-mutation/policy-mutation attempts are rejected before dispatch and logged.
9. External evidence schema rejects prohibited trading/executable fields; deterministic numeric intermediates stay internal/ledger-only.
10. Cost, latency, tokens, provider/model identity, tool calls, and release/snapshot IDs are queryable; shadow-only sources have no positive influence; the relational champion returns a baseline when agent evidence is missing/degraded/contradictory.

## 6. Sources and uncertainty

Recommendations map to: `research-brief.md` (constraints); Hermes `architecture.md`, `agent-loop.md`, `provider-runtime.md`, `tools-runtime.md`; OpenAI Agents `agents/models/guardrails/tracing.md`; Anthropic tool-use overview; Pydantic AI overview/models/tools/durable-execution; LangGraph overview/persistence/functional-api; Deep Agents overview/permissions/backends/subagents/products/GitHub; `dspy-ai.md`; MCP server-tools and authorization specs.

Material unknowns needing spikes: (1) whether remote MCP can satisfy sealed-snapshot/read-only/no-agent-network controls without a custom gateway; (2) LangGraph checkpoint serialization cost with `EvidencePacket`; (3) DSPy prompt-candidate promotion into immutable releases.

<!-- HERMES-MOA SELF-AUDIT: all-six-sections-present; under-9KB; constraints-preserved -->
