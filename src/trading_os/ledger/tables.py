from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from trading_os.kernel.events import EventEnvelope


class Base(DeclarativeBase):
    pass


class EventRow(Base):
    __tablename__ = "event_log"
    __table_args__ = (UniqueConstraint("stream_id", "stream_version"),)

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    stream_id: Mapped[str] = mapped_column(String, index=True)
    stream_version: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    correlation_id: Mapped[str | None] = mapped_column(String)
    causation_id: Mapped[str | None] = mapped_column(String)
    schema_version: Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_envelope(
        cls,
        stream_id: str,
        stream_version: int,
        event: EventEnvelope[dict[str, object]],
    ) -> "EventRow":
        return cls(
            event_id=str(event.event_id),
            stream_id=stream_id,
            stream_version=stream_version,
            event_type=event.event_type,
            payload=dict(event.payload),
            recorded_at=event.recorded_at,
            valid_at=event.valid_at,
            correlation_id=event.correlation_id,
            causation_id=None if event.causation_id is None else str(event.causation_id),
            schema_version=event.schema_version,
        )
