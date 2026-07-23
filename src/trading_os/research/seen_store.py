from typing import Protocol


class SeenRecordStore(Protocol):
    def is_new(self, channel: str, record_id: str, payload_hash: str) -> bool: ...


class InMemorySeenRecordStore:
    def __init__(self) -> None:
        self._seen: set[tuple[str, str, str]] = set()

    def is_new(self, channel: str, record_id: str, payload_hash: str) -> bool:
        key = (channel, record_id, payload_hash)
        if key in self._seen:
            return False
        self._seen.add(key)
        return True
