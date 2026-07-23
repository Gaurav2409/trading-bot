# P0 Corporate-Event Domain Agent Tracer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a shadow-only `corporate_event` tracer that preserves `ResearchAgentPort`, consumes recorded SEC 8-K and applicable NSE/BSE announcement records, executes gather → deterministic normalize → judge through one generic harness, and returns admitted categorical evidence with a canonical run ledger.

**Architecture:** Project-owned immutable releases, capability bindings, compatibility mapping, and ledger remain authoritative. `TrajectoryRelease` is compiled behind `TrajectoryEngine`; the first production engine privately uses LangGraph, while all model calls cross `LLMRole`. Source adapters seal records before execution, and every expected failure becomes admitted missing evidence rather than disabling the relational champion.

**Tech Stack:** Python 3.11+, Pydantic 2.7+, pytest/pytest-asyncio, LangGraph 1.2.x, OpenAI Python 2.46.x, Anthropic Python 0.117.x.

## Global Constraints

- Keep `ResearchAgentPort.investigate(ResearchQuestion) -> EvidencePacket | None` unchanged.
- Use one `DomainAgentHarness`; `corporate_event` is a profile, not a harness subclass.
- No price, quantity, target, expected return, position weight, conviction multiplier, or order intent may cross the evidence seam.
- Every non-catastrophic terminal path must construct an explicit packet and pass `admit_packet()`.
- `None` is reserved for corrupt/unavailable canonical ledger or unresolved immutable release closure.
- Agents receive only node-scoped, typed, read-only capability proxies over `ResearchQuestion.source_record_ids` and `data_snapshot_id`.
- NSE-only and BSE-only listings are complete when their sole applicable exchange is captured; an inapplicable exchange is not missing.
- One missing applicable official channel is degraded but usable; all mandatory channels missing is insufficient; conflicting applicable official records are contradictory. Degraded and contradictory outputs have no positive influence.
- Production and replay use the same `ResearchAgentPort` caller path.
- P0 remains shadow-only and cannot activate `DecisionFeatureActivation` or create executable intent.

## Build order and blocking edges

```text
release types ─┬─> release registry ───────────────┐
               ├─> source coverage + fixtures ─┐   │
               └─> capabilities ────────────────┼──> trajectory + ledger
LLMRole + fixture/provider adapters ─────────────┘          │
                                                            v
                                                  corporate-event nodes
                                                            │
                                                            v
                                                   DomainAgentHarness
                                                            │
                                                            v
                                              replay + shadow composition
```

---

### Task 1: Immutable release and run types

**Files:**
- Create: `src/trading_os/agents/__init__.py`
- Create: `src/trading_os/agents/models.py`
- Test: `tests/unit/agents/__init__.py`
- Test: `tests/unit/agents/test_models.py`

**Interfaces:**
- Consumes: `EvidenceDomain` from `trading_os.research.models`.
- Produces: `ReleaseStatus`, `NodeKind`, `CoverageStatus`, `RunOutcome`, `ExpectedAgentFailure`, `RunBudget`, `TrajectoryNodeRelease`, `TrajectoryEdge`, `TrajectoryRelease`, `AgentProfileRelease`, and `ReleaseClosure`.

- [ ] **Step 1: Write failing immutability and bounded-cycle tests**

```python
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from trading_os.agents.models import (
    AgentProfileRelease,
    NodeKind,
    RunBudget,
    TrajectoryEdge,
    TrajectoryNodeRelease,
    TrajectoryRelease,
)
from trading_os.research.models import EvidenceDomain


def test_agent_profile_is_immutable_and_references_releases_only() -> None:
    profile = AgentProfileRelease(
        release_id="profile:corporate-event:v1",
        status="shadow",
        effective_from=datetime(2026, 7, 23, tzinfo=UTC),
        domain=EvidenceDomain.CORPORATE_EVENT,
        trajectory_release_id="trajectory:corporate-event:v1",
        prompt_release_ids=("prompt:gather:v1", "prompt:judge:v1"),
        capability_release_ids=("capability:source-record-query:v1",),
        source_policy_release_id="source-policy:corporate-event:v1",
        routing_policy_release_id="routing:fixture:v1",
        output_schema_release_id="schema:evidence-packet:v1",
        failure_policy_release_id="failure:explicit-missing:v1",
        evaluation_policy_release_id="evaluation:corporate-event:v1",
        budget=RunBudget(max_turns=4, max_tokens=8_000, max_tool_calls=8),
        content_hash="sha256:profile-v1",
    )
    with pytest.raises(ValidationError):
        profile.domain = EvidenceDomain.FUNDAMENTAL


def test_trajectory_rejects_cycle_without_monotonic_budget_gate() -> None:
    with pytest.raises(ValidationError, match="cycle requires a budget gate"):
        TrajectoryRelease(
            release_id="trajectory:bad:v1",
            status="shadow",
            effective_from=datetime(2026, 7, 23, tzinfo=UTC),
            input_schema_id="schema:research-question:v1",
            output_schema_id="schema:evidence-packet:v1",
            nodes=(
                TrajectoryNodeRelease(node_id="gather", kind=NodeKind.AGENT_LOOP),
                TrajectoryNodeRelease(node_id="judge", kind=NodeKind.AGENT_LOOP),
            ),
            edges=(TrajectoryEdge(source="gather", target="judge"), TrajectoryEdge(source="judge", target="gather")),
            terminal_node_ids=("judge",),
            content_hash="sha256:bad",
        )
```

- [ ] **Step 2: Run the tests and verify the missing module failure**

Run: `pytest tests/unit/agents/test_models.py -v`

Expected: collection fails with `ModuleNotFoundError: No module named 'trading_os.agents'`.

- [ ] **Step 3: Implement the frozen release models and structural validators**

```python
# src/trading_os/agents/models.py
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from trading_os.research.models import EvidenceDomain


class ReleaseStatus(StrEnum):
    PROPOSED = "proposed"
    EXPERIMENTAL = "experimental"
    SHADOW = "shadow"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RETIRED = "retired"


class NodeKind(StrEnum):
    AGENT_LOOP = "agent_loop"
    DETERMINISTIC_TRANSFORM = "deterministic_transform"
    VALIDATION = "validation"
    BRANCH = "branch"
    FAN_OUT = "fan_out"
    JOIN = "join"
    JUDGE = "judge"
    CATEGORICAL_SEAM = "categorical_seam"
    ADMISSION = "admission"
    EXPLICIT_MISSING = "explicit_missing"
    BUDGET_GATE = "budget_gate"


class CoverageStatus(StrEnum):
    COMPLETE = "complete"
    DEGRADED = "degraded"
    CONTRADICTORY = "contradictory"
    INSUFFICIENT = "insufficient"
    SUSPENDED = "suspended"
    INAPPLICABLE = "inapplicable"


class RunOutcome(StrEnum):
    ADMITTED = "admitted"
    EXPLICIT_MISSING = "explicit_missing"
    CATASTROPHIC = "catastrophic"


class ExpectedAgentFailure(RuntimeError):
    def __init__(self, kind: str, *, retryable: bool = False) -> None:
        super().__init__(kind)
        self.kind = kind
        self.retryable = retryable


class RunBudget(BaseModel, frozen=True):
    max_turns: int = Field(ge=1)
    max_tokens: int = Field(ge=1)
    max_tool_calls: int = Field(ge=0)
    max_elapsed_ms: int = Field(default=30_000, ge=1)
    max_cost_microunits: int = Field(default=0, ge=0)


class TrajectoryNodeRelease(BaseModel, frozen=True):
    node_id: str
    kind: NodeKind
    capability_release_ids: tuple[str, ...] = ()
    budget: RunBudget | None = None


class TrajectoryEdge(BaseModel, frozen=True):
    source: str
    target: str
    condition: str | None = None


class TrajectoryRelease(BaseModel, frozen=True):
    release_id: str
    status: ReleaseStatus
    effective_from: datetime
    effective_until: datetime | None = None
    supersedes: str | None = None
    input_schema_id: str
    output_schema_id: str
    nodes: tuple[TrajectoryNodeRelease, ...]
    edges: tuple[TrajectoryEdge, ...]
    terminal_node_ids: tuple[str, ...]
    content_hash: str

    @model_validator(mode="after")
    def validate_graph(self) -> "TrajectoryRelease":
        node_ids = {node.node_id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("node IDs must be unique")
        if not set(self.terminal_node_ids).issubset(node_ids):
            raise ValueError("terminal node is not registered")
        if any(edge.source not in node_ids or edge.target not in node_ids for edge in self.edges):
            raise ValueError("edge references an unknown node")
        cyclic_nodes = {edge.source for edge in self.edges if any(back.target == edge.source for back in self.edges if back.source == edge.target)}
        if cyclic_nodes and not any(node.kind is NodeKind.BUDGET_GATE for node in self.nodes):
            raise ValueError("cycle requires a budget gate")
        return self


class AgentProfileRelease(BaseModel, frozen=True):
    release_id: str
    status: ReleaseStatus
    effective_from: datetime
    effective_until: datetime | None = None
    supersedes: str | None = None
    domain: EvidenceDomain
    trajectory_release_id: str
    prompt_release_ids: tuple[str, ...]
    capability_release_ids: tuple[str, ...]
    source_policy_release_id: str
    routing_policy_release_id: str
    output_schema_release_id: str
    failure_policy_release_id: str
    evaluation_policy_release_id: str
    budget: RunBudget
    content_hash: str


class ReleaseClosure(BaseModel, frozen=True):
    profile: AgentProfileRelease
    trajectory: TrajectoryRelease
    content_hash: str
```

- [ ] **Step 4: Run focused tests and static checks**

Run: `pytest tests/unit/agents/test_models.py -v && ruff check src/trading_os/agents tests/unit/agents`

Expected: tests pass and Ruff reports no errors.

- [ ] **Step 5: Commit the release model slice**

```bash
git add src/trading_os/agents tests/unit/agents
git commit -m "feat(agents): add immutable profile and trajectory releases"
```

### Task 2: Effective release registry and closure resolution

**Files:**
- Create: `src/trading_os/agents/registry.py`
- Test: `tests/unit/agents/test_registry.py`

**Interfaces:**
- Consumes: `AgentProfileRelease`, `TrajectoryRelease`, `ReleaseClosure`, `EvidenceDomain`.
- Produces: `ReleaseRegistry.resolve(domain, cutoff) -> ReleaseClosure` and typed `ReleaseResolutionError`.

- [ ] **Step 1: Write failing effective-date and fail-closed tests**

```python
def test_registry_resolves_one_effective_shadow_profile(corporate_event_releases) -> None:
    registry = ReleaseRegistry(*corporate_event_releases)
    closure = registry.resolve(EvidenceDomain.CORPORATE_EVENT, CUTOFF)
    assert closure.profile.release_id == "profile:corporate-event:v1"
    assert closure.trajectory.release_id == "trajectory:corporate-event:v1"


def test_registry_fails_on_two_effective_profiles(corporate_event_releases) -> None:
    profile, trajectory = corporate_event_releases
    registry = ReleaseRegistry((profile, profile.model_copy(update={"release_id": "duplicate"})), (trajectory,))
    with pytest.raises(ReleaseResolutionError, match="exactly one effective profile"):
        registry.resolve(EvidenceDomain.CORPORATE_EVENT, CUTOFF)
```

- [ ] **Step 2: Run the tests and verify the missing registry failure**

Run: `pytest tests/unit/agents/test_registry.py -v`

Expected: collection fails because `trading_os.agents.registry` does not exist.

- [ ] **Step 3: Implement exact-one resolution and deterministic closure hashing**

```python
class ReleaseResolutionError(RuntimeError):
    pass


class ReleaseRegistry:
    def __init__(
        self,
        profiles: tuple[AgentProfileRelease, ...],
        trajectories: tuple[TrajectoryRelease, ...],
    ) -> None:
        self._profiles = profiles
        self._trajectories = {item.release_id: item for item in trajectories}

    def resolve(self, domain: EvidenceDomain, cutoff: datetime) -> ReleaseClosure:
        matches = tuple(
            item
            for item in self._profiles
            if item.domain is domain
            and item.effective_from <= cutoff
            and (item.effective_until is None or cutoff < item.effective_until)
            and item.status in {ReleaseStatus.SHADOW, ReleaseStatus.ACTIVE}
        )
        if len(matches) != 1:
            raise ReleaseResolutionError("exactly one effective profile is required")
        profile = matches[0]
        trajectory = self._trajectories.get(profile.trajectory_release_id)
        if trajectory is None:
            raise ReleaseResolutionError("trajectory release is unavailable")
        digest = sha256(f"{profile.content_hash}\x00{trajectory.content_hash}".encode()).hexdigest()
        return ReleaseClosure(profile=profile, trajectory=trajectory, content_hash=f"sha256:{digest}")
```

- [ ] **Step 4: Run focused tests**

Run: `pytest tests/unit/agents/test_registry.py -v`

Expected: all registry tests pass.

- [ ] **Step 5: Commit closure resolution**

```bash
git add src/trading_os/agents/registry.py tests/unit/agents/test_registry.py
git commit -m "feat(agents): resolve immutable release closures"
```

### Task 3: Effective-dated source applicability and coverage reconciliation

**Files:**
- Create: `src/trading_os/research/source_coverage.py`
- Modify: `src/trading_os/research/watchers.py`
- Test: `tests/unit/research/test_source_coverage.py`

**Interfaces:**
- Consumes: sealed `SourceRecord` and decision cutoff.
- Produces: `SourceChannelPolicy`, `SourceCoveragePolicyRelease`, `SourceCoverageReceipt`, and `reconcile_coverage(...) -> SourceCoverageReceipt`.

- [ ] **Step 1: Write the failing applicability matrix**

```python
@pytest.mark.parametrize(
    ("applicable", "captured", "expected"),
    [
        (("nse",), ("nse",), CoverageStatus.COMPLETE),
        (("bse",), ("bse",), CoverageStatus.COMPLETE),
        (("nse", "bse"), ("nse",), CoverageStatus.DEGRADED),
        (("nse", "bse"), (), CoverageStatus.INSUFFICIENT),
        (("nse",), (), CoverageStatus.INSUFFICIENT),
    ],
)
def test_exchange_applicability_does_not_penalize_single_listing(applicable, captured, expected):
    receipt = reconcile_coverage(policy(applicable), records(captured), CUTOFF)
    assert receipt.status is expected
    assert "bse" not in receipt.missing_channels if applicable == ("nse",) else True


def test_sec_is_not_missing_when_issuer_is_not_sec_applicable() -> None:
    receipt = reconcile_coverage(policy(("nse",), sec_applicable=False), records(("nse",)), CUTOFF)
    assert receipt.status is CoverageStatus.COMPLETE
    assert "sec" in receipt.inapplicable_channels
```

- [ ] **Step 2: Run the test and verify it fails before implementation**

Run: `pytest tests/unit/research/test_source_coverage.py -v`

Expected: collection fails because `source_coverage` is absent.

- [ ] **Step 3: Extend sealed records and implement deterministic reconciliation**

```python
# additions to watchers.py
class SourceRecord(BaseModel, frozen=True):
    record_id: str
    source_id: str
    source_family_id: str
    channel: str
    jurisdiction: str
    published_at: datetime
    available_at: datetime
    received_at: datetime
    kind: str
    is_issuer_submission: bool
    payload_hash: str
    content: str


# source_coverage.py
class SourceChannelPolicy(BaseModel, frozen=True):
    channel: str
    mandatory: bool
    applicable: bool


class SourceCoveragePolicyRelease(BaseModel, frozen=True):
    release_id: str
    effective_from: datetime
    channels: tuple[SourceChannelPolicy, ...]
    content_hash: str


class SourceCoverageReceipt(BaseModel, frozen=True):
    policy_release_id: str
    status: CoverageStatus
    captured_channels: tuple[str, ...]
    missing_channels: tuple[str, ...]
    inapplicable_channels: tuple[str, ...]
    contradictory_record_ids: tuple[str, ...] = ()


def reconcile_coverage(policy, records, cutoff):
    eligible = tuple(record for record in records if record.available_at <= cutoff)
    captured = {record.channel for record in eligible}
    mandatory = {item.channel for item in policy.channels if item.applicable and item.mandatory}
    missing = mandatory - captured
    inapplicable = {item.channel for item in policy.channels if not item.applicable}
    status = CoverageStatus.COMPLETE
    if missing == mandatory and mandatory:
        status = CoverageStatus.INSUFFICIENT
    elif missing:
        status = CoverageStatus.DEGRADED
    return SourceCoverageReceipt(
        policy_release_id=policy.release_id,
        status=status,
        captured_channels=tuple(sorted(captured)),
        missing_channels=tuple(sorted(missing)),
        inapplicable_channels=tuple(sorted(inapplicable)),
    )
```

- [ ] **Step 4: Add contradiction and late-record cases, then run tests**

Add assertions that different normalized material facts from two applicable official families produce `CONTRADICTORY`, while a record whose `available_at > cutoff` remains uncaptured.

Run: `pytest tests/unit/research/test_source_coverage.py -v`

Expected: complete, degraded, insufficient, contradictory, inapplicable, and late-record cases pass.

- [ ] **Step 5: Commit source coverage semantics**

```bash
git add src/trading_os/research/watchers.py src/trading_os/research/source_coverage.py tests/unit/research/test_source_coverage.py
git commit -m "feat(research): reconcile effective source coverage"
```

### Task 4: Recorded SEC, NSE, and BSE corporate-event adapters

**Files:**
- Create: `src/trading_os/research/corporate_event_sources.py`
- Create: `tests/fixtures/research/corporate_events/sec_8k_material_agreement.json`
- Create: `tests/fixtures/research/corporate_events/nse_board_meeting.json`
- Create: `tests/fixtures/research/corporate_events/bse_board_meeting.json`
- Test: `tests/unit/research/test_corporate_event_sources.py`

**Interfaces:**
- Consumes: recorded JSON bytes and deterministic receipt time.
- Produces: `RecordedSec8KAdapter.capture(...)`, `RecordedNseAnnouncementAdapter.capture(...)`, and `RecordedBseAnnouncementAdapter.capture(...)`, each returning a sealed `SourceRecord`.

- [ ] **Step 1: Add minimal recorded fixtures and failing normalization tests**

```json
{
  "accessionNumber": "0000000000-26-000001",
  "cik": "0000000000",
  "form": "8-K",
  "filingDate": "2026-07-22",
  "acceptanceDateTime": "2026-07-22T14:30:00Z",
  "items": ["1.01"],
  "primaryDocument": "event8k.htm",
  "text": "Registrant entered into a material definitive agreement."
}
```

```python
def test_sec_fixture_is_sealed_with_official_channel_and_hash() -> None:
    record = RecordedSec8KAdapter().capture(FIXTURES / "sec_8k_material_agreement.json", RECEIVED)
    assert record.channel == "sec"
    assert record.kind == "8-K"
    assert record.available_at == datetime(2026, 7, 22, 14, 30, tzinfo=UTC)
    assert record.payload_hash.startswith("sha256:")
    assert record.is_issuer_submission is True


def test_nse_and_bse_same_issuer_notice_share_a_source_family() -> None:
    nse = RecordedNseAnnouncementAdapter().capture(NSE_FIXTURE, RECEIVED)
    bse = RecordedBseAnnouncementAdapter().capture(BSE_FIXTURE, RECEIVED)
    assert nse.source_family_id == bse.source_family_id
    assert {nse.channel, bse.channel} == {"nse", "bse"}
```

- [ ] **Step 2: Run tests and verify missing adapter failure**

Run: `pytest tests/unit/research/test_corporate_event_sources.py -v`

Expected: collection fails because the adapter module is absent.

- [ ] **Step 3: Implement strict recorded adapters**

```python
class RecordedCorporateEventAdapter:
    channel: str

    def capture(self, path: Path, received_at: datetime) -> SourceRecord:
        raw = path.read_bytes()
        payload = json.loads(raw)
        normalized = self._normalize(payload)
        digest = sha256(raw).hexdigest()
        return SourceRecord(
            record_id=normalized.record_id,
            source_id=normalized.source_id,
            source_family_id=normalized.source_family_id,
            channel=self.channel,
            jurisdiction=normalized.jurisdiction,
            published_at=normalized.published_at,
            available_at=normalized.available_at,
            received_at=received_at,
            kind=normalized.kind,
            is_issuer_submission=True,
            payload_hash=f"sha256:{digest}",
            content=normalized.content,
        )
```

Each concrete `_normalize()` must reject a missing official identifier, publication/acceptance time, form/category, or content with `RecordedSourceError`; it must not infer the current time.

- [ ] **Step 4: Run adapter and coverage tests together**

Run: `pytest tests/unit/research/test_corporate_event_sources.py tests/unit/research/test_source_coverage.py -v`

Expected: all tests pass without network access.

- [ ] **Step 5: Commit recorded source adapters**

```bash
git add src/trading_os/research/corporate_event_sources.py tests/fixtures/research/corporate_events tests/unit/research/test_corporate_event_sources.py
git commit -m "feat(research): add recorded SEC NSE and BSE event adapters"
```

### Task 5: Snapshot-scoped capability registry

**Files:**
- Create: `src/trading_os/agents/capabilities.py`
- Test: `tests/unit/agents/test_capabilities.py`

**Interfaces:**
- Consumes: source records, `data_snapshot_id`, question source IDs, profile grants, node grants.
- Produces: `ToolCapabilityRelease`, `CapabilityBinding`, `BoundCapabilities.query_source_records(...)`, and `CapabilityDenied`.

- [ ] **Step 1: Write failing intersection and citation-scope tests**

```python
async def test_binding_exposes_only_profile_node_and_snapshot_intersection(records) -> None:
    bound = registry.bind(
        CapabilityBinding(
            profile_release_id="profile:corporate-event:v1",
            node_id="gather",
            profile_capability_ids=(SOURCE_QUERY_ID,),
            node_capability_ids=(SOURCE_QUERY_ID,),
            source_record_ids=(records[0].record_id,),
            data_snapshot_id="snapshot:1",
        )
    )
    result = await bound.query_source_records((records[0].record_id, records[1].record_id))
    assert tuple(item.record_id for item in result) == (records[0].record_id,)


async def test_ungranted_capability_fails_closed(records) -> None:
    with pytest.raises(CapabilityDenied):
        await no_grants.query_source_records((records[0].record_id,))
```

- [ ] **Step 2: Run tests and verify the missing module failure**

Run: `pytest tests/unit/agents/test_capabilities.py -v`

Expected: collection fails because `capabilities.py` does not exist.

- [ ] **Step 3: Implement immutable capability releases and bound proxies**

```python
class ToolCapabilityRelease(BaseModel, frozen=True):
    release_id: str
    operation: str
    input_schema_id: str
    output_schema_id: str
    read_only: bool
    max_result_bytes: int = Field(gt=0)


class CapabilityBinding(BaseModel, frozen=True):
    profile_release_id: str
    node_id: str
    profile_capability_ids: tuple[str, ...]
    node_capability_ids: tuple[str, ...]
    source_record_ids: tuple[str, ...]
    data_snapshot_id: str


class BoundCapabilities:
    async def query_source_records(self, record_ids: tuple[str, ...]) -> tuple[SourceRecord, ...]:
        self._require(SOURCE_RECORD_QUERY)
        allowed = set(self._binding.source_record_ids)
        return tuple(self._records[item] for item in record_ids if item in allowed)
```

The registry must reject any release with `read_only=False`, duplicate operation names, an implementation without a fixture adapter, or a binding whose profile/node intersection is empty.

- [ ] **Step 4: Run capability tests and type checking**

Run: `pytest tests/unit/agents/test_capabilities.py -v && mypy src/trading_os/agents/capabilities.py`

Expected: tests pass and mypy reports success.

- [ ] **Step 5: Commit capability containment**

```bash
git add src/trading_os/agents/capabilities.py tests/unit/agents/test_capabilities.py
git commit -m "feat(agents): bind snapshot-scoped read-only capabilities"
```

### Task 6: Provider-neutral LLM role and deterministic adapters

**Files:**
- Modify: `pyproject.toml`
- Create: `src/trading_os/agents/llm.py`
- Create: `src/trading_os/agents/providers.py`
- Test: `tests/contract/agents/__init__.py`
- Test: `tests/contract/agents/llm_role_contract.py`
- Test: `tests/contract/agents/test_fixture_llm_role.py`
- Test: `tests/contract/agents/test_openai_llm_role.py`
- Test: `tests/contract/agents/test_anthropic_llm_role.py`

**Interfaces:**
- Consumes: typed structured invocation and Pydantic output schema.
- Produces: `LLMRole.invoke(invocation) -> StructuredResult | ExpectedLLMFailure`, plus fixture, OpenAI, and Anthropic adapters.

- [ ] **Step 1: Add the contract tests first**

```python
class LLMRoleContract:
    def build_role(self) -> LLMRole: ...

    async def test_valid_structured_output(self) -> None:
        result = await self.build_role().invoke(invocation_for(EventExtraction))
        assert isinstance(result, StructuredResult)
        assert isinstance(result.output, EventExtraction)

    async def test_malformed_output_is_expected_failure(self) -> None:
        result = await self.build_role().invoke(malformed_invocation(EventExtraction))
        assert result == ExpectedLLMFailure(kind="malformed_output", retryable=False)

    async def test_hosted_tools_are_never_requested(self) -> None:
        request = invocation_for(EventExtraction)
        assert request.allowed_capability_names == ("source_record_query",)
```

- [ ] **Step 2: Run the fixture contract and verify failure**

Run: `pytest tests/contract/agents/test_fixture_llm_role.py -v`

Expected: collection fails because `trading_os.agents.llm` does not exist.

- [ ] **Step 3: Implement the owned role interface and fixture adapter**

```python
T = TypeVar("T", bound=BaseModel)


class StructuredInvocation(BaseModel, Generic[T], frozen=True):
    invocation_id: str
    role: str
    prompt_release_id: str
    trusted_context: dict[str, str]
    source_record_ids: tuple[str, ...]
    output_type: type[T]
    allowed_capability_names: tuple[str, ...]
    max_tokens: int
    replay_key: str


class StructuredResult(BaseModel, Generic[T], frozen=True):
    output: T
    provider: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    finish_reason: str
    replay_key: str


class ExpectedLLMFailure(BaseModel, frozen=True):
    kind: Literal["timeout", "refusal", "unsupported", "malformed_output", "budget"]
    retryable: bool


class LLMRole(Protocol):
    async def invoke(self, invocation: StructuredInvocation[T]) -> StructuredResult[T] | ExpectedLLMFailure: ...


class FixtureLLMRole:
    def __init__(self, results: dict[str, BaseModel | ExpectedLLMFailure]) -> None:
        self._results = results

    async def invoke(self, invocation):
        return StructuredResult.from_fixture(invocation, self._results[invocation.replay_key])
```

- [ ] **Step 4: Add provider dependencies and adapters behind the same contract**

Add to `pyproject.toml`:

```toml
  "anthropic>=0.117,<0.118",
  "openai>=2.46,<2.47",
```

`OpenAILLMRole` and `AnthropicLLMRole` must accept injected async clients, request structured output only, set provider tracing/data retention controls to the strictest supported values, normalize usage, and map SDK exceptions to `ExpectedLLMFailure`. Contract tests use fake injected clients; they do not require credentials or network.

Run: `pytest tests/contract/agents -v`

Expected: fixture, OpenAI, and Anthropic adapters pass the same contract.

- [ ] **Step 5: Commit the provider boundary**

```bash
git add pyproject.toml src/trading_os/agents/llm.py src/trading_os/agents/providers.py tests/contract/agents
git commit -m "feat(agents): add provider-neutral structured LLM role"
```

### Task 7: Canonical append-only agent run ledger

**Files:**
- Create: `src/trading_os/agents/ledger.py`
- Test: `tests/unit/agents/test_ledger.py`

**Interfaces:**
- Consumes: deterministic `run_id`, release closure, snapshot scope, ordered node/tool/model events.
- Produces: `AgentRunEvent`, `AgentRunLedger.append(...)`, `events_for(run_id)`, and `LedgerUnavailable`.

- [ ] **Step 1: Write failing append-only and reconciliation tests**

```python
async def test_ledger_is_append_only_and_sequence_checked() -> None:
    ledger = InMemoryAgentRunLedger()
    await ledger.append(event("run:1", sequence=0, kind="run_started"))
    await ledger.append(event("run:1", sequence=1, kind="node_started"))
    with pytest.raises(LedgerConflict):
        await ledger.append(event("run:1", sequence=1, kind="node_finished"))


async def test_checkpoint_must_reconcile_with_ledger_hash() -> None:
    ledger = InMemoryAgentRunLedger()
    await ledger.append(event("run:1", sequence=0, kind="run_started", artifact_hash="sha256:a"))
    with pytest.raises(LedgerConflict, match="checkpoint does not match canonical ledger"):
        await ledger.reconcile("run:1", checkpoint_sequence=0, artifact_hash="sha256:b")
```

- [ ] **Step 2: Run tests and verify missing ledger failure**

Run: `pytest tests/unit/agents/test_ledger.py -v`

Expected: collection fails because the agent ledger module is absent.

- [ ] **Step 3: Implement the protocol and deterministic in-memory ledger**

```python
class AgentRunEvent(BaseModel, frozen=True):
    run_id: str
    sequence: int = Field(ge=0)
    kind: str
    release_closure_hash: str
    data_snapshot_id: str
    source_record_ids: tuple[str, ...]
    artifact_hash: str | None = None


class AgentRunLedger(Protocol):
    async def append(self, event: AgentRunEvent) -> None: ...
    async def events_for(self, run_id: str) -> tuple[AgentRunEvent, ...]: ...


class InMemoryAgentRunLedger:
    async def append(self, event: AgentRunEvent) -> None:
        stream = self._streams.setdefault(event.run_id, [])
        if event.sequence != len(stream):
            raise LedgerConflict("agent run sequence conflict")
        stream.append(event)
```

- [ ] **Step 4: Run ledger tests**

Run: `pytest tests/unit/agents/test_ledger.py -v`

Expected: append, conflict, replay, and reconciliation cases pass.

- [ ] **Step 5: Commit the canonical ledger seam**

```bash
git add src/trading_os/agents/ledger.py tests/unit/agents/test_ledger.py
git commit -m "feat(agents): add canonical append-only run ledger"
```

### Task 8: Trajectory compiler and contained LangGraph engine

**Files:**
- Modify: `pyproject.toml`
- Create: `src/trading_os/agents/trajectory.py`
- Create: `src/trading_os/agents/langgraph_engine.py`
- Test: `tests/contract/agents/trajectory_engine_contract.py`
- Test: `tests/contract/agents/test_langgraph_engine.py`

**Interfaces:**
- Consumes: `TrajectoryRelease`, registered project node handlers, invocation state, canonical ledger.
- Produces: opaque `CompiledTrajectory`, `TrajectoryCompiler.compile(...)`, and `TrajectoryEngine.execute(...) -> TrajectoryResult`.

- [ ] **Step 1: Write compiler and engine contract tests**

```python
def test_compiler_rejects_terminal_path_without_seam_and_admission() -> None:
    with pytest.raises(TrajectoryCompileError, match="terminal path must cross categorical seam and admission"):
        compiler.compile(unsafe_trajectory())


async def test_engine_runs_deterministic_node_between_agent_loops() -> None:
    result = await engine.execute(compiled_corporate_event_trajectory(), invocation())
    assert result.visited_node_ids == (
        "gather", "normalize", "validate", "judge", "reconcile", "categorical_seam", "admission"
    )
```

- [ ] **Step 2: Run tests and verify missing compiler failure**

Run: `pytest tests/contract/agents/test_langgraph_engine.py -v`

Expected: collection fails because the trajectory modules are absent.

- [ ] **Step 3: Add LangGraph and implement the project-owned compiler seam**

Add to `pyproject.toml`:

```toml
  "langgraph>=1.2.9,<1.3",
```

```python
class CompiledTrajectory:
    def __init__(self, release_id: str, graph: object) -> None:
        self.release_id = release_id
        self._graph = graph


class TrajectoryInvocation(BaseModel, frozen=True):
    run_id: str
    question_id: str
    release_closure_hash: str
    data_snapshot_id: str
    source_record_ids: tuple[str, ...]


class TrajectoryResult(BaseModel, frozen=True):
    packet: EvidencePacket
    visited_node_ids: tuple[str, ...]
    artifact_hash: str


class TrajectoryCompiler:
    def compile(self, release: TrajectoryRelease) -> CompiledTrajectory:
        self._validate_terminal_paths(release)
        self._validate_capabilities(release)
        return self._engine.compile(release, self._node_registry)


class TrajectoryEngine(Protocol):
    async def execute(self, compiled: CompiledTrajectory, invocation: TrajectoryInvocation) -> TrajectoryResult: ...
```

`LangGraphTrajectoryEngine` privately builds `StateGraph`, uses node IDs from the release, wraps every handler with ledger start/finish/failure events, and never returns LangGraph state or checkpoint objects.

- [ ] **Step 4: Add resume-at-every-boundary contract cases**

Parameterize a test over all seven node boundaries. Inject a crash, resume with the same run ID and release closure, and assert that completed node effects are not duplicated and the final packet hash is identical.

Run: `pytest tests/contract/agents/test_langgraph_engine.py -v`

Expected: compile, execution order, crash/resume, ledger mismatch, and replay tests pass.

- [ ] **Step 5: Commit the contained graph engine**

```bash
git add pyproject.toml src/trading_os/agents/trajectory.py src/trading_os/agents/langgraph_engine.py tests/contract/agents/trajectory_engine_contract.py tests/contract/agents/test_langgraph_engine.py
git commit -m "feat(agents): compile governed trajectories to LangGraph"
```

### Task 9: Corporate-event gather, normalize, judge, and reconciliation nodes

**Files:**
- Create: `src/trading_os/agents/corporate_events.py`
- Create: `src/trading_os/agents/profiles.py`
- Test: `tests/unit/agents/test_corporate_event_nodes.py`

**Interfaces:**
- Consumes: bound source query capability, `LLMRole`, `SourceCoverageReceipt`.
- Produces: `EventExtraction`, `NormalizedCorporateEvent`, `EventJudgement`, registered node handlers, and `corporate_event_profile_releases()`.

- [ ] **Step 1: Write failing node-level behavior tests**

```python
async def test_normalizer_sits_between_gather_and_judge() -> None:
    gathered = EventExtraction(event_type="material_agreement", record_ids=("sec:1",), issuer_id="issuer:1")
    normalized = normalize_event(gathered, cutoff=CUTOFF)
    assert normalized.channel_families == ("issuer:1:material_agreement:2026-07-22",)
    judged = await judge_event(normalized, fixture_role)
    assert judged.assessment == "material_event_supported"


def test_degraded_and_contradictory_evidence_are_not_supportive() -> None:
    assert reconcile_judgement(judgement(), degraded_receipt()).eligibility_effect == "neutral"
    assert reconcile_judgement(judgement(), contradictory_receipt()).eligibility_effect == "neutral"
```

- [ ] **Step 2: Run tests and verify missing node module failure**

Run: `pytest tests/unit/agents/test_corporate_event_nodes.py -v`

Expected: collection fails because `corporate_events.py` does not exist.

- [ ] **Step 3: Implement typed node artifacts and handlers**

```python
class EventExtraction(BaseModel, frozen=True):
    event_type: str
    record_ids: tuple[str, ...]
    issuer_id: str
    stated_effective_at: datetime | None = None


class NormalizedCorporateEvent(BaseModel, frozen=True):
    event_type: str
    issuer_id: str
    record_ids: tuple[str, ...]
    channel_families: tuple[str, ...]
    within_cutoff: bool


class EventJudgement(BaseModel, frozen=True):
    assessment: str
    support_record_ids: tuple[str, ...]
    contradiction_record_ids: tuple[str, ...]
    missing: tuple[str, ...]


class CorporateEventDraft(BaseModel, frozen=True):
    assessment: str
    support_record_ids: tuple[str, ...]
    contradiction_record_ids: tuple[str, ...]
    missing: tuple[str, ...]
    eligibility_effect: str


def reconcile_judgement(judgement, coverage):
    effect = "supportive" if coverage.status is CoverageStatus.COMPLETE and not judgement.contradiction_record_ids else "neutral"
    return CorporateEventDraft(
        assessment=judgement.assessment,
        support_record_ids=judgement.support_record_ids,
        contradiction_record_ids=judgement.contradiction_record_ids,
        missing=tuple(sorted(set(judgement.missing) | set(coverage.missing_channels))),
        eligibility_effect=effect,
    )
```

- [ ] **Step 4: Define the immutable P0 trajectory and profile releases**

`corporate_event_profile_releases()` must build this exact node order:

```python
(
    ("gather", NodeKind.AGENT_LOOP),
    ("normalize", NodeKind.DETERMINISTIC_TRANSFORM),
    ("validate", NodeKind.VALIDATION),
    ("judge", NodeKind.JUDGE),
    ("reconcile", NodeKind.DETERMINISTIC_TRANSFORM),
    ("categorical_seam", NodeKind.CATEGORICAL_SEAM),
    ("admission", NodeKind.ADMISSION),
)
```

Run: `pytest tests/unit/agents/test_corporate_event_nodes.py -v`

Expected: node semantics and release-shape tests pass.

- [ ] **Step 5: Commit the domain profile**

```bash
git add src/trading_os/agents/corporate_events.py src/trading_os/agents/profiles.py tests/unit/agents/test_corporate_event_nodes.py
git commit -m "feat(agents): define corporate-event tracer trajectory"
```

### Task 10: Generic DomainAgentHarness and compatibility mapping

**Files:**
- Create: `src/trading_os/agents/harness.py`
- Modify: `src/trading_os/research/orchestrator.py`
- Test: `tests/unit/agents/test_harness.py`
- Test: `tests/integration/research/test_corporate_event_tracer.py`

**Interfaces:**
- Consumes: release registry, compiler/engine, LLM role, capability registry, coverage reconciler, ledger.
- Produces: `DomainAgentHarness.investigate(question) -> EvidencePacket | None`, implementing the unchanged `ResearchAgentPort`.

- [ ] **Step 1: Write the full compatibility matrix before the harness**

```python
@pytest.mark.parametrize(
    ("case", "expected_assessment", "expected_effect"),
    [
        ("nse_only_complete", "material_event_supported", "supportive"),
        ("bse_only_complete", "material_event_supported", "supportive"),
        ("dual_listed_one_missing", "material_event_supported_degraded", "neutral"),
        ("sec_not_applicable", "material_event_supported", "supportive"),
        ("all_mandatory_missing", "missing_applicable_official_sources", "neutral"),
        ("official_conflict", "contradictory_official_sources", "neutral"),
        ("late_record", "missing_applicable_official_sources", "neutral"),
        ("provider_timeout", "agent_provider_timeout", "neutral"),
        ("malformed_output", "agent_malformed_output", "neutral"),
        ("budget_exhausted", "agent_budget_exhausted", "neutral"),
    ],
)
async def test_corporate_event_compatibility_matrix(case, expected_assessment, expected_effect, harness_factory):
    packet = await harness_factory(case).investigate(question_for(case))
    assert packet is not None
    assert packet.assessment == expected_assessment
    assert packet.eligibility_effect == expected_effect
    assert set(packet.source_record_ids).issubset(question_for(case).source_record_ids)
```

- [ ] **Step 2: Run integration tests and verify missing harness failure**

Run: `pytest tests/unit/agents/test_harness.py tests/integration/research/test_corporate_event_tracer.py -v`

Expected: collection fails because `DomainAgentHarness` does not exist.

- [ ] **Step 3: Implement one generic harness and explicit missing packet construction**

```python
class DomainAgentHarness(ResearchAgentPort):
    async def investigate(self, question: ResearchQuestion) -> EvidencePacket | None:
        run_id = deterministic_run_id(question)
        try:
            closure = self._releases.resolve(question.domain, question.cutoff)
            await self._ledger.append(run_started(run_id, question, closure))
            bound = self._capabilities.bind(binding_for(question, closure))
            compiled = self._compiler.compile(closure.trajectory)
            result = await self._engine.execute(
                compiled,
                invocation_for(run_id, question, closure, bound, self._llm),
            )
            packet = result.packet
        except ExpectedAgentFailure as failure:
            packet = explicit_missing_packet(question, failure)
        except (LedgerUnavailable, ReleaseResolutionError):
            return None
        return admit_packet(packet, question)
```

Keep `ResearchQuestion`, `ResearchAgentPort`, and `ResearchOrchestrator.run()` signatures unchanged. Replace the broad `except Exception` comment with the explicit rule that catastrophic port failure remains `None`; expected model/tool/budget failures are handled inside the harness.

- [ ] **Step 4: Prove admission, seam rejection, and relational fallback**

Add cases where a malicious model result includes `target_price`, cites an out-of-scope record, or changes the instrument. Each must become an admitted explicit-missing packet and a safety ledger event. Then run:

Run: `pytest tests/unit/research tests/unit/agents tests/integration/research tests/integration/ontology/test_relational_fallback.py -v`

Expected: all tests pass and the relational fallback test is unchanged.

- [ ] **Step 5: Commit the vertical tracer**

```bash
git add src/trading_os/agents/harness.py src/trading_os/research/orchestrator.py tests/unit/agents/test_harness.py tests/integration/research/test_corporate_event_tracer.py
git commit -m "feat(agents): add compatible domain agent harness tracer"
```

### Task 11: Replay identity and shadow-only application composition

**Files:**
- Create: `src/trading_os/agents/composition.py`
- Modify: `src/trading_os/app/container.py`
- Modify: `src/trading_os/app/settings.py`
- Test: `tests/integration/agents/test_replay.py`
- Test: `tests/integration/app/test_agent_shadow_composition.py`

**Interfaces:**
- Consumes: recorded source/model/tool fixtures and frozen release closure.
- Produces: `build_shadow_domain_agent(...) -> ResearchAgentPort` and a disabled-by-default shadow configuration.

- [ ] **Step 1: Write failing production/replay caller-parity tests**

```python
async def test_production_and_replay_use_the_same_port_call() -> None:
    production: ResearchAgentPort = build_shadow_domain_agent(production_dependencies())
    replay: ResearchAgentPort = build_shadow_domain_agent(replay_dependencies())
    production_packet = await production.investigate(QUESTION)
    replay_packet = await replay.investigate(QUESTION)
    assert production_packet == replay_packet


def test_agent_shadow_mode_is_disabled_by_default() -> None:
    assert Settings().agent_shadow_enabled is False
```

- [ ] **Step 2: Run tests and verify missing composition failure**

Run: `pytest tests/integration/agents/test_replay.py tests/integration/app/test_agent_shadow_composition.py -v`

Expected: collection fails because `build_shadow_domain_agent` is absent.

- [ ] **Step 3: Implement dependency-only composition**

```python
def build_shadow_domain_agent(deps: DomainAgentDependencies) -> ResearchAgentPort:
    return DomainAgentHarness(
        releases=deps.releases,
        compiler=deps.compiler,
        engine=deps.engine,
        capabilities=deps.capabilities,
        llm=deps.llm,
        ledger=deps.ledger,
    )
```

Add `agent_shadow_enabled: bool = False` and provider credentials as optional secret settings. The application container must not construct a harness or client unless shadow mode is explicitly enabled.

- [ ] **Step 4: Run replay twice and compare packet plus ledger hashes**

Run: `pytest tests/integration/agents/test_replay.py -v && pytest tests/integration/agents/test_replay.py -v`

Expected: both executions pass with the same expected packet and canonical event hashes.

- [ ] **Step 5: Commit shadow composition**

```bash
git add src/trading_os/agents/composition.py src/trading_os/app/container.py src/trading_os/app/settings.py tests/integration/agents/test_replay.py tests/integration/app/test_agent_shadow_composition.py
git commit -m "feat(app): compose shadow-only domain agent tracer"
```

### Task 12: P0 verification and operator-readable evidence

**Files:**
- Create: `docs/operations/domain-agent-shadow-runbook.md`
- Modify: `docs/superpowers/specs/2026-07-23-domain-agent-architecture.md`
- Test: `tests/integration/agents/test_p0_acceptance.py`

**Interfaces:**
- Consumes: completed P0 tracer.
- Produces: executable acceptance test and operator runbook explaining complete, degraded, contradictory, insufficient, and catastrophic outcomes.

- [ ] **Step 1: Add one acceptance test covering the entire fixture matrix**

```python
async def test_p0_fixture_matrix_is_offline_deterministic(p0_cases) -> None:
    for case in p0_cases:
        first = await case.harness.investigate(case.question)
        second = await case.replay_harness.investigate(case.question)
        assert first == second
        assert case.expected_status in first.assessment
        assert set(first.source_record_ids).issubset(case.question.source_record_ids)
```

- [ ] **Step 2: Write the shadow-run runbook with exact interpretation rules**

Document:

```text
complete       all applicable mandatory official channels captured
degraded       at least one applicable official channel captured and at least one missing
contradictory  material official statements conflict; no positive influence
insufficient   all applicable mandatory official channels missing; no positive influence
catastrophic   release closure or canonical ledger unavailable; port returns None
inapplicable   source is not expected for this issuer/listing at the cutoff
```

Include the exact offline test command and state that shadow output cannot activate decisions or create orders.

- [ ] **Step 3: Run the P0 acceptance and existing compatibility suites**

Run: `pytest tests/unit tests/contract tests/integration/agents tests/integration/research tests/integration/ontology/test_relational_fallback.py -v`

Expected: all non-database tests pass; no test requires provider credentials or network.

- [ ] **Step 4: Run repository quality checks**

Run: `ruff check src tests && mypy src && git diff --check`

Expected: all commands exit zero.

- [ ] **Step 5: Commit verified P0 documentation**

```bash
git add docs/operations/domain-agent-shadow-runbook.md docs/superpowers/specs/2026-07-23-domain-agent-architecture.md tests/integration/agents/test_p0_acceptance.py
git commit -m "docs(agents): verify P0 corporate-event tracer"
```

## P0 completion gate

P0 is complete only when the recorded fixture matrix passes through the unchanged `ResearchAgentPort`, every expected failure returns admitted missing evidence, only ledger/release catastrophe returns `None`, replay produces identical packet and ledger hashes, and the existing relational fallback remains green.

The bounded framework experiments are specified in [Domain Agent Framework Spikes](2026-07-23-domain-agent-framework-spikes.md). They consume the interfaces delivered here and cannot widen them.

## Specification coverage

| Approved specification area | Implemented by |
|---|---|
| unchanged port and explicit failure compatibility | Tasks 10–12 |
| immutable desired state and exact release closure | Tasks 1–2 |
| effective source applicability and watcher evolution foundation | Tasks 3–4 |
| node-scoped read-only capabilities | Task 5 |
| provider-neutral model boundary | Task 6 |
| canonical ledger and replay | Tasks 7–8 and 11 |
| deterministic nodes between bounded agent loops | Tasks 8–9 |
| SEC/NSE/BSE corporate-event tracer | Tasks 4 and 9–12 |
| admission, categorical seam, and permanent relational champion | Tasks 10 and 12 |
| shadow-only rollout | Tasks 11–12 |

The remaining nine domain profiles and graphical workbench are P1 subprojects in the approved rollout. Their plan boundaries depend on the P0 release, trajectory, status, and run-projection semantics proven here; they do not block this tracer from starting.

## P1 gaps identified after P0 (2026-07-24)

Walking the P0 tracer against a real event (Tanla Platforms announcing quarterly results, with a next-session re-rate) surfaced two gaps between what P0 proved and what a live event-reactive swing OS needs:

1. **Live NSE/BSE SourceWatcher connector.** P0 ships only `FixtureSourceWatcher` (offline) and recorded SEC/NSE/BSE adapters. There is no live poller that captures an official announcement on a schedule, so a real filing is only seen if hand-fed. The cutoff/coverage/sealing discipline is correct; the live fetch is missing. **Designed** in [Live NSE/BSE SourceWatcher + Early-Signal Tier](../specs/2026-07-24-live-source-watcher-design.md) — official announcement connector (evidence-bearing) + early-signal calendar tier (attention-only) + a committed credible-source catalog. In progress.

2. **`fundamental` domain profile.** A results announcement is both a `corporate_event` (P0 handles this — "material results announcement") and a `fundamental` analysis of the reported numbers (revenue, margin, YoY). Only `corporate_event` is implemented; the `fundamental` profile that reads the numbers inside the filing is not. **Deferred** — one of the nine P1 profiles; not being built in the live-watcher phase.
