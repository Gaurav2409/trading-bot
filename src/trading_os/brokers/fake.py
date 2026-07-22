from datetime import UTC, datetime

from trading_os.brokers.models import (
    BrokerSnapshotObservation,
    OrderAck,
    OrderRequest,
    OrderSide,
)
from trading_os.kernel.ids import AccountId, SnapshotId


class FakeBroker:
    """Deterministic in-memory broker for contract tests.

    Never touches a network. Idempotent by client_order_id; rejects shorts,
    non-positive quantities, unknown accounts, and duplicate client IDs whose
    payload differs from the first submission.
    """

    def __init__(
        self,
        account_id: AccountId,
        currency: str,
        observation: BrokerSnapshotObservation,
    ) -> None:
        self._account_id = account_id
        self._currency = currency
        self._observation = observation
        self._orders: dict[str, tuple[OrderRequest, OrderAck]] = {}
        self._cancelled: set[str] = set()
        self._counter = 0

    @classmethod
    def empty(cls, account_id: AccountId, currency: str) -> "FakeBroker":
        observation = BrokerSnapshotObservation(
            observation_id=SnapshotId(f"fake-obs-{account_id}"),
            account_id=account_id,
            broker="fake",
            observed_at=datetime.now(UTC),
            received_at=datetime.now(UTC),
            positions=(),
            cash=(),
            open_orders=(),
        )
        return cls(account_id, currency, observation)

    async def observe_account(self) -> BrokerSnapshotObservation:
        return self._observation

    async def submit_order(self, request: OrderRequest) -> OrderAck:
        if request.account_id != self._account_id:
            raise ValueError(f"unknown account {request.account_id}")
        if request.side is not OrderSide.BUY:
            raise ValueError("fake broker is long-only in V1")
        if request.quantity <= 0:
            raise ValueError("quantity must be positive")
        existing = self._orders.get(request.client_order_id)
        if existing is not None:
            prior_request, prior_ack = existing
            if prior_request != request:
                raise ValueError(
                    f"client_order_id {request.client_order_id} reused with a different payload"
                )
            return prior_ack
        self._counter += 1
        ack = OrderAck(
            client_order_id=request.client_order_id,
            broker_order_id=f"fake-{self._counter}",
            accepted_at=datetime.now(UTC),
            status="accepted",
        )
        self._orders[request.client_order_id] = (request, ack)
        return ack

    async def cancel_order(self, broker_order_id: str) -> None:
        # Idempotent: cancelling an already-cancelled or unknown order is a no-op.
        self._cancelled.add(broker_order_id)
