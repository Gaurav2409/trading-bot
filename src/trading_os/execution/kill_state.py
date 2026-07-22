from enum import StrEnum

from pydantic import BaseModel


class KillMode(StrEnum):
    ACTIVE = "active"
    ENTRY_DISABLED = "entry_disabled"
    REDUCE_ONLY = "reduce_only"
    MANAGEMENT_ONLY = "management_only"
    HALTED = "halted"


class KillState(BaseModel, frozen=True):
    account_id: str
    generation: int
    mode: KillMode

    @classmethod
    def active(cls, account_id: str, generation: int) -> "KillState":
        return cls(account_id=account_id, generation=generation, mode=KillMode.ACTIVE)

    @property
    def may_increase_exposure(self) -> bool:
        return self.mode is KillMode.ACTIVE

    @property
    def may_reconcile(self) -> bool:
        return True


_SAFETY_REASONS = frozenset(
    {"critical_portfolio_stale", "reconciliation_conflict", "protection_failed"}
)


def transition(state: KillState, reason: str) -> KillState:
    """A safety/compliance/data fault fences new exposure (ENTRY_DISABLED) before
    any human acknowledgement; other reasons halt. Generation is monotonic."""
    mode = KillMode.ENTRY_DISABLED if reason in _SAFETY_REASONS else KillMode.HALTED
    return state.model_copy(update={"generation": state.generation + 1, "mode": mode})
