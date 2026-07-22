from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

from trading_os.kernel.ids import EventId

T = TypeVar("T")


class EventEnvelope(BaseModel, Generic[T], frozen=True):
    event_id: EventId
    event_type: str
    payload: T
    recorded_at: datetime
    valid_at: datetime | None = None
    correlation_id: str | None = None
    causation_id: EventId | None = None
    schema_version: int = Field(default=1, ge=1)


def new_event(event_type: str, payload: dict[str, Any]) -> EventEnvelope[dict[str, Any]]:
    return EventEnvelope(
        event_id=EventId(str(uuid4())),
        event_type=event_type,
        payload=payload,
        recorded_at=datetime.now(UTC),
    )
