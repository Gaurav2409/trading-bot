from enum import StrEnum

from pydantic import BaseModel


class CompletenessState(StrEnum):
    COMPLETE = "complete"
    DEGRADED = "degraded"
    MISSING = "missing"
    STALE = "stale"
    CONFLICT = "conflict"


class PortfolioCompletenessVector(BaseModel, frozen=True):
    custody: CompletenessState
    cash: CompletenessState
    open_orders: CompletenessState
    protection_orders: CompletenessState
    identity: CompletenessState
    settlement: CompletenessState
    prices: CompletenessState
    fx: CompletenessState
    corporate_actions: CompletenessState
    provenance: CompletenessState
    policies: CompletenessState

    @classmethod
    def complete(cls) -> "PortfolioCompletenessVector":
        return cls(**{name: CompletenessState.COMPLETE for name in cls.model_fields})
