from datetime import UTC, datetime

from tests.contract.brokers.contract import BrokerContract

from trading_os.brokers.fake import FakeBroker
from trading_os.brokers.models import OrderRequest, OrderSide, OrderType
from trading_os.brokers.ports import BrokerPort
from trading_os.kernel.ids import AccountId, InstrumentId


async def test_fake_broker_is_idempotent_by_client_order_id() -> None:
    broker = FakeBroker.empty(AccountId("acct-1"), "INR")
    request = OrderRequest(
        account_id=AccountId("acct-1"),
        client_order_id="intent-1",
        instrument_id=InstrumentId("NSE:INE009A01021"),
        side=OrderSide.BUY,
        quantity=1,
        order_type=OrderType.LIMIT,
        limit_price_minor=150_000,
        submitted_after=datetime.now(UTC),
    )
    first = await broker.submit_order(request)
    second = await broker.submit_order(request)
    assert first.broker_order_id == second.broker_order_id


class TestFakeBrokerContract(BrokerContract):
    async def make_broker(self) -> BrokerPort:
        return FakeBroker.empty(self.account_id, self.currency)
