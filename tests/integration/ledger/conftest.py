import os
from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from trading_os.ledger.store import EventStore
from trading_os.ledger.tables import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://trading:trading@localhost:5432/trading",
)

# Append-only guard DDL, kept in sync with migrations/versions/0001_event_ledger.py.
_IMMUTABLE_FUNCTION = """
CREATE OR REPLACE FUNCTION trading_os_event_log_immutable()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'event_log is append-only: % is not permitted', TG_OP;
END;
$$ LANGUAGE plpgsql;
"""
_IMMUTABLE_TRIGGER = """
CREATE TRIGGER event_log_no_update_delete
BEFORE UPDATE OR DELETE ON event_log
FOR EACH ROW EXECUTE FUNCTION trading_os_event_log_immutable();
"""


@pytest_asyncio.fixture(scope="module")
async def engine() -> AsyncIterator[object]:
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(_IMMUTABLE_FUNCTION))
        await conn.execute(text(_IMMUTABLE_TRIGGER))
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def event_store(engine: object) -> AsyncIterator[EventStore]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)  # type: ignore[arg-type]
    async with session_factory() as session:
        yield EventStore(session)


@pytest_asyncio.fixture
def apply_migrations() -> None:
    """Marker fixture: the engine fixture installs the append-only guard DDL."""
    return None

