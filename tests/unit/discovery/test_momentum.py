from decimal import Decimal

from trading_os.discovery.momentum import MomentumDetectorPolicy, MomentumOpportunityDetector
from trading_os.kernel.ids import SnapshotId
from trading_os.market_data.testing import make_daily_bars


def test_detector_finds_accelerating_price_and_volume_without_auto_buying() -> None:
    bars = make_daily_bars(
        closes=[Decimal(str(value)) for value in [80, 82, 84, 88, 94, 103, 115]],
        volumes=[Decimal(str(value)) for value in [10, 11, 12, 15, 22, 35, 58]],
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
    assert candidates[0].setup == "momentum_acceleration"
    assert not hasattr(candidates[0], "quantity")
    assert not hasattr(candidates[0], "order")


def test_flat_series_produces_no_candidate() -> None:
    bars = make_daily_bars(
        closes=[Decimal("100")] * 7,
        volumes=[Decimal("10")] * 7,
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
    assert detector.detect(bars, SnapshotId("data-1")) == []


def test_candidate_has_no_executable_fields() -> None:
    from trading_os.discovery.models import OpportunityCandidate

    forbidden = {"quantity", "price", "target_weight", "target_position", "order", "broker"}
    assert forbidden.isdisjoint(OpportunityCandidate.model_fields)
