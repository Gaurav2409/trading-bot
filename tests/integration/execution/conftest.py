import os
from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from trading_os.execution.reservations import ReservationStore, reservations_metadata

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://trading:trading@localhost:5432/trading",
)


@pytest_asyncio.fixture(scope="module")
async def engine() -> AsyncIterator[object]:
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(reservations_metadata.drop_all)
        await conn.run_sync(reservations_metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(reservations_metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def reservation_store(engine: object) -> AsyncIterator[ReservationStore]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)  # type: ignore[arg-type]
    async with session_factory() as session:
        yield ReservationStore(session)
