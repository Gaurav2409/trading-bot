from pydantic import BaseModel

from trading_os.kernel.ids import AccountId, InstrumentId
from trading_os.portfolio.models import CashBuckets, PositionBuckets


class AccountPortfolioProjection(BaseModel, frozen=True):
    """A partitioned view of exactly one Brokerage Account."""

    account_id: AccountId
    broker: str
    base_currency: str
    positions: dict[InstrumentId, PositionBuckets]
    cash: CashBuckets

    @property
    def available_minor(self) -> int:
        return self.cash.available_minor


class OwnerPortfolioCut(BaseModel, frozen=True):
    """Partition-preserving aggregation over compatible account projections.

    Exposes per-account accessors and analytical exposure only. It deliberately
    provides no combined buying power, saleable quantity or order reservation:
    execution resources are never netted across accounts or currencies.
    """

    account_projections: tuple[AccountPortfolioProjection, ...]

    def account(self, account_id: AccountId) -> AccountPortfolioProjection:
        for projection in self.account_projections:
            if projection.account_id == account_id:
                return projection
        raise KeyError(f"no projection for account {account_id}")

    def available_minor_for(self, account_id: AccountId) -> int:
        return self.account(account_id).available_minor
