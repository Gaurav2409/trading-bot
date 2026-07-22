from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class QuantityUnit(StrEnum):
    SHARES = "shares"
    CONTRACTS = "contracts"
    BASE_CURRENCY = "base_currency"
    QUOTE_CURRENCY = "quote_currency"


class Money(BaseModel, frozen=True):
    currency: str
    minor_units: int

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if len(value) != 3 or value != value.upper():
            raise ValueError("currency must be a three-letter uppercase code")
        return value


class Quantity(BaseModel, frozen=True):
    value: Decimal = Field(ge=Decimal("0"))
    unit: QuantityUnit
