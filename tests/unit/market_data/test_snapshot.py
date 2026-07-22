from datetime import UTC, datetime, timedelta
from decimal import Decimal

from trading_os.kernel.ids import InstrumentId
from trading_os.market_data.models import Bar
from trading_os.market_data.snapshot import build_validated_snapshot


def _bar(received_offset_seconds: int, cutoff: datetime) -> Bar:
    return Bar(
        instrument_id=InstrumentId("NSE:INE000000001"),
        timeframe="15m",
        start=cutoff - timedelta(minutes=15),
        end=cutoff,
        received_at=cutoff + timedelta(seconds=received_offset_seconds),
        open=Decimal("100"),
        high=Decimal("102"),
        low=Decimal("99"),
        close=Decimal("101"),
        volume=Decimal("10000"),
        source_id="kite",
        entitlement="live",
        adjustment_set_id="raw",
    )


def test_snapshot_rejects_bar_received_after_decision_cutoff() -> None:
    cutoff = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    result = build_validated_snapshot([_bar(1, cutoff)], cutoff)
    assert result.rejected_count == 1
    assert result.bars == ()


def test_snapshot_accepts_bar_received_at_or_before_cutoff() -> None:
    cutoff = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    result = build_validated_snapshot([_bar(-1, cutoff)], cutoff)
    assert result.rejected_count == 0
    assert len(result.bars) == 1
    assert result.snapshot_id


def test_snapshot_is_content_addressed_and_stable() -> None:
    cutoff = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    a = build_validated_snapshot([_bar(-1, cutoff)], cutoff)
    b = build_validated_snapshot([_bar(-1, cutoff)], cutoff)
    assert a.snapshot_id == b.snapshot_id
