from typing import Protocol

from trading_os.market_data.models import Bar, Quote


class MarketDataPort(Protocol):
    async def historical_bars(
        self, instrument_id: str, timeframe: str, start: str, end: str
    ) -> list[Bar]:
        raise NotImplementedError

    async def latest_quote(self, instrument_id: str) -> Quote:
        raise NotImplementedError


class FixtureMarketData:
    """Offline market-data port backed by in-memory bars/quotes."""

    def __init__(self, bars: dict[tuple[str, str], list[Bar]], quotes: dict[str, Quote]) -> None:
        self._bars = bars
        self._quotes = quotes

    async def historical_bars(
        self, instrument_id: str, timeframe: str, start: str, end: str
    ) -> list[Bar]:
        return list(self._bars.get((instrument_id, timeframe), []))

    async def latest_quote(self, instrument_id: str) -> Quote:
        return self._quotes[instrument_id]
