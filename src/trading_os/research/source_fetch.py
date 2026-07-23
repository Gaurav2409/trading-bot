from datetime import datetime
from typing import Protocol

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
