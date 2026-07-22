from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from trading_os.kernel.events import EventEnvelope
from trading_os.ledger.tables import EventRow


class ConcurrencyError(RuntimeError):
    pass


class EventStore:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(
        self,
        stream_id: str,
        expected_version: int,
        events: Sequence[EventEnvelope[dict[str, object]]],
    ) -> int:
        current = await self._session.scalar(
            select(func.coalesce(func.max(EventRow.stream_version), 0)).where(
                EventRow.stream_id == stream_id
            )
        )
        current = int(current or 0)
        requested_ids = {str(event.event_id) for event in events}
        existing_ids = set(
            (
                await self._session.scalars(
                    select(EventRow.event_id).where(EventRow.event_id.in_(requested_ids))
                )
            ).all()
        )
        if requested_ids and existing_ids == requested_ids:
            return current
        if current != expected_version:
            raise ConcurrencyError(f"expected {expected_version}, found {current}")
        for offset, event in enumerate(events, start=1):
            self._session.add(EventRow.from_envelope(stream_id, current + offset, event))
        await self._session.commit()
        return current + len(events)

    async def read_stream(self, stream_id: str) -> list[EventRow]:
        query: Select[tuple[EventRow]] = (
            select(EventRow)
            .where(EventRow.stream_id == stream_id)
            .order_by(EventRow.stream_version)
        )
        return list((await self._session.scalars(query)).all())
