from enum import StrEnum

from pydantic import BaseModel


class DifferenceClass(StrEnum):
    NONE = "none"
    EXPLAINED_TIMING = "explained_timing"
    EXPECTED_EXTERNAL = "expected_external"
    STALE_OBSERVATION = "stale_observation"
    UNKNOWN_EFFECT = "unknown_effect"
    UNEXPLAINED_CUSTODY = "unexplained_custody"
    CASH_CONFLICT = "cash_conflict"
    MISSING_ORDER = "missing_order"
    PROTECTION_CONFLICT = "protection_conflict"
    IDENTITY_CONFLICT = "identity_conflict"


class ReconciliationDifference(BaseModel, frozen=True):
    kind: DifferenceClass
    fail_direction: str
    broker_value: str
    os_value: str


def reconcile_quantity(broker_quantity: int, os_expected_quantity: int) -> ReconciliationDifference:
    """Reconcile a broker-reported custody quantity against the OS expectation.

    Records the difference as a typed fact with a deterministic fail direction;
    it never rewrites either input to hide the difference. Any unexplained
    divergence fences new exposure (entry_disabled) while reconciliation and
    broker-native protection continue.
    """
    if broker_quantity == os_expected_quantity:
        return ReconciliationDifference(
            kind=DifferenceClass.NONE,
            fail_direction="none",
            broker_value=str(broker_quantity),
            os_value=str(os_expected_quantity),
        )
    return ReconciliationDifference(
        kind=DifferenceClass.UNEXPLAINED_CUSTODY,
        fail_direction="entry_disabled",
        broker_value=str(broker_quantity),
        os_value=str(os_expected_quantity),
    )
