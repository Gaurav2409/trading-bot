"""Reusable normalized-broker contract suite.

Any BrokerPort implementation (fake, Kite, Alpaca) must satisfy these behaviors.
Subclass ``BrokerContract`` and implement ``make_broker`` to bind the suite to a
concrete adapter.
"""

from datetime import UTC, datetime

import pytest

from trading_os.brokers.models import OrderRequest, OrderSide, OrderType
from trading_os.brokers.ports import BrokerPort
from trading_os.kernel.ids import AccountId, InstrumentId


class BrokerContract:
    account_id: AccountId = AccountId("acct-1")
    currency: str = "INR"

    async def make_broker(self) -> BrokerPort:
        raise NotImplementedError

    def _request(self, client_order_id: str = "intent-1", quantity: int = 1) -> OrderRequest:
        return OrderRequest(
            account_id=self.account_id,
            client_order_id=client_order_id,
            instrument_id=InstrumentId("NSE:INE009A01021"),
            side=OrderSide.BUY,
            quantity=quantity,
            order_type=OrderType.LIMIT,
            limit_price_minor=150_000,
            submitted_after=datetime.now(UTC),
        )

    async def test_observation_timestamps_are_utc(self) -> None:
        broker = await self.make_broker()
        obs = await broker.observe_account()
        assert obs.received_at.tzinfo is UTC
        if obs.observed_at is not None:
            assert obs.observed_at.tzinfo is UTC

    async def test_position_buckets_are_non_negative(self) -> None:
        broker = await self.make_broker()
        obs = await broker.observe_account()
        for line in obs.positions:
            assert line.settled_available_quantity >= 0
            assert line.unsettled_quantity >= 0
            assert line.pledged_quantity >= 0
            assert line.authorization_blocked_quantity >= 0
            assert line.broker_saleable_quantity >= 0

    async def test_submit_is_idempotent_by_client_order_id(self) -> None:
        broker = await self.make_broker()
        request = self._request()
        first = await broker.submit_order(request)
        second = await broker.submit_order(request)
        assert first.broker_order_id == second.broker_order_id

    async def test_duplicate_client_id_with_different_payload_is_rejected(self) -> None:
        broker = await self.make_broker()
        await broker.submit_order(self._request(client_order_id="dup", quantity=1))
        with pytest.raises(ValueError):
            await broker.submit_order(self._request(client_order_id="dup", quantity=5))

    async def test_cancel_is_idempotent(self) -> None:
        broker = await self.make_broker()
        ack = await broker.submit_order(self._request())
        await broker.cancel_order(ack.broker_order_id)
        await broker.cancel_order(ack.broker_order_id)
