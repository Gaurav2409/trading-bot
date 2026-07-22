from trading_os.kernel.ids import AccountId, InstrumentId
from trading_os.portfolio.analysis import CurrentPortfolioAnalysis, PortfolioRiskOverlaySet
from trading_os.portfolio.completeness import PortfolioCompletenessVector
from trading_os.portfolio.models import CashBuckets, PositionBuckets
from trading_os.portfolio.projector import AccountPortfolioProjection


def _projection_with_holding(sector_qty: int) -> AccountPortfolioProjection:
    positions = {}
    if sector_qty:
        positions[InstrumentId("NSE:INE000000009")] = PositionBuckets(
            settled_available=sector_qty,
            unsettled=0,
            pledged=0,
            liened=0,
            authorization_blocked=0,
            broker_saleable=sector_qty,
            local_sell_reserved=0,
            pending_buy=0,
            pending_sell=0,
        )
    return AccountPortfolioProjection(
        account_id=AccountId("kite-1"),
        broker="kite",
        base_currency="INR",
        positions=positions,
        cash=CashBuckets(
            currency="INR",
            settled_minor=1_000_000,
            unsettled_minor=0,
            broker_available_minor=1_000_000,
            os_reserved_minor=0,
            pending_debit_minor=0,
            pending_credit_minor=0,
        ),
    )


def test_external_holding_tightens_via_overlay_not_new_quantity() -> None:
    # Without the external holding the candidate sector looks safe.
    without = CurrentPortfolioAnalysis.build(
        _projection_with_holding(0),
        PortfolioCompletenessVector.complete(),
        candidate_instrument=InstrumentId("NSE:INE000000009"),
        candidate_sector="metals",
        sector_of={InstrumentId("NSE:INE000000009"): "metals"},
        sector_cap_minor=500_000,
        price_minor={InstrumentId("NSE:INE000000009"): 10_000},
    )
    # A sizeable but under-cap external metals holding must tighten the overlay
    # multiplier (still in (0, 1], never increasing size).
    under_cap = CurrentPortfolioAnalysis.build(
        _projection_with_holding(30),  # 30 * 10_000 = 300_000 of a 500_000 cap
        PortfolioCompletenessVector.complete(),
        candidate_instrument=InstrumentId("NSE:INE000000009"),
        candidate_sector="metals",
        sector_of={InstrumentId("NSE:INE000000009"): "metals"},
        sector_cap_minor=500_000,
        price_minor={InstrumentId("NSE:INE000000009"): 10_000},
    )
    # An over-cap external holding must veto rather than grant any new exposure.
    over_cap = CurrentPortfolioAnalysis.build(
        _projection_with_holding(60),  # 60 * 10_000 = 600_000 > 500_000 cap
        PortfolioCompletenessVector.complete(),
        candidate_instrument=InstrumentId("NSE:INE000000009"),
        candidate_sector="metals",
        sector_of={InstrumentId("NSE:INE000000009"): "metals"},
        sector_cap_minor=500_000,
        price_minor={InstrumentId("NSE:INE000000009"): 10_000},
    )
    assert isinstance(without.overlay, PortfolioRiskOverlaySet)
    assert without.overlay.multiplier == 1.0
    assert not without.overlay.veto
    assert 0 < under_cap.overlay.multiplier < without.overlay.multiplier
    assert over_cap.overlay.veto is True


def test_analysis_never_accepts_household_aggregate_as_cash() -> None:
    analysis = CurrentPortfolioAnalysis.build(
        _projection_with_holding(0),
        PortfolioCompletenessVector.complete(),
        candidate_instrument=InstrumentId("NSE:INE000000009"),
        candidate_sector="metals",
        sector_of={},
        sector_cap_minor=500_000,
        price_minor={},
    )
    assert "household_aggregate_minor" not in CurrentPortfolioAnalysis.model_fields
    assert analysis.account_id == AccountId("kite-1")
