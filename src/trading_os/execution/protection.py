from enum import StrEnum

from pydantic import BaseModel


class ProtectionState(StrEnum):
    UNREQUIRED = "unrequired"
    PENDING_FILL = "pending_fill"
    PENDING_PROTECTION = "pending_protection"
    PROTECTED = "protected"
    DEGRADED = "degraded"
    FAILED = "failed"
    CLOSED = "closed"


class ProtectionSupervisor(BaseModel, frozen=True):
    """Broker-confirmed coverage state machine. A fill is not treated as fully
    managed until a broker-native stop covers the reconciled quantity. Protection
    failure fences new entries and never fabricates a close quantity when custody
    is stale."""

    state: ProtectionState
    covered_quantity: int = 0
    filled_quantity: int = 0
    guessed_close_quantity: int | None = None

    @classmethod
    def unrequired(cls) -> "ProtectionSupervisor":
        return cls(state=ProtectionState.UNREQUIRED)

    @classmethod
    def required(cls, covered_quantity: int) -> "ProtectionSupervisor":
        return cls(state=ProtectionState.PENDING_FILL, covered_quantity=covered_quantity)

    @property
    def fences_new_entries(self) -> bool:
        return self.state in {ProtectionState.DEGRADED, ProtectionState.FAILED}

    def on_fill(self, filled_quantity: int) -> "ProtectionSupervisor":
        return self.model_copy(
            update={
                "state": ProtectionState.PENDING_PROTECTION,
                "filled_quantity": filled_quantity,
            }
        )

    def on_protection_observed(self, stop_quantity: int) -> "ProtectionSupervisor":
        if stop_quantity >= self.filled_quantity and stop_quantity >= self.covered_quantity:
            return self.model_copy(update={"state": ProtectionState.PROTECTED})
        return self.model_copy(update={"state": ProtectionState.DEGRADED})

    def on_protection_failed(self) -> "ProtectionSupervisor":
        # Enters MANAGEMENT_ONLY at the account level; never guesses a close qty.
        return self.model_copy(
            update={"state": ProtectionState.FAILED, "guessed_close_quantity": None}
        )
