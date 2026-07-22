from trading_os.portfolio.completeness import CompletenessState, PortfolioCompletenessVector
from trading_os.portfolio.gate import GateAction, decide_portfolio_gate


def test_missing_open_orders_blocks_new_exposure() -> None:
    vector = PortfolioCompletenessVector.complete().model_copy(
        update={"open_orders": CompletenessState.MISSING}
    )
    assert decide_portfolio_gate(vector).action is GateAction.BLOCK_NEW_EXPOSURE


def test_unknown_cost_history_does_not_hide_current_exposure() -> None:
    vector = PortfolioCompletenessVector.complete().model_copy(
        update={"provenance": CompletenessState.DEGRADED}
    )
    decision = decide_portfolio_gate(vector)
    assert decision.action is GateAction.ALLOW
    assert "partial performance history" in decision.warnings


def test_stale_custody_blocks_new_exposure() -> None:
    vector = PortfolioCompletenessVector.complete().model_copy(
        update={"custody": CompletenessState.STALE}
    )
    assert decide_portfolio_gate(vector).action is GateAction.BLOCK_NEW_EXPOSURE


def test_protection_order_uncertainty_is_management_only() -> None:
    vector = PortfolioCompletenessVector.complete().model_copy(
        update={"protection_orders": CompletenessState.MISSING}
    )
    assert decide_portfolio_gate(vector).action is GateAction.MANAGEMENT_ONLY


def test_all_complete_allows() -> None:
    assert decide_portfolio_gate(PortfolioCompletenessVector.complete()).action is GateAction.ALLOW
