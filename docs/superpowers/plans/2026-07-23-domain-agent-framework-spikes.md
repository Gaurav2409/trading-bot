# Domain Agent Framework Spikes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evaluate remote MCP, Pydantic AI, Deep Agents, and DSPy against the completed P0 harness seams, producing pass/fail evidence and immutable proposals without granting any framework source, policy, ledger, or activation authority.

**Architecture:** Each experiment implements one existing project interface and runs only against recorded corporate-event fixtures. Passing experiments become replaceable adapters; failing experiments remain documented pattern sources. The project-owned `DomainAgentHarness`, releases, capability registry, canonical ledger, compatibility mapping, and admission path are unchanged.

**Tech Stack:** Python 3.11+, MCP Python SDK 1.28.x, Pydantic AI 2.14.x, Deep Agents 0.6.x, DSPy 3.2.x, pytest/pytest-asyncio.

## Global Constraints

- Complete `2026-07-23-domain-agent-p0-tracer.md` Tasks 1–10 before executing these experiments.
- Install the stable MCP 1.x line with `<2`; MCP 2.x is pre-release during this plan.
- Deep Agents receives no filesystem, shell, sandbox execution, REPL, persistent memory, skills loader, direct MCP, or default general-purpose subagent authority.
- Pydantic AI implements `LLMRole` only; its graph, durable state, tool, MCP, and agent authority do not enter the harness.
- DSPy runs offline, uses recorded training and held-out fixtures, and emits `DefinitionProposal`; it cannot modify an active registry.
- Remote MCP is a transport behind a pinned `ToolCapabilityRelease`; runtime discovery cannot add or alter project capabilities.
- Every experiment is credential-free and network-free in CI.
- A failed gate causes no production-interface change.

---

### Task 1: Pinned remote MCP capability adapter

**Files:**
- Modify: `pyproject.toml`
- Create: `src/trading_os/agents/mcp_adapter.py`
- Test: `tests/contract/agents/test_mcp_capability_adapter.py`
- Create: `tests/fixtures/agents/mcp/source_record_query.json`

**Interfaces:**
- Consumes: `ToolCapabilityRelease`, `CapabilityBinding`, injected MCP session, frozen server/tool schema release.
- Produces: `MCPCapabilityAdapter.invoke(request) -> typed result | ExpectedToolFailure` behind `ToolCapabilityRegistry`.

- [ ] **Step 1: Write the fail-closed contract matrix**

```python
@pytest.mark.parametrize(
    ("mutation", "failure_kind"),
    [
        ("server_identity", "server_identity_drift"),
        ("input_schema", "tool_schema_drift"),
        ("output_schema", "tool_schema_drift"),
        ("extra_tool", "runtime_authority_expansion"),
        ("list_changed", "runtime_authority_expansion"),
        ("auth_audience", "auth_audience_mismatch"),
        ("oversized_result", "result_too_large"),
        ("citation_escape", "citation_scope_violation"),
    ],
)
async def test_mcp_adapter_fails_closed(mutation, failure_kind, mcp_adapter_factory) -> None:
    result = await mcp_adapter_factory(mutation).invoke(QUERY)
    assert result == ExpectedToolFailure(kind=failure_kind, retryable=False)
```

- [ ] **Step 2: Add the stable SDK dependency and verify test failure**

Add to an `agent-spikes` optional dependency group in `pyproject.toml`:

```toml
agent-spikes = [
  "mcp>=1.28.1,<2",
]
```

Run: `pytest tests/contract/agents/test_mcp_capability_adapter.py -v`

Expected: collection fails because `mcp_adapter.py` is absent.

- [ ] **Step 3: Implement pinned identity/schema validation around an injected session**

```python
class MCPServerRelease(BaseModel, frozen=True):
    server_id: str
    audience: str
    tool_name: str
    input_schema_hash: str
    output_schema_hash: str
    max_result_bytes: int


class MCPCapabilityAdapter:
    def __init__(self, release, session, allowed_source_record_ids):
        self._release = release
        self._session = session
        self._allowed = frozenset(allowed_source_record_ids)

    async def invoke(self, request):
        observed = await self._session.describe_pinned_tool(self._release.tool_name)
        drift = validate_observed_tool(self._release, observed)
        if drift is not None:
            return drift
        raw = await self._session.call_tool(self._release.tool_name, request.model_dump())
        return validate_result(raw, self._release, self._allowed)
```

The injected session exposes only `describe_pinned_tool(name)` and `call_tool(name, payload)`; the adapter never invokes unrestricted `tools/list`, accepts `listChanged`, or forwards caller tokens.

- [ ] **Step 4: Prove fixture replay and successful typed access**

Run: `pytest tests/contract/agents/test_mcp_capability_adapter.py -v`

Expected: the valid fixture matches the local capability result, and all eight drift/authority cases fail closed.

- [ ] **Step 5: Commit the MCP experiment**

```bash
git add pyproject.toml src/trading_os/agents/mcp_adapter.py tests/contract/agents/test_mcp_capability_adapter.py tests/fixtures/agents/mcp
git commit -m "spike(agents): contain remote MCP behind capabilities"
```

### Task 2: Pydantic AI as an LLMRole adapter

**Files:**
- Modify: `pyproject.toml`
- Create: `src/trading_os/agents/pydantic_ai_role.py`
- Test: `tests/contract/agents/test_pydantic_ai_llm_role.py`

**Interfaces:**
- Consumes: `StructuredInvocation[T]` and injected Pydantic AI model.
- Produces: `PydanticAILLMRole`, satisfying the existing `LLMRole` contract.

- [ ] **Step 1: Reuse the LLMRole contract and add an authority test**

```python
class TestPydanticAILLMRole(LLMRoleContract):
    def build_role(self) -> LLMRole:
        return PydanticAILLMRole(model=FunctionModel(valid_event_response))


async def test_pydantic_ai_role_has_no_tools_or_durable_state() -> None:
    role = PydanticAILLMRole(model=FunctionModel(valid_event_response))
    assert role.registered_tool_count == 0
    assert role.uses_durable_state is False
```

- [ ] **Step 2: Add the dependency and verify the adapter test fails**

Extend `agent-spikes`:

```toml
  "pydantic-ai>=2.14.1,<2.15",
```

Run: `pytest tests/contract/agents/test_pydantic_ai_llm_role.py -v`

Expected: collection fails because `PydanticAILLMRole` is absent.

- [ ] **Step 3: Implement only the owned role boundary**

```python
class PydanticAILLMRole:
    registered_tool_count = 0
    uses_durable_state = False

    def __init__(self, model: Model) -> None:
        self._model = model

    async def invoke(self, invocation: StructuredInvocation[T]):
        agent = Agent(
            self._model,
            output_type=invocation.output_type,
            tools=(),
            retries=0,
        )
        try:
            result = await agent.run(render_prompt(invocation))
        except Exception as error:
            return map_pydantic_ai_failure(error)
        return normalize_pydantic_ai_result(invocation, result)
```

Do not pass dependencies, toolsets, MCP servers, history processors, durable execution, or model-native tools.

- [ ] **Step 4: Run the common contract and compare fixture output hashes**

Run: `pytest tests/contract/agents/test_pydantic_ai_llm_role.py tests/contract/agents/test_fixture_llm_role.py -v`

Expected: both adapters produce the same typed corporate-event output hash and expected-failure categories.

- [ ] **Step 5: Commit the Pydantic AI experiment**

```bash
git add pyproject.toml src/trading_os/agents/pydantic_ai_role.py tests/contract/agents/test_pydantic_ai_llm_role.py
git commit -m "spike(agents): evaluate Pydantic AI behind LLMRole"
```

### Task 3: Deep Agents as a stripped AgenticLoopStrategy

**Files:**
- Modify: `pyproject.toml`
- Create: `src/trading_os/agents/loops.py`
- Create: `src/trading_os/agents/deep_agents_strategy.py`
- Test: `tests/contract/agents/agentic_loop_contract.py`
- Test: `tests/contract/agents/test_deep_agents_strategy.py`

**Interfaces:**
- Consumes: `BoundedAgentLoopRequest[T]`, explicit bound capability proxies, `LLMRole`, outer budget.
- Produces: `AgenticLoopStrategy.run(...) -> AgentLoopResult[T]` and candidate `BoundedDeepAgentsStrategy`.

- [ ] **Step 1: Define and test the project-owned loop contract**

```python
class BoundedAgentLoopRequest(BaseModel, Generic[T], frozen=True):
    run_id: str
    node_id: str
    output_type: type[T]
    capability_names: tuple[str, ...]
    max_turns: int = Field(ge=1)
    max_tokens: int = Field(ge=1)
    max_tool_calls: int = Field(ge=0)
    max_subagents: int = Field(ge=0)
    max_subagent_depth: int = Field(ge=0)


class AgenticLoopStrategy(Protocol):
    async def run(self, request: BoundedAgentLoopRequest[T]) -> AgentLoopResult[T]: ...
```

Contract cases must cover typed success, token/turn/tool exhaustion, disallowed capability, child isolation, and transcript replay.

- [ ] **Step 2: Add stable Deep Agents and run the failing contract**

Extend `agent-spikes`:

```toml
  "deepagents>=0.6.12,<0.7",
```

Run: `pytest tests/contract/agents/test_deep_agents_strategy.py -v`

Expected: collection fails because `BoundedDeepAgentsStrategy` is absent.

- [ ] **Step 3: Construct the candidate with explicit omissions**

```python
class BoundedDeepAgentsStrategy:
    def __init__(self, model, capability_tool_factory) -> None:
        self._model = model
        self._capability_tool_factory = capability_tool_factory

    async def run(self, request):
        tools = tuple(self._capability_tool_factory(name) for name in request.capability_names)
        agent = create_deep_agent(
            model=self._model,
            tools=list(tools),
            system_prompt=render_loop_prompt(request),
            subagents=[],
            middleware=[],
        )
        return await invoke_with_outer_budget(agent, request)
```

The constructor must reject non-empty filesystem backends, shell/sandbox tools, persistent stores, skills middleware, direct MCP tools, undeclared subagents, or a model object that bypasses the metered project facade.

- [ ] **Step 4: Run the pass/fail gate**

Run: `pytest tests/contract/agents/test_deep_agents_strategy.py -v`

Expected: all contract cases pass. If any case fails after systematic diagnosis, stop this task, record the exact failed gate as `pattern_only`, remove the candidate adapter from release fixtures, and retain the unchanged `DomainAgentHarness` and `TrajectoryRelease` interfaces.

- [ ] **Step 5: Commit the Deep Agents evidence**

```bash
git add pyproject.toml src/trading_os/agents/loops.py src/trading_os/agents/deep_agents_strategy.py tests/contract/agents/agentic_loop_contract.py tests/contract/agents/test_deep_agents_strategy.py
git commit -m "spike(agents): gate Deep Agents as a loop strategy"
```

### Task 4: DSPy offline definition proposals

**Files:**
- Modify: `pyproject.toml`
- Create: `src/trading_os/agents/proposals.py`
- Create: `src/trading_os/agents/dspy_optimizer.py`
- Create: `tests/fixtures/agents/evaluation/corporate_event_train.jsonl`
- Create: `tests/fixtures/agents/evaluation/corporate_event_held_out.jsonl`
- Test: `tests/unit/agents/test_definition_proposals.py`
- Test: `tests/integration/agents/test_dspy_optimizer.py`

**Interfaces:**
- Consumes: parent prompt/profile release, recorded train fixtures, issuer/event-family-separated held-out fixtures, hard safety metrics.
- Produces: immutable `DefinitionProposal` and evaluation receipt; no registry write API.

- [ ] **Step 1: Write proposal immutability and activation-denial tests**

```python
def test_definition_proposal_contains_provenance_and_cannot_activate() -> None:
    proposal = DefinitionProposal(
        proposal_id="proposal:prompt:gather:2",
        parent_release_id="prompt:gather:v1",
        candidate_content_hash="sha256:candidate",
        optimizer_release="dspy:3.2",
        train_fixture_hash="sha256:train",
        held_out_fixture_hash="sha256:held-out",
        metrics=(MetricResult(name="schema_validity", value=1.0, hard_floor=1.0),),
    )
    assert not hasattr(proposal, "activate")
    assert not hasattr(proposal, "registry")


def test_hard_safety_floor_cannot_be_traded_for_aggregate_gain() -> None:
    assert evaluate_candidate(candidate(schema_validity=0.99, aggregate=0.95)).accepted is False
```

- [ ] **Step 2: Add DSPy and verify the optimizer test fails**

Extend `agent-spikes`:

```toml
  "dspy>=3.2.1,<3.3",
```

Run: `pytest tests/unit/agents/test_definition_proposals.py tests/integration/agents/test_dspy_optimizer.py -v`

Expected: collection fails because proposal and optimizer modules are absent.

- [ ] **Step 3: Implement proposal-only evaluation**

```python
class MetricResult(BaseModel, frozen=True):
    name: str
    value: float
    hard_floor: float | None = None


class DefinitionProposal(BaseModel, frozen=True):
    proposal_id: str
    parent_release_id: str
    candidate_content_hash: str
    optimizer_release: str
    train_fixture_hash: str
    held_out_fixture_hash: str
    metrics: tuple[MetricResult, ...]


class DSPyDefinitionOptimizer:
    def propose(self, parent, train, held_out) -> DefinitionProposal:
        candidate = self._compile_against_train(parent, train)
        metrics = self._evaluate(candidate, held_out)
        return build_definition_proposal(parent, candidate, train, held_out, metrics)
```

The optimizer object receives no `ReleaseRegistry`, filesystem path to active definitions, provider credentials, or activation callback.

- [ ] **Step 4: Evaluate held-out safety floors**

The held-out set must use issuers and event families absent from training. Assert exact floors of `1.0` for schema validity, citation scope, cutoff safety, prohibited-field rejection, and contradiction preservation. Run:

Run: `pytest tests/unit/agents/test_definition_proposals.py tests/integration/agents/test_dspy_optimizer.py -v`

Expected: a compliant candidate produces a proposal; any hard-floor regression is rejected regardless of aggregate score.

- [ ] **Step 5: Commit the offline optimizer**

```bash
git add pyproject.toml src/trading_os/agents/proposals.py src/trading_os/agents/dspy_optimizer.py tests/fixtures/agents/evaluation tests/unit/agents/test_definition_proposals.py tests/integration/agents/test_dspy_optimizer.py
git commit -m "feat(agents): add DSPy proposal-only optimization"
```

### Task 5: Consolidated experiment decision record

**Files:**
- Create: `docs/research/19-domain-agent-framework-spike-results.md`
- Test: `tests/integration/agents/test_framework_spike_acceptance.py`

**Interfaces:**
- Consumes: contract and integration results from Tasks 1–4.
- Produces: explicit adopt/reject result for each adapter and a machine-checked assertion that the public port and release schemas did not widen.

- [ ] **Step 1: Add an architecture invariance test**

```python
def test_framework_spikes_do_not_widen_public_authority() -> None:
    assert tuple(inspect.signature(ResearchAgentPort.investigate).parameters) == ("self", "question")
    assert "activate" not in ReleaseRegistry.__dict__
    assert "tools_list" not in MCPCapabilityAdapter.__dict__
    assert "filesystem" not in BoundedAgentLoopRequest.model_fields
    assert "order" not in EvidencePacket.model_fields
```

- [ ] **Step 2: Run all framework contracts**

Run: `pytest tests/contract/agents tests/integration/agents/test_dspy_optimizer.py tests/integration/agents/test_framework_spike_acceptance.py -v`

Expected: every accepted adapter passes its contract; rejected adapters have a named failing gate and are absent from active/shadow profile release fixtures.

- [ ] **Step 3: Record the decision matrix**

For each component, record dependency version, fixture hash, contract command, result, failed gate if any, retained project interface, and decision (`adopt_adapter`, `pattern_only`, or `reject`). Do not use an aggregate score to override a safety failure.

- [ ] **Step 4: Run final repository checks**

Run: `ruff check src tests && mypy src && git diff --check`

Expected: all commands exit zero.

- [ ] **Step 5: Commit experiment results**

```bash
git add docs/research/19-domain-agent-framework-spike-results.md tests/integration/agents/test_framework_spike_acceptance.py
git commit -m "docs(agents): record framework spike decisions"
```

## Experiment completion gate

The experiments are complete when each framework has an explicit evidence-backed decision, every adopted adapter passes the existing project contract without widening authority, and no rejected adapter appears in a profile release.

## Specification coverage

| Approved specification area | Implemented by |
|---|---|
| remote MCP as pinned internal transport | Task 1 |
| Pydantic AI behind `LLMRole` | Task 2 |
| Deep Agents as a replaceable bounded loop strategy | Task 3 |
| DSPy as offline proposal engine | Task 4 |
| framework authority invariance and evidence-backed adoption | Task 5 |
