from datetime import datetime

from pydantic import BaseModel

from trading_os.brokers.models import OrderSide, OrderType


class OrderIntent(BaseModel, frozen=True):
    client_order_id: str
    account_id: str
    instrument_id: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    limit_price_minor: int
    stop_price_minor: int | None
    created_at: datetime
