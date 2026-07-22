"""Research agent orchestration boundary.

A ResearchAgentPort accepts a bounded research question plus source-record IDs
and returns a candidate EvidencePacket. Admission validates citations, cutoff,
closed enums and prompt-injection isolation. LLM failure produces an explicit
missing packet rather than blocking relational operation.
"""

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel

from trading_os.research.models import EvidenceDomain, EvidencePacket
from trading_os.research.seam import (
    CategoricalSeamViolation,
    assert_categorical_assessment,
    reject_forbidden_token,
)


class ResearchQuestion(BaseModel, frozen=True):
    question_id: str
    instrument_id: str
    domain: EvidenceDomain
    source_record_ids: tuple[str, ...]
    cutoff: datetime
    data_snapshot_id: str


class ResearchAgentPort(Protocol):
    async def investigate(self, question: ResearchQuestion) -> EvidencePacket | None:
        raise NotImplementedError


class AdmissionError(ValueError):
    pass


def admit_packet(packet: EvidencePacket, question: ResearchQuestion) -> EvidencePacket:
    """Validate a candidate packet before it may influence decisioning."""
    if packet.instrument_id != question.instrument_id:
        raise AdmissionError("packet instrument does not match the question")
    if packet.domain is not question.domain:
        raise AdmissionError("packet domain does not match the question")
    if packet.cutoff > question.cutoff:
        raise AdmissionError("packet cutoff is later than the question cutoff")
    cited = set(packet.source_record_ids)
    allowed = set(question.source_record_ids)
    if not cited.issubset(allowed):
        raise AdmissionError("packet cites source records outside the question scope")
    # Categorical evidence seam (spec §4, §16): the primary constitutional
    # invariant. The assessment must be a registered categorical value for the
    # domain and carry no executable number; support/contradiction/missing
    # tokens must carry no executable-number field name. This is the idempotent
    # defence at the port boundary that no harness node path can bypass — a
    # model-authored assessment like "agent_2500" is rejected here even if it
    # slips past an upstream seam node.
    try:
        assert_categorical_assessment(packet.domain, packet.assessment)
        for token in (*packet.support, *packet.contradictions, *packet.missing):
            reject_forbidden_token(token)
    except CategoricalSeamViolation as violation:
        raise AdmissionError(f"categorical seam violation: {violation}") from violation
    # Sentiment is risk-only unless corroborated by a primary source.
    if packet.domain is EvidenceDomain.SENTIMENT and "primary_corroboration" in packet.missing:
        if packet.eligibility_effect != "risk_only":
            raise AdmissionError("uncorroborated sentiment must be risk_only")
    return packet


class ResearchOrchestrator:
    def __init__(self, agent: ResearchAgentPort) -> None:
        self._agent = agent

    async def run(self, question: ResearchQuestion) -> EvidencePacket | None:
        try:
            candidate = await self._agent.investigate(question)
        except Exception:  # noqa: BLE001
            # Catastrophic port failure (unavailable canonical ledger or an
            # unresolved immutable release closure) is the only path to None.
            # Expected model/tool/budget failures are handled inside the
            # DomainAgentHarness and return an admitted explicit-missing packet,
            # never an exception, so the relational champion is never disabled.
            return None
        if candidate is None:
            return None
        # Idempotent defence: the orchestrator re-validates every candidate at
        # the port boundary even though the harness already admitted it.
        return admit_packet(candidate, question)
