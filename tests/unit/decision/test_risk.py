from trading_os.decision.risk import RiskEngine, RiskInput
from trading_os.research.models import RiskOverlaySet


def test_overlay_can_only_shrink_never_increase() -> None:
    engine = RiskEngine()
    base = RiskInput(
        provisional_quantity=100,
        entry_price_minor=100_000,
        deployed_minor=0,
        max_deployed_minor=100_000_000,
        symbol_exposure_minor=0,
        max_symbol_minor=100_000_000,
        overlay=RiskOverlaySet(multiplier=0.5),
    )
    decision = engine.evaluate(base)
    assert decision.final_quantity == 50  # shrunk, never grown

    grown_attempt = base.model_copy(update={"overlay": RiskOverlaySet(multiplier=1.0)})
    assert engine.evaluate(grown_attempt).final_quantity == 100


def test_external_holding_shrinks_candidate_via_symbol_cap() -> None:
    engine = RiskEngine()
    decision = engine.evaluate(
        RiskInput(
            provisional_quantity=100,
            entry_price_minor=100_000,
            deployed_minor=0,
            max_deployed_minor=100_000_000,
            symbol_exposure_minor=9_500_000,  # existing external holding near the cap
            max_symbol_minor=10_000_000,
            overlay=RiskOverlaySet(multiplier=1.0),
        )
    )
    # Only 500_000 of symbol headroom -> at 100_000/share, at most 5 shares.
    assert decision.final_quantity == 5
    assert "symbol_cap" in decision.reason_codes


def test_veto_forces_zero() -> None:
    engine = RiskEngine()
    decision = engine.evaluate(
        RiskInput(
            provisional_quantity=100,
            entry_price_minor=100_000,
            deployed_minor=0,
            max_deployed_minor=100_000_000,
            symbol_exposure_minor=0,
            max_symbol_minor=100_000_000,
            overlay=RiskOverlaySet(multiplier=1.0, veto=True, reason_codes=("veto_test",)),
        )
    )
    assert decision.final_quantity == 0
    assert "veto_test" in decision.reason_codes
