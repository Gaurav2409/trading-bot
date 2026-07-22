from typing import Protocol

from trading_os.brokers.models import BrokerSnapshotObservation, OrderAck, OrderRequest


class BrokerPort(Protocol):
    async def observe_account(self) -> BrokerSnapshotObservation:
        raise NotImplementedError

    async def submit_order(self, request: OrderRequest) -> OrderAck:
        raise NotImplementedError

    async def cancel_order(self, broker_order_id: str) -> None:
        raise NotImplementedError
