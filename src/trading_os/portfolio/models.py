from pydantic import BaseModel, Field

from trading_os.kernel.ids import AccountId


class PositionBuckets(BaseModel, frozen=True):
    settled_available: int = Field(ge=0)
    unsettled: int = Field(ge=0)
    pledged: int = Field(ge=0)
    liened: int = Field(ge=0)
    authorization_blocked: int = Field(ge=0)
    broker_saleable: int = Field(ge=0)
    local_sell_reserved: int = Field(ge=0)
    pending_buy: int = Field(ge=0)
    pending_sell: int = Field(ge=0)

    @property
    def total_owned(self) -> int:
        return self.settled_available + self.unsettled + self.pledged + self.liened

    @property
    def saleable_now(self) -> int:
        return max(0, self.broker_saleable - self.local_sell_reserved)


class CashBuckets(BaseModel, frozen=True):
    currency: str
    settled_minor: int
    unsettled_minor: int
    broker_available_minor: int
    os_reserved_minor: int = Field(ge=0)
    pending_debit_minor: int = Field(ge=0)
    pending_credit_minor: int = Field(ge=0)

    @property
    def available_minor(self) -> int:
        return max(
            0,
            self.broker_available_minor - self.os_reserved_minor - self.pending_debit_minor,
        )


class ReconciliationConflict(BaseModel, frozen=True):
    account_id: AccountId
    field_name: str
    broker_value: str
    os_value: str
    fail_direction: str
