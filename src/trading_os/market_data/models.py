from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from trading_os.kernel.ids import InstrumentId


class Bar(BaseModel, frozen=True):
    instrument_id: InstrumentId
    timeframe: str
    start: datetime
    end: datetime
    received_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal = Field(ge=0)
    source_id: str
    entitlement: str
    adjustment_set_id: str


class Quote(BaseModel, frozen=True):
    instrument_id: InstrumentId
    observed_at: datetime
    received_at: datetime
    bid: Decimal | None
    ask: Decimal | None
    last: Decimal | None
    source_id: str
    entitlement: str


class CorporateActionObservation(BaseModel, frozen=True):
    instrument_id: InstrumentId
    action_type: str
    published_at: datetime
    effective_at: datetime
    received_at: datetime
    ratio: Decimal | None = None
    source_id: str = ""


class FxMark(BaseModel, frozen=True):
    base_currency: str
    quote_currency: str
    rate: Decimal
    published_at: datetime
    received_at: datetime
    source_id: str
    entitlement: str


class AdjustedBar(BaseModel, frozen=True):
    """A derived adjusted series. Never overwrites raw bars; it references the
    raw bar and the corporate-action evidence used to derive it."""

    raw_instrument_id: InstrumentId
    raw_adjustment_set_id: str
    adjustment_set_id: str
    corporate_action_ids: tuple[str, ...]
    bar: Bar
