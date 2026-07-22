from datetime import UTC, datetime, timedelta
from decimal import Decimal

from trading_os.kernel.ids import InstrumentId
from trading_os.market_data.models import Bar


def make_daily_bars(closes: list[Decimal], volumes: list[Decimal]) -> list[Bar]:
    if len(closes) != len(volumes):
        raise ValueError("closes and volumes must have the same length")
    start = datetime(2026, 7, 1, tzinfo=UTC)
    bars: list[Bar] = []
    previous = closes[0]
    for index, (close, volume) in enumerate(zip(closes, volumes, strict=True)):
        day = start + timedelta(days=index)
        bars.append(
            Bar(
                instrument_id=InstrumentId("BSE:INE000000001"),
                timeframe="1d",
                start=day,
                end=day + timedelta(days=1),
                received_at=day + timedelta(days=1, seconds=1),
                open=previous,
                high=max(previous, close),
                low=min(previous, close),
                close=close,
                volume=volume,
                source_id="fixture",
                entitlement="test",
                adjustment_set_id="raw",
            )
        )
        previous = close
    return bars
