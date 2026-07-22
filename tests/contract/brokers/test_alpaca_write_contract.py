from datetime import UTC, datetime

import pytest

from trading_os.brokers.alpaca import AlpacaBroker
from trading_os.brokers.mapping import LiveWriteDisabled
from trading_os.brokers.models import OrderRequest, OrderSide, OrderType
from trading_os.kernel.ids import AccountId, InstrumentId
from trading_os.policy.capability import AuthorityDecision


class RecordingAlpacaClient:
    def __init__(self) -> None:
        self.submit_calls: list[dict[str, object]] = []

    def submit_order(self, **kwargs: object) -> dict[str, str]:
        self.submit_calls.append(kwargs)
        return {"id": "alpaca-live-1", "client_order_id": str(kwargs.get("client_order_id"))}


def _request() -> OrderRequest:
    return OrderRequest(
        account_id=AccountId("alpaca-1"),
        client_order_id="intent-1",
        instrument_id=InstrumentId("NASDAQ:TESTUS"),
        side=OrderSide.BUY,
        quantity=1,
        order_type=OrderType.LIMIT,
        limit_price_minor=5_000,
        submitted_after=datetime.now(UTC),
    )


async def test_alpaca_write_denied_without_authority_never_calls_sdk() -> None:
    client = RecordingAlpacaClient()
    broker = AlpacaBroker(AccountId("alpaca-1"), client)
    denied = AuthorityDecision(allowed=False, reason="broker_not_ready")
    with pytest.raises(LiveWriteDisabled):
        await broker.submit_order(_request(), authority=denied)
    assert client.submit_calls == []


async def test_alpaca_write_allowed_passes_client_order_id() -> None:
    client = RecordingAlpacaClient()
    broker = AlpacaBroker(AccountId("alpaca-1"), client)
    allowed = AuthorityDecision(allowed=True, reason="all_authorities_effective")
    ack = await broker.submit_order(_request(), authority=allowed)
    assert ack.broker_order_id == "alpaca-live-1"
    assert client.submit_calls[0]["client_order_id"] == "intent-1"
