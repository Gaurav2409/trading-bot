from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading_os.kernel.values import Money, Quantity, QuantityUnit


def test_money_rejects_lowercase_currency() -> None:
    with pytest.raises(ValidationError):
        Money(currency="inr", minor_units=1)


def test_quantity_carries_unit() -> None:
    quantity = Quantity(value=Decimal("2"), unit=QuantityUnit.SHARES)
    assert quantity.value == Decimal("2")
