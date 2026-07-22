from enum import StrEnum

from pydantic import BaseModel

from trading_os.portfolio.completeness import CompletenessState, PortfolioCompletenessVector

# Dimensions whose missing/stale/conflict state blocks new exposure entirely.
_CRITICAL = (
    "custody",
    "cash",
    "open_orders",
    "identity",
    "settlement",
    "prices",
    "fx",
    "corporate_actions",
    "policies",
)
_BLOCKING_STATES = frozenset(
    {CompletenessState.MISSING, CompletenessState.STALE, CompletenessState.CONFLICT}
)


class GateAction(StrEnum):
    ALLOW = "allow"
    REDUCE_ONLY = "reduce_only"
    MANAGEMENT_ONLY = "management_only"
    BLOCK_NEW_EXPOSURE = "block_new_exposure"


class PortfolioGateDecision(BaseModel, frozen=True):
    action: GateAction
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


def decide_portfolio_gate(vector: PortfolioCompletenessVector) -> PortfolioGateDecision:
    reasons: list[str] = []
    warnings: list[str] = []

    for dimension in _CRITICAL:
        state = getattr(vector, dimension)
        if state in _BLOCKING_STATES:
            reasons.append(f"{dimension}:{state.value}")

    if reasons:
        return PortfolioGateDecision(
            action=GateAction.BLOCK_NEW_EXPOSURE,
            reasons=tuple(reasons),
            warnings=(),
        )

    # Protection-order uncertainty does not block reconciliation or reduction,
    # but it does prevent treating positions as fully managed.
    if vector.protection_orders in _BLOCKING_STATES:
        return PortfolioGateDecision(
            action=GateAction.MANAGEMENT_ONLY,
            reasons=(f"protection_orders:{vector.protection_orders.value}",),
            warnings=(),
        )

    # Provenance degradation warns but never erases current exposure.
    if vector.provenance is not CompletenessState.COMPLETE:
        warnings.append("partial performance history")

    return PortfolioGateDecision(
        action=GateAction.ALLOW,
        reasons=(),
        warnings=tuple(warnings),
    )
