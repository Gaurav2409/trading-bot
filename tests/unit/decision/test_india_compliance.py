from trading_os.brokers.models import OrderType
from trading_os.decision.compliance import IndiaComplianceInput, evaluate_india


def test_india_algo_market_order_is_not_constructible() -> None:
    assert set(OrderType) == {OrderType.LIMIT, OrderType.STOP_LIMIT}


def test_unregistered_static_ip_vetoes_new_india_exposure() -> None:
    decision = evaluate_india(
        IndiaComplianceInput(
            static_ip_ready=False,
            algorithm_tag_ready=True,
            settled_cash_sufficient=True,
            order_rate_last_second=0,
            max_orders_per_second=10,
            instrument_allowed=True,
        )
    )
    assert decision.outcome == "veto"
    assert decision.reason == "static_ip_not_ready"


def test_missing_tag_vetoes() -> None:
    decision = evaluate_india(
        IndiaComplianceInput(
            static_ip_ready=True,
            algorithm_tag_ready=False,
            settled_cash_sufficient=True,
            order_rate_last_second=0,
            max_orders_per_second=10,
            instrument_allowed=True,
        )
    )
    assert decision.outcome == "veto"
    assert decision.reason == "algorithm_tag_not_ready"


def test_order_rate_ceiling_vetoes() -> None:
    decision = evaluate_india(
        IndiaComplianceInput(
            static_ip_ready=True,
            algorithm_tag_ready=True,
            settled_cash_sufficient=True,
            order_rate_last_second=10,
            max_orders_per_second=10,
            instrument_allowed=True,
        )
    )
    assert decision.outcome == "veto"
    assert decision.reason == "order_rate_exceeded"


def test_all_ready_allows() -> None:
    decision = evaluate_india(
        IndiaComplianceInput(
            static_ip_ready=True,
            algorithm_tag_ready=True,
            settled_cash_sufficient=True,
            order_rate_last_second=2,
            max_orders_per_second=10,
            instrument_allowed=True,
        )
    )
    assert decision.outcome == "allow"
