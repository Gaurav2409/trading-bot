from datetime import UTC, datetime

import pytest

from trading_os.brokers.kite import KiteBroker
from trading_os.brokers.mapping import LiveWriteDisabled
from trading_os.brokers.models import OrderRequest, OrderSide, OrderType
from trading_os.kernel.ids import AccountId, InstrumentId
from trading_os.policy.capability import AuthorityDecision


class RecordingKiteClient:
    def __init__(self) -> None:
        self.place_calls: list[dict[str, object]] = []

    def place_order(self, **kwargs: object) -> dict[str, str]:
        self.place_calls.append(kwargs)
        return {"order_id": "kite-live-1"}


def _request() -> OrderRequest:
    return OrderRequest(
        account_id=AccountId("kite-1"),
        client_order_id="intent-1",
        instrument_id=InstrumentId("NSE:INE009A01021"),
        side=OrderSide.BUY,
        quantity=1,
        order_type=OrderType.LIMIT,
        limit_price_minor=150_000,
        submitted_after=datetime.now(UTC),
    )


async def test_kite_write_denied_without_authority_never_calls_sdk() -> None:
    client = RecordingKiteClient()
    broker = KiteBroker(AccountId("kite-1"), client)
    denied = AuthorityDecision(allowed=False, reason="account_capability_missing")
    with pytest.raises(LiveWriteDisabled):
        await broker.submit_order(_request(), authority=denied)
    assert client.place_calls == []  # SDK never invoked before authority passes


async def test_kite_write_allowed_calls_sdk_once() -> None:
    client = RecordingKiteClient()
    broker = KiteBroker(AccountId("kite-1"), client)
    allowed = AuthorityDecision(allowed=True, reason="all_authorities_effective")
    ack = await broker.submit_order(_request(), authority=allowed)
    assert ack.broker_order_id == "kite-live-1"
    assert len(client.place_calls) == 1
    # India: only limit/stop-limit order types reach the SDK, never market.
    assert client.place_calls[0]["order_type"] in {"LIMIT", "SL"}
