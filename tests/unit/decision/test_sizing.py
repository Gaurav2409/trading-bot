from trading_os.decision.sizing import SizingInput, size_cash_equity


def test_agent_conviction_cannot_change_quantity() -> None:
    base = SizingInput(
        available_cash_minor=1_250_000,
        capital_minor=5_000_000,
        risk_fraction_ppm=10_000,
        entry_price_minor=100_000,
        stop_price_minor=95_000,
        max_symbol_minor=500_000,
        lot_size=1,
    )
    assert size_cash_equity(base).quantity == 5
    assert "conviction" not in SizingInput.model_fields


def test_zero_or_negative_risk_per_share_sizes_zero() -> None:
    base = SizingInput(
        available_cash_minor=1_000_000,
        capital_minor=5_000_000,
        risk_fraction_ppm=10_000,
        entry_price_minor=100_000,
        stop_price_minor=100_000,
        max_symbol_minor=500_000,
        lot_size=1,
    )
    assert size_cash_equity(base).quantity == 0


def test_lot_size_rounds_down() -> None:
    base = SizingInput(
        available_cash_minor=10_000_000,
        capital_minor=100_000_000,
        risk_fraction_ppm=10_000,
        entry_price_minor=100_000,
        stop_price_minor=90_000,
        max_symbol_minor=100_000_000,
        lot_size=5,
    )
    # by_risk = (100_000_000 * 10_000 / 1e6) / 10_000 = 100 -> lot-rounded stays 100
    result = size_cash_equity(base)
    assert result.quantity % 5 == 0
