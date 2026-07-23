from datetime import UTC, datetime

import httpx
import pytest

from trading_os.research.source_fetch import HttpSourceFetcher, SourceFetchError


@pytest.mark.integration
async def test_http_fetcher_maps_transport_and_returns_raw(monkeypatch: pytest.MonkeyPatch) -> None:
    # Uses a stub transport so the shape is proven without a live exchange; the
    # marker keeps it out of the default gate where the real endpoints are used.
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text='[]')

    fetcher = HttpSourceFetcher()
    fetcher._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))  # type: ignore[attr-defined]
    result = await fetcher.fetch("https://example.test/latest", since=datetime(2026, 7, 21, tzinfo=UTC))
    assert result.status == 200
    assert result.payload == "[]"


@pytest.mark.integration
async def test_http_fetcher_maps_bad_status_to_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="blocked")

    fetcher = HttpSourceFetcher()
    fetcher._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))  # type: ignore[attr-defined]
    with pytest.raises(SourceFetchError):
        await fetcher.fetch("https://example.test/latest", since=datetime(2026, 7, 21, tzinfo=UTC))
