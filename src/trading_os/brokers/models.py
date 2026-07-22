from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from trading_os.kernel.ids import AccountId, InstrumentId, SnapshotId


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    LIMIT = "limit"
    STOP_LIMIT = "stop_limit"


class PositionObservation(BaseModel, frozen=True):
    instrument_id: InstrumentId
    settled_available_quantity: int = Field(ge=0)
    unsettled_quantity: int = Field(ge=0)
    pledged_quantity: int = Field(ge=0)
    authorization_blocked_quantity: int = Field(ge=0)
    broker_saleable_quantity: int = Field(ge=0)
    average_cost_minor: int | None
    last_price_minor: int | None
    currency: str
    source_record_hash: str


class CashObservation(BaseModel, frozen=True):
    currency: str
    settled_minor: int
    broker_available_minor: int
    unsettled_minor: int
    source_record_hash: str


class OpenOrderObservation(BaseModel, frozen=True):
    broker_order_id: str
    client_order_id: str | None
    instrument_id: InstrumentId
    side: OrderSide
    remaining_quantity: int = Field(ge=0)
    limit_price_minor: int | None
    status: str


class BrokerSnapshotObservation(BaseModel, frozen=True):
    observation_id: SnapshotId
    account_id: AccountId
    broker: str
    observed_at: datetime | None
    received_at: datetime
    positions: tuple[PositionObservation, ...]
    cash: tuple[CashObservation, ...]
    open_orders: tuple[OpenOrderObservation, ...]
    missing_segments: frozenset[str] = frozenset()


class OrderRequest(BaseModel, frozen=True):
    account_id: AccountId
    client_order_id: str
    instrument_id: InstrumentId
    side: OrderSide
    quantity: int = Field(gt=0)
    order_type: OrderType
    limit_price_minor: int
    stop_price_minor: int | None = None
    submitted_after: datetime


class OrderAck(BaseModel, frozen=True):
    client_order_id: str
    broker_order_id: str
    accepted_at: datetime
    status: str
