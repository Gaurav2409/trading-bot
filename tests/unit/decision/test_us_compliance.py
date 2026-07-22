from trading_os.decision.compliance import UsComplianceInput, evaluate_us


def test_trading_blocked_account_vetoes() -> None:
    decision = evaluate_us(
        UsComplianceInput(
            trading_blocked=True,
            account_blocked=False,
            trade_suspended_by_user=False,
            buying_power_minor=100_000,
            required_minor=5_000,
            asset_tradable=True,
            data_entitlement_ready=True,
            pdt_round_trips_used=0,
            pdt_round_trip_budget=3,
        )
    )
    assert decision.outcome == "veto"
    assert decision.reason == "trading_blocked"


def test_insufficient_buying_power_shrinks_or_vetoes() -> None:
    decision = evaluate_us(
        UsComplianceInput(
            trading_blocked=False,
            account_blocked=False,
            trade_suspended_by_user=False,
            buying_power_minor=1_000,
            required_minor=5_000,
            asset_tradable=True,
            data_entitlement_ready=True,
            pdt_round_trips_used=0,
            pdt_round_trip_budget=3,
        )
    )
    assert decision.outcome == "veto"
    assert decision.reason == "insufficient_buying_power"


def test_pdt_budget_exhausted_vetoes() -> None:
    decision = evaluate_us(
        UsComplianceInput(
            trading_blocked=False,
            account_blocked=False,
            trade_suspended_by_user=False,
            buying_power_minor=100_000,
            required_minor=5_000,
            asset_tradable=True,
            data_entitlement_ready=True,
            pdt_round_trips_used=3,
            pdt_round_trip_budget=3,
        )
    )
    assert decision.outcome == "veto"
    assert decision.reason == "pdt_budget_exhausted"


def test_all_clear_allows() -> None:
    decision = evaluate_us(
        UsComplianceInput(
            trading_blocked=False,
            account_blocked=False,
            trade_suspended_by_user=False,
            buying_power_minor=100_000,
            required_minor=5_000,
            asset_tradable=True,
            data_entitlement_ready=True,
            pdt_round_trips_used=1,
            pdt_round_trip_budget=3,
        )
    )
    assert decision.outcome == "allow"
