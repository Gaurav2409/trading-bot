from pydantic import BaseModel, Field
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class ReservationBase(DeclarativeBase):
    pass


reservations_metadata = ReservationBase.metadata


class ReservationRow(ReservationBase):
    __tablename__ = "order_reservation"
    __table_args__ = (UniqueConstraint("account_id", "cas_version", name="uq_reservation_cas"),)

    reservation_id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str] = mapped_column(String, index=True)
    cas_version: Mapped[int] = mapped_column(Integer)
    cash_minor: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    risk_minor: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="held")


class OrderReservation(BaseModel, frozen=True):
    reservation_id: str
    account_id: str
    cas_version: int
    policy_release_ids: tuple[str, ...]
    cash_minor: int = Field(ge=0)
    quantity: int = Field(ge=0)
    risk_minor: int = Field(ge=0)


class ReservationConflict(RuntimeError):
    pass


class ReservationStore:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def reserve(self, reservation: OrderReservation) -> bool:
        """Reserve cash/quantity/risk against a snapshot CAS version. Two
        reservations against the same (account, cas_version) cannot both commit:
        the unique constraint forces at most one winner."""
        self._session.add(
            ReservationRow(
                reservation_id=reservation.reservation_id,
                account_id=reservation.account_id,
                cas_version=reservation.cas_version,
                cash_minor=reservation.cash_minor,
                quantity=reservation.quantity,
                risk_minor=reservation.risk_minor,
                status="held",
            )
        )
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ReservationConflict(
                f"CAS version {reservation.cas_version} already reserved for "
                f"{reservation.account_id}"
            ) from exc
        return True

    async def release(self, reservation_id: str) -> None:
        """Idempotent: releasing an unknown or already-released reservation is a
        no-op."""
        row = await self._session.get(ReservationRow, reservation_id)
        if row is None or row.status == "released":
            return
        row.status = "released"
        await self._session.commit()
