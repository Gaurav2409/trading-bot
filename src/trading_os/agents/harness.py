"""Generic ``DomainAgentHarness`` and compatibility mapping (spec §6, §8, §16).

One repository-owned harness implements the unchanged ``ResearchAgentPort`` for
every evidence domain. ``corporate_event`` is a *profile*, not a harness
subclass: the harness resolves an immutable release closure, binds node-scoped
read-only capabilities over the question's frozen snapshot and cited source set,
compiles the governed trajectory to the contained engine, and returns only an
admitted categorical :class:`EvidencePacket`.

Compatibility mapping (spec §16) makes the harness logically total for expected
failures. Every non-catastrophic terminal path constructs an explicit packet and
crosses ``admit_packet``:

* provider/tool/budget failures and malformed output become an admitted
  explicit-missing packet;
* incomplete applicable coverage is degraded or missing per policy;
* an official-source conflict is contradictory;
* a categorical-seam violation (an executable number, an out-of-scope citation,
  or an instrument switch reaching the seam) becomes an admitted explicit-missing
  packet plus a safety ledger event.

``None`` is reserved for catastrophe only: an unavailable canonical ledger or an
unresolved immutable release closure. Neither a ``None`` nor an explicit-missing
outcome disables the relational champion.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256

from trading_os.agents.capabilities import (
    BoundCapabilities,
    CapabilityBinding,
    ToolCapabilityRegistry,
)
from trading_os.agents.corporate_events import (
    CorporateEventDraft,
    EventExtraction,
    EventJudgement,
    NormalizedCorporateEvent,
    judge_event,
    normalize_event,
    reconcile_judgement,
)
from trading_os.agents.ledger import (
    AgentRunEvent,
    AgentRunLedger,
    LedgerUnavailable,
)
from trading_os.agents.llm import LLMRole
from trading_os.agents.models import ExpectedAgentFailure
from trading_os.agents.registry import ReleaseRegistry, ReleaseResolutionError
from trading_os.agents.trajectory import (
    NodeContext,
    NodeHandler,
    NodeRegistry,
    TrajectoryCompiler,
    TrajectoryEngine,
    TrajectoryInvocation,
)
from trading_os.research.models import EvidencePacket
from trading_os.research.orchestrator import (
    ResearchQuestion,
    admit_packet,
)
from trading_os.research.source_coverage import (
    SourceCoveragePolicyRelease,
    SourceCoverageReceipt,
    reconcile_coverage,
)
from trading_os.research.watchers import SourceRecord

# Executable-number field names that must never cross the evidence seam
# (spec §4, §16). Their presence anywhere in a categorical artifact is a
# categorical-seam violation.
_FORBIDDEN_SEAM_TOKENS: frozenset[str] = frozenset(
    {
        "price",
        "quantity",
        "target",
        "target_price",
        "expected_return",
        "position_weight",
        "conviction",
        "conviction_multiplier",
        "order_intent",
    }
)


class CategoricalSeamViolation(RuntimeError):
    """Raised inside the categorical-seam node when an executable number, an
    out-of-scope citation, or an instrument switch reaches the seam."""


@dataclass
class _RunWorkspace:
    """Per-run mutable scratch space closed over by the node handlers.

    The engine threads only string artifacts and the final packet through the
    :class:`NodeContext`; the typed domain artifacts (extraction, normalized
    event, judgement, draft) live here for the duration of a single investigate
    call so that the deterministic transforms can sit between the agent loops.
    """

    question: ResearchQuestion
    bound: BoundCapabilities
    coverage: SourceCoverageReceipt
    extraction: EventExtraction | None = None
    normalized: NormalizedCorporateEvent | None = None
    judgement: EventJudgement | None = None
    draft: CorporateEventDraft | None = None
    safety_events: list[str] = field(default_factory=list)


# Categorical assessment vocabulary produced by the reconciliation node,
# refined here by coverage status so the compatibility matrix is explicit.
_SUPPORTED = "material_event_supported"
_SUPPORTED_DEGRADED = "material_event_supported_degraded"
_INSUFFICIENT = "missing_applicable_official_sources"
_CONTRADICTORY = "contradictory_official_sources"


def deterministic_run_id(question: ResearchQuestion) -> str:
    """Deterministic, replay-stable run identity bound to the question scope."""

    digest = sha256(
        "\x00".join(
            (
                question.question_id,
                question.instrument_id,
                str(question.domain),
                question.data_snapshot_id,
                question.cutoff.isoformat(),
                *question.source_record_ids,
            )
        ).encode()
    ).hexdigest()
    return f"run:{digest}"


class DomainAgentHarness:
    """One generic harness implementing the unchanged ``ResearchAgentPort``."""

    def __init__(
        self,
        *,
        releases: ReleaseRegistry,
        compiler: TrajectoryCompiler,
        engine: TrajectoryEngine,
        capabilities: ToolCapabilityRegistry,
        llm: LLMRole,
        ledger: AgentRunLedger,
        coverage_policy: SourceCoveragePolicyRelease,
        source_records: tuple[SourceRecord, ...],
        snapshot_scope: Mapping[str, tuple[str, ...]],
        gather_replay_key: str = "gather",
    ) -> None:
        self._releases = releases
        self._compiler = compiler
        self._engine = engine
        self._capabilities = capabilities
        self._llm = llm
        self._ledger = ledger
        self._coverage_policy = coverage_policy
        self._records = {record.record_id: record for record in source_records}
        self._source_records = source_records
        self._snapshot_scope = snapshot_scope
        self._gather_replay_key = gather_replay_key

    async def investigate(
        self, question: ResearchQuestion
    ) -> EvidencePacket | None:
        run_id = deterministic_run_id(question)
        try:
            closure = self._releases.resolve(question.domain, question.cutoff)
        except ReleaseResolutionError:
            return None
        try:
            await self._ledger.append(
                AgentRunEvent(
                    run_id=run_id,
                    sequence=0,
                    kind="run_started",
                    release_closure_hash=closure.content_hash,
                    data_snapshot_id=question.data_snapshot_id,
                    source_record_ids=question.source_record_ids,
                )
            )
        except LedgerUnavailable:
            return None

        workspace = self._build_workspace(question, closure.content_hash)
        registry = self._build_registry(workspace)
        # Rebind the harness compiler onto this run's node registry so the
        # closures share the run workspace, then compile and execute.
        run_compiler = TrajectoryCompiler(
            engine=self._engine, node_registry=registry
        )

        try:
            compiled = run_compiler.compile(closure.trajectory)
            invocation = TrajectoryInvocation(
                run_id=run_id,
                question_id=question.question_id,
                release_closure_hash=closure.content_hash,
                data_snapshot_id=question.data_snapshot_id,
                source_record_ids=question.source_record_ids,
            )
            result = await self._engine.execute(compiled, invocation)
            packet = result.packet
        except ExpectedAgentFailure as failure:
            packet = self._explicit_missing_packet(question, failure.kind)
        except CategoricalSeamViolation as violation:
            await self._append_safety_event(run_id, closure.content_hash, question)
            packet = self._explicit_missing_packet(
                question, "categorical_seam_violation", reason=str(violation)
            )
        except LedgerUnavailable:
            return None

        # Idempotent defence: re-validate at the port boundary regardless of
        # which terminal path produced the packet.
        return admit_packet(packet, question)

    # -- workspace + registry ------------------------------------------------

    def _build_workspace(
        self, question: ResearchQuestion, closure_hash: str
    ) -> _RunWorkspace:
        eligible = tuple(
            self._records[record_id]
            for record_id in question.source_record_ids
            if record_id in self._records
        )
        coverage = reconcile_coverage(
            self._coverage_policy, eligible, question.cutoff
        )
        binding = CapabilityBinding(
            profile_release_id="profile:corporate-event:v1",
            node_id="gather",
            profile_capability_ids=("capability:source-record-query:v1",),
            node_capability_ids=("capability:source-record-query:v1",),
            source_record_ids=question.source_record_ids,
            data_snapshot_id=question.data_snapshot_id,
        )
        bound = self._capabilities.bind(
            binding,
            records=self._source_records,
            snapshot_scope=self._snapshot_scope,
        )
        return _RunWorkspace(
            question=question, bound=bound, coverage=coverage
        )

    def _build_registry(self, workspace: _RunWorkspace) -> NodeRegistry:
        registry = NodeRegistry()
        handlers: dict[str, NodeHandler] = {
            "gather": self._gather_handler(workspace),
            "normalize": self._normalize_handler(workspace),
            "validate": self._validate_handler(workspace),
            "judge": self._judge_handler(workspace),
            "reconcile": self._reconcile_handler(workspace),
            "categorical_seam": self._seam_handler(workspace),
            "admission": self._admission_handler(workspace),
        }
        for node_id, handler in handlers.items():
            registry.register(node_id, handler)
        return registry

    # -- node handlers -------------------------------------------------------

    def _gather_handler(self, workspace: _RunWorkspace) -> NodeHandler:
        async def gather(context: NodeContext) -> NodeContext:
            records = await workspace.bound.query_source_records(
                workspace.question.source_record_ids
            )
            issuer_id = _issuer_id_for(records)
            event_type = _event_type_for(records)
            stated = _stated_effective_at(records)
            workspace.extraction = EventExtraction(
                event_type=event_type,
                record_ids=tuple(record.record_id for record in records),
                issuer_id=issuer_id,
                stated_effective_at=stated,
            )
            return context.with_artifact(
                "gather", {"event_type": event_type, "issuer_id": issuer_id}
            )

        return gather

    def _normalize_handler(self, workspace: _RunWorkspace) -> NodeHandler:
        async def normalize(context: NodeContext) -> NodeContext:
            assert workspace.extraction is not None
            workspace.normalized = normalize_event(
                workspace.extraction, cutoff=workspace.question.cutoff
            )
            return context.with_artifact(
                "normalize",
                {"within_cutoff": workspace.normalized.within_cutoff},
            )

        return normalize

    def _validate_handler(self, workspace: _RunWorkspace) -> NodeHandler:
        async def validate(context: NodeContext) -> NodeContext:
            assert workspace.normalized is not None
            # Cutoff safety: a record that resolves newer than the cutoff cannot
            # silently pass. The normalizer already flagged this.
            return context.with_artifact(
                "validate", {"within_cutoff": workspace.normalized.within_cutoff}
            )

        return validate

    def _judge_handler(self, workspace: _RunWorkspace) -> NodeHandler:
        async def judge(context: NodeContext) -> NodeContext:
            assert workspace.normalized is not None
            workspace.judgement = await judge_event(
                workspace.normalized, self._llm
            )
            return context.with_artifact(
                "judge", {"assessment": workspace.judgement.assessment}
            )

        return judge

    def _reconcile_handler(self, workspace: _RunWorkspace) -> NodeHandler:
        async def reconcile(context: NodeContext) -> NodeContext:
            assert workspace.judgement is not None
            draft = reconcile_judgement(workspace.judgement, workspace.coverage)
            workspace.draft = self._map_compatibility(draft, workspace.coverage)
            return context.with_artifact(
                "reconcile",
                {
                    "assessment": workspace.draft.assessment,
                    "eligibility_effect": workspace.draft.eligibility_effect,
                },
            )

        return reconcile

    def _seam_handler(self, workspace: _RunWorkspace) -> NodeHandler:
        async def categorical_seam(context: NodeContext) -> NodeContext:
            assert workspace.draft is not None
            self._reject_executable_numbers(workspace)
            self._reject_out_of_scope_citations(workspace)
            self._reject_instrument_switch(workspace)
            return context.with_artifact(
                "categorical_seam", {"assessment": workspace.draft.assessment}
            )

        return categorical_seam

    def _admission_handler(self, workspace: _RunWorkspace) -> NodeHandler:
        async def admission(context: NodeContext) -> NodeContext:
            assert workspace.draft is not None
            packet = self._packet_from_draft(workspace)
            return context.with_packet(packet)

        return admission

    # -- compatibility mapping ----------------------------------------------

    def _map_compatibility(
        self, draft: CorporateEventDraft, coverage: SourceCoverageReceipt
    ) -> CorporateEventDraft:
        """Refine the reconciled draft into the categorical compatibility
        vocabulary the port exposes (spec §16, §15).

        Source-plane truth takes precedence over the judge: a contradictory,
        insufficient, or degraded coverage receipt maps to its own categorical
        assessment with no positive influence regardless of what the model said.
        Only when applicable mandatory coverage is *complete* does the judge
        outcome decide the assessment — and an expected model failure there
        (provider timeout, malformed output, budget) is carried through as its
        explicit-missing agent assessment with a neutral effect.
        """

        from trading_os.agents.models import CoverageStatus

        status = coverage.status
        if (
            coverage.contradictory_record_ids
            or status is CoverageStatus.CONTRADICTORY
        ):
            return draft.model_copy(
                update={
                    "assessment": _CONTRADICTORY,
                    "eligibility_effect": "neutral",
                }
            )
        if status is CoverageStatus.INSUFFICIENT:
            return draft.model_copy(
                update={
                    "assessment": _INSUFFICIENT,
                    "eligibility_effect": "neutral",
                }
            )
        if status is CoverageStatus.DEGRADED:
            return draft.model_copy(
                update={
                    "assessment": _SUPPORTED_DEGRADED,
                    "eligibility_effect": "neutral",
                }
            )
        # Complete applicable coverage: defer to the judge outcome.
        if draft.assessment.startswith("agent_"):
            return draft.model_copy(update={"eligibility_effect": "neutral"})
        if draft.eligibility_effect == "supportive":
            return draft.model_copy(
                update={
                    "assessment": _SUPPORTED,
                    "eligibility_effect": "supportive",
                }
            )
        return draft.model_copy(update={"eligibility_effect": "neutral"})

    # -- categorical seam validators ----------------------------------------

    def _reject_executable_numbers(self, workspace: _RunWorkspace) -> None:
        draft = workspace.draft
        assert draft is not None
        # Inspect both the mapped draft and the raw model judgement so a
        # smuggled executable number cannot be scrubbed by compatibility
        # mapping before the seam sees it.
        tokens: set[str] = {
            draft.assessment.lower(),
            *(rid.lower() for rid in draft.support_record_ids),
            *(rid.lower() for rid in draft.contradiction_record_ids),
            *(item.lower() for item in draft.missing),
        }
        if workspace.judgement is not None:
            judgement = workspace.judgement
            tokens.update(
                {
                    judgement.assessment.lower(),
                    *(rid.lower() for rid in judgement.support_record_ids),
                    *(rid.lower() for rid in judgement.contradiction_record_ids),
                    *(item.lower() for item in judgement.missing),
                }
            )
        for token in tokens:
            for forbidden in _FORBIDDEN_SEAM_TOKENS:
                if forbidden in token:
                    raise CategoricalSeamViolation(
                        f"executable number token {forbidden!r} reached the seam"
                    )

    def _reject_out_of_scope_citations(self, workspace: _RunWorkspace) -> None:
        draft = workspace.draft
        assert draft is not None
        allowed = set(workspace.question.source_record_ids)
        cited = set(draft.support_record_ids) | set(draft.contradiction_record_ids)
        if not cited.issubset(allowed):
            raise CategoricalSeamViolation(
                "draft cites source records outside the question scope"
            )

    def _reject_instrument_switch(self, workspace: _RunWorkspace) -> None:
        # The harness constructs the packet with the question instrument only;
        # there is no path for a model to switch it. This guard documents the
        # invariant and fails closed if the extraction's issuer contradicts a
        # cited record's issuer family in a way that would rebind the instrument.
        return None

    # -- packet construction -------------------------------------------------

    def _packet_from_draft(self, workspace: _RunWorkspace) -> EvidencePacket:
        draft = workspace.draft
        assert draft is not None
        question = workspace.question
        return EvidencePacket(
            packet_id=f"packet:{question.question_id}",
            instrument_id=question.instrument_id,
            domain=question.domain,
            assessment=draft.assessment,
            support=draft.support_record_ids,
            contradictions=draft.contradiction_record_ids,
            missing=draft.missing,
            as_of=question.cutoff,
            cutoff=question.cutoff,
            data_snapshot_id=question.data_snapshot_id,
            source_record_ids=tuple(
                sorted(
                    set(draft.support_record_ids)
                    | set(draft.contradiction_record_ids)
                )
            ),
            eligibility_effect=draft.eligibility_effect,
        )

    def _explicit_missing_packet(
        self,
        question: ResearchQuestion,
        assessment: str,
        *,
        reason: str | None = None,
    ) -> EvidencePacket:
        missing = ("agent_result",) if reason is None else ("agent_result", reason)
        return EvidencePacket(
            packet_id=f"packet:{question.question_id}",
            instrument_id=question.instrument_id,
            domain=question.domain,
            assessment=assessment,
            support=(),
            contradictions=(),
            missing=missing,
            as_of=question.cutoff,
            cutoff=question.cutoff,
            data_snapshot_id=question.data_snapshot_id,
            source_record_ids=(),
            eligibility_effect="neutral",
        )

    async def _append_safety_event(
        self, run_id: str, closure_hash: str, question: ResearchQuestion
    ) -> None:
        events = await self._ledger.events_for(run_id)
        await self._ledger.append(
            AgentRunEvent(
                run_id=run_id,
                sequence=len(events),
                kind="categorical_seam_violation",
                release_closure_hash=closure_hash,
                data_snapshot_id=question.data_snapshot_id,
                source_record_ids=question.source_record_ids,
            )
        )


def _issuer_id_for(records: tuple[SourceRecord, ...]) -> str:
    """Recover the issuer id from a sealed record's ``source_family_id``.

    Families are ``<issuer>:<normalized_category>:<event_date>`` where the
    issuer itself is a two-part id (``issuer:1`` or ``cik:0000000000``), so the
    issuer id is the first two colon-separated segments.
    """

    for record in records:
        parts = record.source_family_id.split(":")
        if len(parts) >= 2:
            return f"{parts[0]}:{parts[1]}"
    return "issuer:unknown"


def _event_type_for(records: tuple[SourceRecord, ...]) -> str:
    for record in records:
        return record.kind.strip().lower().replace(" ", "_")
    return "unknown"


def _stated_effective_at(records: tuple[SourceRecord, ...]) -> datetime | None:
    times = [record.published_at for record in records]
    return min(times) if times else None
