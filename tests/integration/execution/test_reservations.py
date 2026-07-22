import pytest

from trading_os.execution.reservations import (
    OrderReservation,
    ReservationConflict,
    ReservationStore,
)


async def test_two_reservations_same_cas_version_only_one_commits(
    reservation_store: ReservationStore,
) -> None:
    r1 = OrderReservation(
        reservation_id="res-1",
        account_id="kite-1",
        cas_version=7,
        policy_release_ids=("cap-1",),
        cash_minor=100_000,
        quantity=5,
        risk_minor=25_000,
    )
    r2 = OrderReservation(
        reservation_id="res-2",
        account_id="kite-1",
        cas_version=7,
        policy_release_ids=("cap-1",),
        cash_minor=100_000,
        quantity=5,
        risk_minor=25_000,
    )
    assert await reservation_store.reserve(r1) is True
    with pytest.raises(ReservationConflict):
        await reservation_store.reserve(r2)


async def test_release_is_idempotent(reservation_store: ReservationStore) -> None:
    r1 = OrderReservation(
        reservation_id="res-3",
        account_id="alpaca-1",
        cas_version=3,
        policy_release_ids=("cap-2",),
        cash_minor=5_000,
        quantity=1,
        risk_minor=1_000,
    )
    await reservation_store.reserve(r1)
    await reservation_store.release("res-3")
    await reservation_store.release("res-3")  # idempotent
