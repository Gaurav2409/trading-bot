from trading_os.brokers.models import OrderAck, OrderRequest
from trading_os.brokers.ports import BrokerPort
from trading_os.kernel.events import new_event
from trading_os.ledger.store import EventStore


class ExecutionCoordinator:
    """Ordered, crash-safe side-effect protocol.

    Appends a durable OrderIntentCreated before broker submission, submits with
    the intent id as the client_order_id, then appends the acknowledgement. On
    restart the intent stream is replayed: if an acknowledgement already exists,
    the coordinator does not resubmit. The broker's own idempotency (same
    client_order_id -> same broker_order_id) is the second line of defense.
    """

    def __init__(self, event_store: EventStore, broker: BrokerPort) -> None:
        self._events = event_store
        self._broker = broker

    def _stream(self, client_order_id: str) -> str:
        return f"order:{client_order_id}"

    async def submit(self, request: OrderRequest) -> OrderAck:
        stream = self._stream(request.client_order_id)
        existing = await self._events.read_stream(stream)

        # Replay: if we already acknowledged this intent, return the recorded ack
        # without a duplicate broker submission.
        for row in existing:
            if row.event_type == "OrderAcknowledged":
                return OrderAck(
                    client_order_id=row.payload["client_order_id"],
                    broker_order_id=row.payload["broker_order_id"],
                    accepted_at=request.submitted_after,
                    status=row.payload["status"],
                )

        # Append the durable intent before any broker side effect (idempotent
        # append: replaying the same intent event is a no-op).
        if not existing:
            intent_event = new_event(
                "OrderIntentCreated",
                {
                    "client_order_id": request.client_order_id,
                    "account_id": str(request.account_id),
                    "instrument_id": str(request.instrument_id),
                    "side": request.side.value,
                    "quantity": request.quantity,
                },
            )
            await self._events.append(stream, 0, [intent_event])

        # Submit; broker is idempotent by client_order_id.
        ack = await self._broker.submit_order(request)

        ack_event = new_event(
            "OrderAcknowledged",
            {
                "client_order_id": ack.client_order_id,
                "broker_order_id": ack.broker_order_id,
                "status": ack.status,
            },
        )
        # Append after the intent (version 1 already used by the intent).
        current = await self._events.read_stream(stream)
        await self._events.append(stream, len(current), [ack_event])
        return ack
