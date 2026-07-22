from hypothesis import given
from hypothesis import strategies as st

from trading_os.kernel.ids import AccountId
from trading_os.portfolio.models import CashBuckets, PositionBuckets
from trading_os.portfolio.projector import AccountPortfolioProjection, OwnerPortfolioCut


@given(
    settled=st.integers(min_value=0, max_value=1_000_000),
    reserved=st.integers(min_value=0, max_value=1_000_000),
)
def test_saleable_never_exceeds_owned(settled: int, reserved: int) -> None:
    buckets = PositionBuckets(
        settled_available=settled,
        unsettled=0,
        pledged=0,
        liened=0,
        authorization_blocked=0,
        broker_saleable=settled,
        local_sell_reserved=reserved,
        pending_buy=0,
        pending_sell=0,
    )
    assert 0 <= buckets.saleable_now <= buckets.total_owned


def _projection(account_id: str, currency: str) -> AccountPortfolioProjection:
    return AccountPortfolioProjection(
        account_id=AccountId(account_id),
        broker="kite" if currency == "INR" else "alpaca",
        base_currency=currency,
        positions={},
        cash=CashBuckets(
            currency=currency,
            settled_minor=100_000,
            unsettled_minor=0,
            broker_available_minor=100_000,
            os_reserved_minor=0,
            pending_debit_minor=0,
            pending_credit_minor=0,
        ),
    )


def test_owner_cut_never_pools_cash_across_currencies() -> None:
    kite = _projection("kite-1", "INR")
    alpaca = _projection("alpaca-1", "USD")
    cut = OwnerPortfolioCut(account_projections=(kite, alpaca))
    # No combined buying power is exposed; each partition keeps its own cash.
    assert not hasattr(cut, "combined_available_minor")
    assert cut.available_minor_for(AccountId("kite-1")) == 100_000
    assert cut.available_minor_for(AccountId("alpaca-1")) == 100_000


def test_inr_cash_cannot_fund_alpaca_order() -> None:
    kite = _projection("kite-1", "INR")
    alpaca = _projection("alpaca-1", "USD")
    cut = OwnerPortfolioCut(account_projections=(kite, alpaca))
    # There is no cross-account funding accessor; the only accessor is per account.
    assert cut.available_minor_for(AccountId("alpaca-1")) == 100_000
    # INR partition is independent; accessing a foreign account for funding is not offered.
    assert cut.account(AccountId("kite-1")).base_currency == "INR"
    assert cut.account(AccountId("alpaca-1")).base_currency == "USD"
