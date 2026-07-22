from datetime import UTC, datetime
from decimal import Decimal

from trading_os.discovery.momentum import MomentumDetectorPolicy, MomentumOpportunityDetector
from trading_os.discovery.registry import OpportunityDetectorRegistry
from trading_os.kernel.ids import InstrumentId, SnapshotId
from trading_os.market_data.testing import make_daily_bars


def test_registry_emits_receipt_even_when_an_instrument_fails() -> None:
    good = make_daily_bars(
        closes=[Decimal(str(v)) for v in [80, 82, 84, 88, 94, 103, 115]],
        volumes=[Decimal(str(v)) for v in [10, 11, 12, 15, 22, 35, 58]],
    )
    detector = MomentumOpportunityDetector(
        MomentumDetectorPolicy(
            release_id="momentum-v1",
            return_lookback=5,
            minimum_return=Decimal("0.15"),
            volume_lookback=5,
            minimum_volume_ratio=Decimal("2"),
        )
    )
    registry = OpportunityDetectorRegistry(detectors=[detector])
    bars_by_instrument = {
        InstrumentId("BSE:INE000000001"): good,
        InstrumentId("BSE:INE000000002"): [],  # too few bars -> omitted
    }
    result = registry.run(
        bars_by_instrument,
        SnapshotId("data-1"),
        started_at=datetime(2026, 7, 8, tzinfo=UTC),
        completed_at=datetime(2026, 7, 8, 0, 0, 1, tzinfo=UTC),
    )
    assert len(result.candidates) == 1
    receipt = result.receipt
    assert InstrumentId("BSE:INE000000001") in receipt.scanned_instruments
    assert InstrumentId("BSE:INE000000002") in receipt.omitted


def test_bse_only_candidate_outside_index_is_still_discovered() -> None:
    # A Cropster-like BSE-only momentum name is discoverable even without index membership.
    bars = make_daily_bars(
        closes=[Decimal(str(v)) for v in [50, 52, 55, 60, 68, 80, 96]],
        volumes=[Decimal(str(v)) for v in [5, 6, 7, 10, 18, 30, 55]],
    )
    detector = MomentumOpportunityDetector(
        MomentumDetectorPolicy(
            release_id="momentum-v1",
            return_lookback=5,
            minimum_return=Decimal("0.15"),
            volume_lookback=5,
            minimum_volume_ratio=Decimal("2"),
        )
    )
    candidates = detector.detect(bars, SnapshotId("data-1"))
    assert len(candidates) == 1
    assert str(candidates[0].instrument_id).startswith("BSE:")
