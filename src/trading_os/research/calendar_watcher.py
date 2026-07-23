import json
from datetime import datetime

from pydantic import BaseModel

from trading_os.research.source_fetch import SourceFetchError, SourceFetchPort


class WatchScheduled(BaseModel, frozen=True):
    """Tier-2 early signal: an event is expected. Attention-only; this can never
    become an EvidencePacket. It carries no assessment, citation, or effect."""

    issuer_id: str
    event_kind: str
    expected_at: datetime
    authority_tier: str
    provenance_endpoint: str


class CalendarWatcher:
    def __init__(
        self, fetch_port: SourceFetchPort, endpoint: str, *, authority_tier: str = "official_calendar"
    ) -> None:
        self._fetch = fetch_port
        self._endpoint = endpoint
        self._authority_tier = authority_tier

    async def poll(self, since: datetime) -> tuple[WatchScheduled, ...]:
        try:
            raw = await self._fetch.fetch(self._endpoint, since=since)
            items = json.loads(raw.payload)
            if not isinstance(items, list):
                return ()
        except (SourceFetchError, json.JSONDecodeError):
            return ()
        intents: list[WatchScheduled] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                issuer_id = str(item["issuerId"])
                event_kind = str(item["eventKind"])
                expected_at = datetime.fromisoformat(
                    str(item["expectedDateTime"]).replace("Z", "+00:00")
                )
            except (KeyError, ValueError):
                continue
            intents.append(
                WatchScheduled(
                    issuer_id=issuer_id,
                    event_kind=event_kind,
                    expected_at=expected_at,
                    authority_tier=self._authority_tier,
                    provenance_endpoint=self._endpoint,
                )
            )
        return tuple(intents)
