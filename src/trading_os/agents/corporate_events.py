"""Corporate-event domain node artifacts and handlers (spec §8.2, §9, §14).

The P0 corporate-event tracer threads three typed artifacts through the governed
trajectory:

* :class:`EventExtraction` — the categorical result of the ``gather`` agent loop
  (event type, cited record IDs, issuer, optional stated effective time). It
  carries no executable number.
* :class:`NormalizedCorporateEvent` — the output of the deterministic
  ``normalize`` transform that sits between the two agent loops. It derives a
  stable channel-family key per record family and a cutoff-eligibility flag
  without inventing any numeric intermediate.
* :class:`EventJudgement` — the categorical assessment produced by the ``judge``
  agent loop through the provider-neutral :class:`LLMRole`.

The deterministic ``reconcile`` transform fuses the judgement with the
:class:`SourceCoverageReceipt`: only complete, non-conflicting coverage yields a
``supportive`` :class:`CorporateEventDraft`; degraded, contradictory, or
insufficient coverage has no positive influence (``neutral``).

Every artifact is categorical: no price, quantity, target, expected return,
position weight, conviction multiplier, or order intent crosses this seam.
"""

from datetime import datetime

from pydantic import BaseModel

from trading_os.agents.llm import (
    ExpectedLLMFailure,
    LLMRole,
    StructuredInvocation,
    StructuredResult,
)
from trading_os.agents.models import CoverageStatus
from trading_os.research.source_coverage import SourceCoverageReceipt

# Categorical assessment vocabulary. Expected model/tool/budget failures map to
# an explicit-missing assessment so the relational champion is never disabled.
_FAILURE_ASSESSMENTS: dict[str, str] = {
    "timeout": "agent_provider_timeout",
    "refusal": "agent_provider_refusal",
    "unsupported": "agent_capability_unsupported",
    "malformed_output": "agent_malformed_output",
    "budget": "agent_budget_exhausted",
}


class EventExtraction(BaseModel, frozen=True):
    """Categorical output of the ``gather`` agent loop."""

    event_type: str
    record_ids: tuple[str, ...]
    issuer_id: str
    stated_effective_at: datetime | None = None


class NormalizedCorporateEvent(BaseModel, frozen=True):
    """Deterministic normalization output between the two agent loops."""

    event_type: str
    issuer_id: str
    record_ids: tuple[str, ...]
    channel_families: tuple[str, ...]
    within_cutoff: bool


class EventJudgement(BaseModel, frozen=True):
    """Categorical assessment produced by the ``judge`` agent loop."""

    assessment: str
    support_record_ids: tuple[str, ...]
    contradiction_record_ids: tuple[str, ...]
    missing: tuple[str, ...]


class CorporateEventDraft(BaseModel, frozen=True):
    """Reconciled categorical draft ready for the categorical seam and admission."""

    assessment: str
    support_record_ids: tuple[str, ...]
    contradiction_record_ids: tuple[str, ...]
    missing: tuple[str, ...]
    eligibility_effect: str


def _channel_family(
    issuer_id: str, event_type: str, effective_at: datetime | None
) -> str:
    """Deterministic family key: issuer + normalized category + event date.

    Mirrors ``corporate_event_sources._issuer_family`` so a normalized event
    aligns with the sealed source records it cites. When the extraction states
    no effective time, the family degrades to ``unknown`` rather than inventing
    the current clock.
    """

    normalized_category = event_type.strip().lower().replace(" ", "_")
    event_date = (
        effective_at.date().isoformat() if effective_at is not None else "unknown"
    )
    return f"{issuer_id}:{normalized_category}:{event_date}"


def normalize_event(
    extraction: EventExtraction, *, cutoff: datetime
) -> NormalizedCorporateEvent:
    """Deterministic ``normalize`` node: derive family key and cutoff eligibility."""

    within_cutoff = (
        extraction.stated_effective_at is None
        or extraction.stated_effective_at <= cutoff
    )
    channel_families = (
        _channel_family(
            extraction.issuer_id,
            extraction.event_type,
            extraction.stated_effective_at,
        ),
    )
    return NormalizedCorporateEvent(
        event_type=extraction.event_type,
        issuer_id=extraction.issuer_id,
        record_ids=extraction.record_ids,
        channel_families=channel_families,
        within_cutoff=within_cutoff,
    )


def judge_replay_key(normalized: NormalizedCorporateEvent) -> str:
    """Deterministic replay key for the judge invocation."""

    return f"judge:{normalized.issuer_id}:{normalized.event_type}"


async def judge_event(
    normalized: NormalizedCorporateEvent, role: LLMRole
) -> EventJudgement:
    """``judge`` node: map normalized evidence to a categorical assessment.

    Provider access crosses the owned :class:`LLMRole` seam and requests only the
    ``source_record_query`` capability. An expected model failure becomes an
    explicit-missing categorical judgement rather than a raised exception, so the
    relational champion is never disabled.
    """

    invocation: StructuredInvocation[EventJudgement] = StructuredInvocation(
        invocation_id=f"invocation:{judge_replay_key(normalized)}",
        role="corporate_event_judge",
        prompt_release_id="prompt:judge:v1",
        trusted_context={
            "event_type": normalized.event_type,
            "issuer_id": normalized.issuer_id,
            "within_cutoff": str(normalized.within_cutoff),
        },
        source_record_ids=normalized.record_ids,
        output_type=EventJudgement,
        allowed_capability_names=("source_record_query",),
        max_tokens=1024,
        replay_key=judge_replay_key(normalized),
    )
    result = await role.invoke(invocation)
    if isinstance(result, ExpectedLLMFailure):
        return EventJudgement(
            assessment=_FAILURE_ASSESSMENTS[result.kind],
            support_record_ids=(),
            contradiction_record_ids=(),
            missing=("agent_result",),
        )
    assert isinstance(result, StructuredResult)
    return result.output


def reconcile_judgement(
    judgement: EventJudgement, coverage: SourceCoverageReceipt
) -> CorporateEventDraft:
    """Deterministic ``reconcile`` node: fuse judgement and coverage receipt.

    Only complete coverage with no conflicting official records and no judged
    contradiction is ``supportive``; anything else (degraded, contradictory,
    insufficient, or a judged contradiction) is ``neutral`` — no positive
    influence.
    """

    supportive = (
        coverage.status is CoverageStatus.COMPLETE
        and not judgement.contradiction_record_ids
        and not coverage.contradictory_record_ids
    )
    effect = "supportive" if supportive else "neutral"
    missing = tuple(
        sorted(set(judgement.missing) | set(coverage.missing_channels))
    )
    return CorporateEventDraft(
        assessment=judgement.assessment,
        support_record_ids=judgement.support_record_ids,
        contradiction_record_ids=judgement.contradiction_record_ids,
        missing=missing,
        eligibility_effect=effect,
    )
