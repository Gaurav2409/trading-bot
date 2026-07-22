from datetime import UTC, datetime, timedelta
from decimal import Decimal

from trading_os.kernel.ids import InstrumentId
from trading_os.market_data.models import Bar
from trading_os.market_data.snapshot import build_validated_snapshot


def _ohlc_bad_bar(cutoff: datetime) -> Bar:
    # high < close: an inconsistent OHLC record.
    return Bar(
        instrument_id=InstrumentId("NSE:INE000000002"),
        timeframe="1d",
        start=cutoff - timedelta(days=1),
        end=cutoff,
        received_at=cutoff - timedelta(seconds=1),
        open=Decimal("100"),
        high=Decimal("100"),
        low=Decimal("99"),
        close=Decimal("120"),
        volume=Decimal("1"),
        source_id="kite",
        entitlement="live",
        adjustment_set_id="raw",
    )


def test_inconsistent_ohlc_is_rejected() -> None:
    cutoff = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    result = build_validated_snapshot([_ohlc_bad_bar(cutoff)], cutoff)
    assert result.rejected_count == 1
    assert result.bars == ()


def test_iex_only_bar_cannot_claim_sip_coverage() -> None:
    cutoff = datetime(2026, 7, 22, 20, 0, tzinfo=UTC)
    iex_bar = Bar(
        instrument_id=InstrumentId("NASDAQ:TESTUS"),
        timeframe="1d",
        start=cutoff - timedelta(days=1),
        end=cutoff,
        received_at=cutoff - timedelta(seconds=1),
        open=Decimal("10"),
        high=Decimal("11"),
        low=Decimal("9"),
        close=Decimal("10.5"),
        volume=Decimal("1000"),
        source_id="alpaca",
        entitlement="iex",
        adjustment_set_id="raw",
    )
    result = build_validated_snapshot([iex_bar], cutoff, require_entitlement="sip")
    assert result.rejected_count == 1
    assert "entitlement" in result.rejections[0].reason
