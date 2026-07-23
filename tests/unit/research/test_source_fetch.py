from datetime import UTC, datetime

import pytest

from trading_os.research.source_fetch import (
    FixtureSourceFetcher,
    RawFetchResult,
    SourceFetchError,
)

AT = datetime(2026, 7, 21, tzinfo=UTC)


async def test_fixture_fetcher_returns_recorded_payload() -> None:
    fetcher = FixtureSourceFetcher(
        {"nse/latest": RawFetchResult(endpoint="nse/latest", status=200, fetched_at=AT, payload="[]")}
    )
    result = await fetcher.fetch("nse/latest", since=AT)
    assert result.status == 200
    assert result.payload == "[]"


async def test_fixture_fetcher_raises_recorded_error() -> None:
    fetcher = FixtureSourceFetcher({"bse/latest": SourceFetchError("blocked")})
    with pytest.raises(SourceFetchError):
        await fetcher.fetch("bse/latest", since=AT)
