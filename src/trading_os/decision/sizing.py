from pydantic import BaseModel, Field


class SizingInput(BaseModel, frozen=True):
    available_cash_minor: int = Field(ge=0)
    capital_minor: int = Field(gt=0)
    risk_fraction_ppm: int = Field(gt=0, le=1_000_000)
    entry_price_minor: int = Field(gt=0)
    stop_price_minor: int = Field(gt=0)
    max_symbol_minor: int = Field(gt=0)
    lot_size: int = Field(gt=0)


class ProvisionalSize(BaseModel, frozen=True):
    quantity: int = Field(ge=0)
    notional_minor: int = Field(ge=0)
    risk_minor: int = Field(ge=0)


def size_cash_equity(value: SizingInput) -> ProvisionalSize:
    """Deterministic fixed-fractional sizing. Integer (minor-unit) arithmetic
    only — no floats, no conviction input; conviction never scales size."""
    risk_per_share = value.entry_price_minor - value.stop_price_minor
    if risk_per_share <= 0:
        return ProvisionalSize(quantity=0, notional_minor=0, risk_minor=0)
    risk_budget = value.capital_minor * value.risk_fraction_ppm // 1_000_000
    by_risk = risk_budget // risk_per_share
    by_cash = value.available_cash_minor // value.entry_price_minor
    by_symbol = value.max_symbol_minor // value.entry_price_minor
    raw = min(by_risk, by_cash, by_symbol)
    quantity = raw - raw % value.lot_size
    return ProvisionalSize(
        quantity=quantity,
        notional_minor=quantity * value.entry_price_minor,
        risk_minor=quantity * risk_per_share,
    )
