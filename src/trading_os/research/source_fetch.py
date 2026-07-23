from datetime import datetime
from typing import Protocol

import httpx
from pydantic import BaseModel


class SourceFetchError(RuntimeError):
    """A transport-level failure (network, anti-bot block, timeout, bad status)."""


class RawFetchResult(BaseModel, frozen=True):
    endpoint: str
    status: int
    fetched_at: datetime
    payload: str


class SourceFetchPort(Protocol):
    async def fetch(self, endpoint: str, *, since: datetime) -> RawFetchResult: ...


class FixtureSourceFetcher:
    """Deterministic offline fetcher; replays recorded results by endpoint."""

    def __init__(self, results: dict[str, RawFetchResult | SourceFetchError]) -> None:
        self._results = dict(results)

    async def fetch(self, endpoint: str, *, since: datetime) -> RawFetchResult:
        recorded = self._results.get(endpoint)
        if recorded is None:
            raise SourceFetchError(f"no fixture for endpoint {endpoint!r}")
        if isinstance(recorded, SourceFetchError):
            raise recorded
        return recorded


class HttpSourceFetcher:
    """Live transport for NSE/BSE endpoints. Integration-only; not exercised by
    the default offline gate. Maps non-2xx and transport errors to SourceFetchError.
    """

    def __init__(
        self,
        base_headers: dict[str, str] | None = None,
        *,
        timeout_s: float = 10.0,
        max_bytes: int = 2_000_000,
        warmup_url: str | None = None,
    ) -> None:
        self._headers = base_headers or {
            "User-Agent": "Mozilla/5.0 (compatible; trading-os/1.0)",
            "Accept": "application/json,text/plain,*/*",
        }
        self._timeout_s = timeout_s
        self._max_bytes = max_bytes
        self._warmup_url = warmup_url
        self._client = httpx.AsyncClient(headers=self._headers, timeout=timeout_s)

    async def fetch(self, endpoint: str, *, since: datetime) -> RawFetchResult:
        try:
            if self._warmup_url is not None:
                await self._client.get(self._warmup_url)  # establishes cookies
            response = await self._client.get(endpoint)
        except httpx.HTTPError as exc:
            raise SourceFetchError(f"transport error for {endpoint}: {exc}") from exc
        if response.status_code >= 400:
            raise SourceFetchError(f"bad status {response.status_code} for {endpoint}")
        text = response.text
        if len(text.encode()) > self._max_bytes:
            raise SourceFetchError(f"result exceeds {self._max_bytes} bytes for {endpoint}")
        return RawFetchResult(
            endpoint=endpoint,
            status=response.status_code,
            fetched_at=since,
            payload=text,
        )
