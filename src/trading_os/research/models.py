from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EvidenceDomain(StrEnum):
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    CORPORATE_EVENT = "corporate_event"
    SENTIMENT = "sentiment"
    MACRO = "macro"
    ECONOMIC_RELATIONSHIP = "economic_relationship"
    GOVERNANCE = "governance"
    LIQUIDITY = "liquidity"
    PORTFOLIO = "portfolio"
    MARKET_MECHANICS = "market_mechanics"


class EvidencePacket(BaseModel, frozen=True):
    packet_id: str
    instrument_id: str
    domain: EvidenceDomain
    assessment: str
    support: tuple[str, ...]
    contradictions: tuple[str, ...]
    missing: tuple[str, ...]
    as_of: datetime
    cutoff: datetime
    data_snapshot_id: str
    source_record_ids: tuple[str, ...]
    eligibility_effect: str


class DecisionFeatureSet(BaseModel, frozen=True):
    feature_set_id: str
    instrument_id: str
    categorical_features: dict[str, str]
    evidence_packet_ids: tuple[str, ...]
    semantic_snapshot_id: str | None
    activation_release_id: str | None


class RiskOverlaySet(BaseModel, frozen=True):
    """Tighten-only: multiplier in (0, 1] and/or a veto. No free-form agent
    result crosses this boundary."""

    multiplier: float = Field(gt=0, le=1)
    veto: bool = False
    reason_codes: tuple[str, ...] = ()
