# Nine-Day Two-Broker Live V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete first live vertical slice of the Trading OS in nine days: Zerodha and
Alpaca cash-equity sleeves, broad opportunity discovery, typed research, current portfolio analysis,
deterministic protected execution, reconciliation, retrospective diagnosis, and configurable
evidence-gated live authority.

**Architecture:** Build a modular Python event-ledger application with account-partitioned broker
observations, current portfolio projections, immutable policy releases, deterministic decisioning,
and ports-and-adapters broker integration. Postgres is the authoritative relational path; Valkey is
disposable coordination state; OWL/SHACL, Fuseki and Neo4j are rebuildable research projections.
The React console shows portfolio, candidates, decisions, controls, retrospectives and validated
TradingView Lightweight Charts, while agents consume numeric evidence rather than images.

**Tech Stack:** Python 3.11+, `uv`, Pydantic v2, pydantic-settings, SQLAlchemy 2, Alembic,
Postgres/TimescaleDB, asyncpg, Valkey, FastAPI, APScheduler, structlog, httpx, pandas/NumPy,
exchange-calendars, Kite Connect, alpaca-py, RDFLib, pySHACL, Fuseki/TDB2, Neo4j, pytest,
pytest-asyncio, Hypothesis, mypy, Ruff, TypeScript, React, Vite, Vitest, Playwright, and TradingView
Lightweight Charts.

## Required execution skills

- Start with `superpowers:using-git-worktrees` so implementation is isolated from the current dirty
  workspace.
- Use `superpowers:subagent-driven-development` for one fresh implementation agent per task, or
  `superpowers:executing-plans` when running the tasks inline.
- Use Matt Pocock's `codebase-design` vocabulary before finalizing each module boundary and
  `design-an-interface` when a port has more than one credible shape.
- Use `test-driven-development` for every behavior change: red, green, refactor.
- Use `requesting-code-review` after each day boundary and `verification-before-completion` before
  any live-readiness claim.
- Use `systematic-debugging` for any failing test or unexpected broker behavior.

## Global constraints

- `docs/superpowers/specs/2026-07-22-live-v1-architecture-amendment.md` is controlling.
- V1 execution is long-only, cash-funded cash equity through Zerodha and Alpaca only.
- Research types contain no quantity, price, target weight, broker order or execution method.
- Both accounts retain independent capital envelopes, orders, reconciliation and kill generations.
- Initial envelopes are INR 50,000 for Zerodha and USD 200 for Alpaca, with no automatic reload.
- Current portfolio analysis must include non-OS holdings, positions and open orders before sizing.
- Missing or conflicting critical portfolio dimensions block new exposure for the affected account.
- Deterministic provisional sizing occurs before post-trade risk/compliance tightening or veto.
- The semantic layer may influence economics only through an effective `DecisionFeatureActivation`;
  relational snapshot-scoped retrieval always remains available.
- Family and non-equity capability assignments remain deny-by-default in V1.
- Policy releases are immutable and effective-dated; changing a limit never rewrites history or
  resets loss/drawdown.
- A safety stop fences new exposure before human acknowledgement and keeps reconciliation and
  broker-native protection alive.
- India live orders use only order types allowed by the effective compliance profile; never assume
  algo market orders are permitted.
- Live execution is impossible unless an explicit broker-scoped `LiveAuthorityReceipt` matches the
  account, policy versions, readiness checks and current kill generation.
- Never commit credentials, access tokens, account numbers, raw broker payloads or live order logs.

## Nine-day delivery map

| Day | Tasks | Exit evidence |
|---|---|---|
| 1 | 1–3 | Clean toolchain; kernel, identity and immutable policy contracts pass |
| 2 | 4–6 | Event ledger, broker contract suite and read-only adapters pass fixture tests |
| 3 | 7–8 | Current portfolio normalization, completeness and analysis gate pass |
| 4 | 9–10 | Validated market snapshots, discovery coverage and tradability packets pass |
| 5 | 11 | Relational evidence champion, ontology kernel and typed agent seam pass |
| 6 | 12–13 | Deterministic sizing/risk plus India/US compliance pass replay tests |
| 7 | 14–15 | Durable execution, protection, kill states and broker write adapters pass |
| 8 | 16–17 | Reconciliation, retrospective, API and operator console pass end-to-end tests |
| 9 | 18 | Both broker T0 readiness receipts and reversible live activation runbook pass |

## Planned file structure

```text
src/trading_os/
  app/                 settings, dependency wiring, scheduler, CLI, API
  kernel/              IDs, money, quantity, time, event envelopes
  identity/            legal party, profile, ownership, account access and mandates
  policy/              immutable releases, assignments, activation and evaluation
  ledger/              append-only Postgres store, projections and migrations
  brokers/             normalized ports, fake, Kite and Alpaca adapters
  portfolio/           observations, authority, normalization, completeness and analysis
  market_data/         bars, prices, FX marks, validated snapshots and corporate actions
  discovery/           detector registry, momentum detector and coverage receipts
  tradability/         account-specific tradability/risk packet builders
  research/            evidence packets, source watchers, agent orchestration
  ontology/            OWL/SHACL source, semantic snapshot and projection ports
  decision/            eligibility, sizing, portfolio risk overlays and compliance
  execution/           reservations, intents, coordinator, protection and kill state
  retrospective/       decision/outcome linkage, diagnosis and challenger proposals
web/                    React operator console and Lightweight Charts
tests/                  unit, contract, integration, replay and live-readiness tests
deploy/                 Compose services, health checks and operator configuration
```

---

## Day 1 — Foundation

### Task 1: Replace the stale repository baseline and establish one-command verification

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `config/env.example`
- Create: `src/trading_os/__init__.py`
- Create: `src/trading_os/app/settings.py`
- Create: `tests/unit/app/test_settings.py`
- Create: `deploy/compose.yml`
- Create: `Makefile`

**Interfaces:**
- Consumes: the controlling spec and existing Python 3.11 project.
- Produces: `Settings`, the `trading_os` package, local services, and `make verify` used by every
  later task.

- [ ] **Step 1: Write the failing settings test**

```python
from trading_os.app.settings import Environment, Settings


def test_live_mode_is_disabled_by_default() -> None:
    settings = Settings(_env_file=None)
    assert settings.environment is Environment.DEVELOPMENT
    assert settings.live_mode_requested is False
    assert settings.database_url.startswith("postgresql+asyncpg://")
```

- [ ] **Step 2: Run the test and confirm the package is absent**

Run: `uv run pytest tests/unit/app/test_settings.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'trading_os'`.

- [ ] **Step 3: Replace obsolete dependencies and create settings**

Use this project dependency set in `pyproject.toml`; remove Angel One, IBKR, Polygon, automated TOTP
login, Europe/XETRA and the old 12-agent claim:

```toml
[project]
name = "trading-os"
version = "0.1.0"
description = "Evidence-gated two-broker cash-equity Trading OS"
requires-python = ">=3.11"
dependencies = [
  "alembic>=1.13",
  "alpaca-py>=0.26",
  "apscheduler>=3.10",
  "asyncpg>=0.29",
  "exchange-calendars>=4.5",
  "fastapi>=0.115",
  "httpx>=0.27",
  "kiteconnect>=5.0",
  "neo4j>=5.23",
  "numpy>=1.26",
  "pandas>=2.2",
  "pydantic>=2.7",
  "pydantic-settings>=2.3",
  "pyshacl>=0.26",
  "rdflib>=7.0",
  "sqlalchemy[asyncio]>=2.0",
  "structlog>=24.0",
  "uvicorn[standard]>=0.30",
  "valkey>=6.0",
]

[project.optional-dependencies]
dev = [
  "hypothesis>=6.100",
  "mypy>=1.10",
  "pytest>=8.0",
  "pytest-asyncio>=0.23",
  "pytest-cov>=5.0",
  "ruff>=0.4",
  "testcontainers[postgres]>=4.7",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
  "contract: normalized broker contract tests",
  "integration: local service integration tests",
  "live_readiness: read-only tests requiring explicit broker credentials",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
strict = true
python_version = "3.11"
```

Create `src/trading_os/app/settings.py`:

```python
from enum import StrEnum

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Environment = Environment.DEVELOPMENT
    live_mode_requested: bool = False
    database_url: str = "postgresql+asyncpg://trading:trading@localhost:5432/trading"
    valkey_url: str = "redis://localhost:6379/0"
    kite_api_key: SecretStr | None = None
    kite_access_token: SecretStr | None = None
    alpaca_api_key: SecretStr | None = None
    alpaca_secret_key: SecretStr | None = None
    alpaca_paper: bool = True
```

Create `src/trading_os/__init__.py` with `__all__: list[str] = []`. Configure Compose with
Postgres/TimescaleDB, Valkey, Fuseki and Neo4j health checks; use named volumes and bind services to
localhost. `Makefile` targets: `sync`, `services-up`, `services-down`, `lint`, `typecheck`, `test`,
`verify` where `verify` runs Ruff, mypy and pytest in that order.

- [ ] **Step 4: Update the safe environment template and README**

`config/env.example` must contain only non-secret names and live-safe defaults:

```dotenv
ENVIRONMENT=development
LIVE_MODE_REQUESTED=false
DATABASE_URL=postgresql+asyncpg://trading:trading@localhost:5432/trading
VALKEY_URL=redis://localhost:6379/0
KITE_API_KEY=
KITE_ACCESS_TOKEN=
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
ALPACA_PAPER=true
```

Document that live activation is a policy/readiness operation, not a base-URL edit, and that Kite
interactive login/session renewal is operator-owned rather than TOTP automation.

- [ ] **Step 5: Verify and commit**

Run: `uv sync --extra dev && make verify`

Expected: Ruff, mypy and the settings test pass.

```bash
git add pyproject.toml README.md config/env.example Makefile deploy/compose.yml src/trading_os tests/unit/app
git commit -m "chore: establish live-v1 project foundation"
```

### Task 2: Add the typed kernel and immutable event envelope

**Files:**
- Create: `src/trading_os/kernel/ids.py`
- Create: `src/trading_os/kernel/values.py`
- Create: `src/trading_os/kernel/events.py`
- Create: `tests/unit/kernel/test_values.py`
- Create: `tests/unit/kernel/test_events.py`

**Interfaces:**
- Consumes: Python, Pydantic and UTC time.
- Produces: `AccountId`, `InstrumentId`, `SnapshotId`, `ReleaseId`, `Money`, `Quantity`,
  `QuantityUnit`, `EventEnvelope[T]`, and `new_event()`.

- [ ] **Step 1: Write failing invariant tests**

```python
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading_os.kernel.events import new_event
from trading_os.kernel.ids import AccountId
from trading_os.kernel.values import Money, Quantity, QuantityUnit


def test_money_rejects_lowercase_currency() -> None:
    with pytest.raises(ValidationError):
        Money(currency="inr", minor_units=1)


def test_quantity_carries_unit() -> None:
    quantity = Quantity(value=Decimal("2"), unit=QuantityUnit.SHARES)
    assert quantity.value == Decimal("2")


def test_event_has_utc_recorded_time() -> None:
    event = new_event("AccountObserved", {"account_id": "acct-1"})
    assert event.recorded_at.tzinfo is UTC
    assert event.recorded_at <= datetime.now(UTC)
    assert AccountId("acct-1") == "acct-1"
```

- [ ] **Step 2: Run tests and verify the kernel is absent**

Run: `uv run pytest tests/unit/kernel -v`

Expected: FAIL importing `trading_os.kernel`.

- [ ] **Step 3: Implement IDs and value objects**

```python
# src/trading_os/kernel/ids.py
from typing import NewType

AccountId = NewType("AccountId", str)
InstrumentId = NewType("InstrumentId", str)
SnapshotId = NewType("SnapshotId", str)
ValidatedDataSnapshotId = NewType("ValidatedDataSnapshotId", str)
SemanticSnapshotId = NewType("SemanticSnapshotId", str)
ReleaseId = NewType("ReleaseId", str)
EventId = NewType("EventId", str)
TenantId = NewType("TenantId", str)
```

```python
# src/trading_os/kernel/values.py
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
```

- [ ] **Step 4: Implement the immutable event envelope**

```python
# src/trading_os/kernel/events.py
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

from trading_os.kernel.ids import EventId

T = TypeVar("T")


class EventEnvelope(BaseModel, Generic[T], frozen=True):
    event_id: EventId
    event_type: str
    payload: T
    recorded_at: datetime
    valid_at: datetime | None = None
    correlation_id: str | None = None
    causation_id: EventId | None = None
    schema_version: int = Field(default=1, ge=1)


def new_event(event_type: str, payload: dict[str, Any]) -> EventEnvelope[dict[str, Any]]:
    return EventEnvelope(
        event_id=EventId(str(uuid4())),
        event_type=event_type,
        payload=payload,
        recorded_at=datetime.now(UTC),
    )
```

- [ ] **Step 5: Verify and commit**

Run: `uv run pytest tests/unit/kernel -v && uv run mypy src/trading_os/kernel`

Expected: all tests and strict typing pass.

```bash
git add src/trading_os/kernel tests/unit/kernel
git commit -m "feat: add typed domain kernel"
```

### Task 3: Model legal parties, account authority and immutable policy releases

**Files:**
- Create: `src/trading_os/identity/models.py`
- Create: `src/trading_os/policy/models.py`
- Create: `src/trading_os/policy/evaluator.py`
- Create: `tests/unit/identity/test_authority.py`
- Create: `tests/unit/policy/test_releases.py`

**Interfaces:**
- Consumes: typed kernel values.
- Produces: `LegalParty`, `UserProfile`, `BrokerageAccount`, `BrokerConnectionRef`,
  `AccountAccessGrant`, `TradingMandate`, `Household`, `CapitalEnvelopeRelease`,
  `ExposurePolicyRelease`, `PromotionPolicyRelease`, `PolicySet`, and `PolicyEvaluator`.

- [ ] **Step 1: Write failing identity and policy tests**

```python
from datetime import UTC, datetime, timedelta

from trading_os.identity.models import AccessScope, AccountAccessGrant
from trading_os.kernel.ids import AccountId, ReleaseId
from trading_os.policy.evaluator import PolicyEvaluator
from trading_os.policy.models import CapitalEnvelopeRelease


def test_household_read_grant_does_not_authorize_execution() -> None:
    now = datetime.now(UTC)
    grant = AccountAccessGrant(
        grant_id="grant-1",
        account_id=AccountId("acct-1"),
        grantee_party_id="party-2",
        scopes=frozenset({AccessScope.READ}),
        effective_from=now - timedelta(minutes=1),
    )
    assert grant.allows(AccessScope.EXECUTE, now) is False


def test_capital_release_is_effective_dated() -> None:
    now = datetime.now(UTC)
    release = CapitalEnvelopeRelease(
        release_id=ReleaseId("capital-1"),
        account_id=AccountId("acct-1"),
        currency="INR",
        capital_minor=5_000_000,
        max_cumulative_loss_minor=5_000_000,
        effective_from=now - timedelta(seconds=1),
    )
    assert PolicyEvaluator().is_effective(release, now) is True
```

- [ ] **Step 2: Run tests and confirm missing models**

Run: `uv run pytest tests/unit/identity tests/unit/policy -v`

Expected: FAIL importing the identity and policy modules.

- [ ] **Step 3: Implement separate identity and authority types**

```python
# src/trading_os/identity/models.py
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from trading_os.kernel.ids import AccountId


class AccessScope(StrEnum):
    READ = "read"
    RECONCILE = "reconcile"
    PROPOSE = "propose"
    APPROVE = "approve"
    EXECUTE = "execute"


class LegalParty(BaseModel, frozen=True):
    party_id: str
    party_kind: str


class UserProfile(BaseModel, frozen=True):
    profile_id: str
    party_id: str
    tenant_id: str


class BrokerageAccount(BaseModel, frozen=True):
    account_id: AccountId
    broker: str
    environment: str
    external_account_hash: str
    base_currency: str


class BrokerConnectionRef(BaseModel, frozen=True):
    connection_id: str
    broker: str
    credential_secret_ref: str


class AccountAccessGrant(BaseModel, frozen=True):
    grant_id: str
    account_id: AccountId
    grantee_party_id: str
    scopes: frozenset[AccessScope]
    effective_from: datetime
    effective_until: datetime | None = None
    revoked_at: datetime | None = None

    def allows(self, scope: AccessScope, at: datetime) -> bool:
        return (
            scope in self.scopes
            and self.effective_from <= at
            and (self.effective_until is None or at < self.effective_until)
            and (self.revoked_at is None or at < self.revoked_at)
        )


class TradingMandate(AccountAccessGrant):
    strategy_ids: frozenset[str]


class Household(BaseModel, frozen=True):
    household_id: str
    display_name: str
```

- [ ] **Step 4: Implement immutable policy models and evaluation**

```python
# src/trading_os/policy/models.py
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from trading_os.kernel.ids import AccountId, ReleaseId


class EffectiveRelease(BaseModel, frozen=True):
    release_id: ReleaseId
    effective_from: datetime
    effective_until: datetime | None = None
    supersedes: ReleaseId | None = None


class CapitalEnvelopeRelease(EffectiveRelease):
    account_id: AccountId
    currency: str
    capital_minor: int = Field(gt=0)
    max_cumulative_loss_minor: int = Field(gt=0)
    automatic_reload: bool = False

    @model_validator(mode="after")
    def validate_loss_ceiling(self) -> "CapitalEnvelopeRelease":
        if self.max_cumulative_loss_minor > self.capital_minor:
            raise ValueError("maximum cumulative loss cannot exceed the capital envelope")
        return self


class ExposurePolicyRelease(EffectiveRelease):
    account_id: AccountId
    max_deployed_fraction: float = Field(gt=0, le=1)
    max_symbol_fraction: float = Field(gt=0, le=1)


class PromotionPolicyRelease(EffectiveRelease):
    account_id: AccountId
    tier: str
    required_protected_entries: int = Field(ge=0)
    required_reconciled_exits: int = Field(ge=0)
    daily_loss_cooldown_ppm: int = Field(ge=0, le=1_000_000)
    retrospective_drawdown_ppm: int = Field(ge=0, le=1_000_000)
    promotion_block_drawdown_ppm: int = Field(ge=0, le=1_000_000)
    demote_drawdown_ppm: int = Field(ge=0, le=1_000_000)
    restart_drawdown_ppm: int = Field(ge=0, le=1_000_000)
    stop_drawdown_ppm: int = Field(ge=0, le=1_000_000)


class PolicySet(BaseModel, frozen=True):
    capital: CapitalEnvelopeRelease
    exposure: ExposurePolicyRelease
    promotion: PromotionPolicyRelease
```

```python
# src/trading_os/policy/evaluator.py
from datetime import datetime

from trading_os.policy.models import EffectiveRelease


class PolicyEvaluator:
    def is_effective(self, release: EffectiveRelease, at: datetime) -> bool:
        return release.effective_from <= at and (
            release.effective_until is None or at < release.effective_until
        )
```

- [ ] **Step 5: Add initial-release fixture builders and verify**

Create test builders that produce the approved INR 50,000 and USD 200 T0 releases with 25% deployed
and 10% per-symbol limits. Assert `automatic_reload is False` and that changing Day-10 limits
requires a distinct `release_id` with `supersedes` set.

```python
def test_initial_capital_values_and_day_10_supersession(now) -> None:
    inr = CapitalEnvelopeRelease(
        release_id=ReleaseId("kite-capital-v1"), account_id=AccountId("kite-1"),
        currency="INR", capital_minor=5_000_000, max_cumulative_loss_minor=5_000_000,
        effective_from=now,
    )
    usd = CapitalEnvelopeRelease(
        release_id=ReleaseId("alpaca-capital-v1"), account_id=AccountId("alpaca-1"),
        currency="USD", capital_minor=20_000, max_cumulative_loss_minor=20_000,
        effective_from=now,
    )
    day_10 = inr.model_copy(
        update={
            "release_id": ReleaseId("kite-capital-v2"),
            "supersedes": inr.release_id,
            "effective_from": now + timedelta(days=10),
        }
    )
    assert inr.automatic_reload is False
    assert usd.automatic_reload is False
    assert day_10.release_id != inr.release_id
    assert day_10.supersedes == inr.release_id
```

Run: `uv run pytest tests/unit/identity tests/unit/policy -v && make verify`

Expected: tests, Ruff and mypy pass.

```bash
git add src/trading_os/identity src/trading_os/policy tests/unit/identity tests/unit/policy
git commit -m "feat: model account authority and policy releases"
```

---

## Day 2 — Durable state and broker observations

### Task 4: Add the append-only Postgres event store and replay contract

**Files:**
- Create: `src/trading_os/ledger/tables.py`
- Create: `src/trading_os/ledger/store.py`
- Create: `src/trading_os/ledger/replay.py`
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/versions/0001_event_ledger.py`
- Create: `tests/integration/ledger/conftest.py`
- Create: `tests/integration/ledger/test_event_store.py`

**Interfaces:**
- Consumes: `EventEnvelope` and Postgres.
- Produces: `EventStore.append()`, `EventStore.read_stream()`, optimistic stream versions and
  deterministic replay.

- [ ] **Step 1: Write the failing append/idempotency test**

```python
import pytest

from trading_os.kernel.events import new_event
from trading_os.ledger.store import ConcurrencyError, EventStore


async def test_append_is_idempotent_and_version_checked(event_store: EventStore) -> None:
    event = new_event("CapitalEnvelopeReleased", {"release_id": "capital-1"})
    assert await event_store.append("account:acct-1", 0, [event]) == 1
    assert await event_store.append("account:acct-1", 1, [event]) == 1
    with pytest.raises(ConcurrencyError):
        await event_store.append("account:acct-1", 0, [new_event("Other", {})])
```

- [ ] **Step 2: Run the integration test against local Postgres**

Run: `docker compose -f deploy/compose.yml up -d postgres && uv run pytest tests/integration/ledger/test_event_store.py -v`

Expected: FAIL importing `trading_os.ledger.store`.

- [ ] **Step 3: Create the append-only table and migration**

The `event_log` table must contain `event_id` primary key, `stream_id`, `stream_version`,
`event_type`, JSONB `payload`, `recorded_at`, nullable `valid_at`, `correlation_id`, `causation_id`,
and `schema_version`, with unique `(stream_id, stream_version)`. Add database rules or permissions
that deny UPDATE and DELETE to the runtime role.

```python
# src/trading_os/ledger/tables.py
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from trading_os.kernel.events import EventEnvelope


class Base(DeclarativeBase):
    pass


class EventRow(Base):
    __tablename__ = "event_log"
    __table_args__ = (UniqueConstraint("stream_id", "stream_version"),)

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    stream_id: Mapped[str] = mapped_column(String, index=True)
    stream_version: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    correlation_id: Mapped[str | None] = mapped_column(String)
    causation_id: Mapped[str | None] = mapped_column(String)
    schema_version: Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_envelope(
        cls,
        stream_id: str,
        stream_version: int,
        event: EventEnvelope[dict[str, object]],
    ) -> "EventRow":
        return cls(
            event_id=str(event.event_id),
            stream_id=stream_id,
            stream_version=stream_version,
            event_type=event.event_type,
            payload=dict(event.payload),
            recorded_at=event.recorded_at,
            valid_at=event.valid_at,
            correlation_id=event.correlation_id,
            causation_id=None if event.causation_id is None else str(event.causation_id),
            schema_version=event.schema_version,
        )
```

Create `tests/integration/ledger/conftest.py` with an async SQLAlchemy engine using
`TEST_DATABASE_URL` (defaulting to the local Compose test database), create/drop `Base.metadata` per
module, and yield a fresh `EventStore` backed by an `async_sessionmaker(expire_on_commit=False)`.

- [ ] **Step 4: Implement append and stream reads in one transaction**

```python
# src/trading_os/ledger/store.py
from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from trading_os.kernel.events import EventEnvelope
from trading_os.ledger.tables import EventRow


class ConcurrencyError(RuntimeError):
    pass


class EventStore:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(
        self,
        stream_id: str,
        expected_version: int,
        events: Sequence[EventEnvelope[dict[str, object]]],
    ) -> int:
        current = await self._session.scalar(
            select(func.coalesce(func.max(EventRow.stream_version), 0)).where(
                EventRow.stream_id == stream_id
            )
        )
        requested_ids = {str(event.event_id) for event in events}
        existing_ids = set(
            (
                await self._session.scalars(
                    select(EventRow.event_id).where(EventRow.event_id.in_(requested_ids))
                )
            ).all()
        )
        if requested_ids and existing_ids == requested_ids:
            return int(current)
        if current != expected_version:
            raise ConcurrencyError(f"expected {expected_version}, found {current}")
        for offset, event in enumerate(events, start=1):
            self._session.add(EventRow.from_envelope(stream_id, current + offset, event))
        await self._session.commit()
        return int(current) + len(events)

    async def read_stream(self, stream_id: str) -> list[EventRow]:
        query: Select[tuple[EventRow]] = select(EventRow).where(
            EventRow.stream_id == stream_id
        ).order_by(EventRow.stream_version)
        return list((await self._session.scalars(query)).all())
```

- [ ] **Step 5: Prove replay and append-only behavior**

Add tests that replay the same stream twice to identical state, reject conflicting stream versions,
and demonstrate the runtime role cannot update or delete an event.

Run: `uv run alembic upgrade head && uv run pytest tests/integration/ledger -v`

Expected: all ledger tests pass.

- [ ] **Step 6: Commit**

```bash
git add alembic.ini migrations src/trading_os/ledger tests/integration/ledger
git commit -m "feat: add append-only event ledger"
```

### Task 5: Freeze the normalized broker observation and execution ports

**Files:**
- Create: `src/trading_os/brokers/models.py`
- Create: `src/trading_os/brokers/ports.py`
- Create: `src/trading_os/brokers/fake.py`
- Create: `tests/contract/brokers/contract.py`
- Create: `tests/contract/brokers/test_fake_contract.py`

**Interfaces:**
- Consumes: account IDs, Money, Quantity, UTC clocks and client-order IDs.
- Produces: `BrokerPort`, `BrokerSnapshotObservation`, `PositionObservation`, `CashObservation`,
  `OpenOrderObservation`, `OrderRequest`, `OrderAck`, and a reusable broker contract suite.

- [ ] **Step 1: Write the fake-broker contract test**

```python
from datetime import UTC, datetime

from trading_os.brokers.fake import FakeBroker
from trading_os.brokers.models import OrderRequest, OrderSide, OrderType
from trading_os.kernel.ids import AccountId, InstrumentId


async def test_fake_broker_is_idempotent_by_client_order_id() -> None:
    broker = FakeBroker.empty(AccountId("acct-1"), "INR")
    request = OrderRequest(
        account_id=AccountId("acct-1"),
        client_order_id="intent-1",
        instrument_id=InstrumentId("NSE:INE009A01021"),
        side=OrderSide.BUY,
        quantity=1,
        order_type=OrderType.LIMIT,
        limit_price_minor=150_000,
        submitted_after=datetime.now(UTC),
    )
    first = await broker.submit_order(request)
    second = await broker.submit_order(request)
    assert first.broker_order_id == second.broker_order_id
```

- [ ] **Step 2: Run the contract test and confirm failure**

Run: `uv run pytest tests/contract/brokers/test_fake_contract.py -v`

Expected: FAIL importing broker modules.

- [ ] **Step 3: Define immutable observation and order models**

```python
# src/trading_os/brokers/models.py
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from trading_os.kernel.ids import AccountId, InstrumentId, SnapshotId


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    LIMIT = "limit"
    STOP_LIMIT = "stop_limit"


class PositionObservation(BaseModel, frozen=True):
    instrument_id: InstrumentId
    settled_available_quantity: int = Field(ge=0)
    unsettled_quantity: int = Field(ge=0)
    pledged_quantity: int = Field(ge=0)
    authorization_blocked_quantity: int = Field(ge=0)
    broker_saleable_quantity: int = Field(ge=0)
    average_cost_minor: int | None
    last_price_minor: int | None
    currency: str
    source_record_hash: str


class CashObservation(BaseModel, frozen=True):
    currency: str
    settled_minor: int
    broker_available_minor: int
    unsettled_minor: int
    source_record_hash: str


class OpenOrderObservation(BaseModel, frozen=True):
    broker_order_id: str
    client_order_id: str | None
    instrument_id: InstrumentId
    side: OrderSide
    remaining_quantity: int = Field(ge=0)
    limit_price_minor: int | None
    status: str


class BrokerSnapshotObservation(BaseModel, frozen=True):
    observation_id: SnapshotId
    account_id: AccountId
    broker: str
    observed_at: datetime | None
    received_at: datetime
    positions: tuple[PositionObservation, ...]
    cash: tuple[CashObservation, ...]
    open_orders: tuple[OpenOrderObservation, ...]
    missing_segments: frozenset[str] = frozenset()


class OrderRequest(BaseModel, frozen=True):
    account_id: AccountId
    client_order_id: str
    instrument_id: InstrumentId
    side: OrderSide
    quantity: int = Field(gt=0)
    order_type: OrderType
    limit_price_minor: int
    stop_price_minor: int | None = None
    submitted_after: datetime


class OrderAck(BaseModel, frozen=True):
    client_order_id: str
    broker_order_id: str
    accepted_at: datetime
    status: str
```

- [ ] **Step 4: Define the port and deterministic fake**

```python
# src/trading_os/brokers/ports.py
from typing import Protocol

from trading_os.brokers.models import BrokerSnapshotObservation, OrderAck, OrderRequest


class BrokerPort(Protocol):
    async def observe_account(self) -> BrokerSnapshotObservation:
        raise NotImplementedError

    async def submit_order(self, request: OrderRequest) -> OrderAck:
        raise NotImplementedError

    async def cancel_order(self, broker_order_id: str) -> None:
        raise NotImplementedError
```

Implement `FakeBroker` with an in-memory observation and a dictionary keyed by `client_order_id`;
reject shorts, non-positive quantities and unknown accounts.

- [ ] **Step 5: Build the reusable contract suite**

The suite must prove observation timestamps are UTC, position buckets are non-negative, order
submission is idempotent, duplicate client IDs with different payloads are rejected, and cancel is
idempotent. Run it against `FakeBroker` now and both real adapters in Task 6/15.

Run: `uv run pytest tests/contract/brokers -v && uv run mypy src/trading_os/brokers`

Expected: all contract tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/trading_os/brokers tests/contract/brokers
git commit -m "feat: define normalized broker contract"
```

### Task 6: Implement read-only Kite and Alpaca adapters with recorded fixtures

**Files:**
- Create: `src/trading_os/brokers/kite.py`
- Create: `src/trading_os/brokers/alpaca.py`
- Create: `src/trading_os/brokers/mapping.py`
- Create: `tests/fixtures/brokers/kite_portfolio.json`
- Create: `tests/fixtures/brokers/alpaca_portfolio.json`
- Create: `tests/contract/brokers/test_kite_read_contract.py`
- Create: `tests/contract/brokers/test_alpaca_read_contract.py`

**Interfaces:**
- Consumes: `BrokerPort`, broker SDK clients and canonical instrument mapping.
- Produces: read-only normalized account observations from Kite and Alpaca; write methods remain
  structurally disabled until Task 15.

- [ ] **Step 1: Write failing fixture-mapping tests**

```python
import json
from pathlib import Path

from trading_os.brokers.kite import map_kite_snapshot
from trading_os.kernel.ids import AccountId


def test_kite_t1_and_pledged_quantities_are_not_saleable_twice() -> None:
    payload = json.loads(Path("tests/fixtures/brokers/kite_portfolio.json").read_text())
    snapshot = map_kite_snapshot(AccountId("kite-1"), payload)
    line = snapshot.positions[0]
    assert line.unsettled_quantity == 2
    assert line.pledged_quantity == 1
    assert line.broker_saleable_quantity == 7
```

Add the symmetric Alpaca test proving a pre-existing position appears even when no OS client order
ID exists.

- [ ] **Step 2: Run mapping tests and verify failure**

Run: `uv run pytest tests/contract/brokers/test_kite_read_contract.py tests/contract/brokers/test_alpaca_read_contract.py -v`

Expected: FAIL importing adapter mapping functions.

- [ ] **Step 3: Add sanitized fixture payloads**

Use fabricated account IDs and instruments. The Kite fixture must contain one holding with quantity
10, T1 quantity 2, pledged quantity 1 and authorized quantity 7; its positions payload contains the
same symbol with zero overnight net quantity so the later normalizer can prove no double count. The
Alpaca fixture must contain one USD position, account cash and one open limit order. No fixture may
contain a real account number or token.

- [ ] **Step 4: Implement pure mapping before SDK I/O**

```python
# src/trading_os/brokers/mapping.py
from trading_os.kernel.ids import InstrumentId


def canonical_equity_id(venue: str, isin_or_symbol: str) -> InstrumentId:
    normalized_venue = venue.upper()
    normalized_key = isin_or_symbol.upper()
    return InstrumentId(f"{normalized_venue}:{normalized_key}")
```

`map_kite_snapshot()` and `map_alpaca_snapshot()` must accept plain dictionaries and produce
`BrokerSnapshotObservation` without network access. Preserve raw-payload SHA-256 hashes and record
`received_at` when the mapping starts.

- [ ] **Step 5: Add SDK-backed observation calls**

`KiteBroker.observe_account()` calls `holdings()`, `positions()`, `orders()` and `margins()` through
`anyio.to_thread.run_sync`; `AlpacaBroker.observe_account()` calls `get_all_positions()`,
`get_account()` and open-order retrieval. Each segment records success independently; a failed
segment produces a snapshot with that segment in `missing_segments`, never an empty-success value.
Both adapters raise `LiveWriteDisabled` for submit/cancel until Task 15.

- [ ] **Step 6: Run contract tests and commit**

Run: `uv run pytest tests/contract/brokers -v`

Expected: fake and both read-only mapping suites pass without credentials or network access.

```bash
git add src/trading_os/brokers tests/fixtures/brokers tests/contract/brokers
git commit -m "feat: add read-only Kite and Alpaca observations"
```

---

## Day 3 — Current portfolio analysis

### Task 7: Implement field authority, broker overlap rules and partitioned portfolio projection

**Files:**
- Create: `src/trading_os/portfolio/models.py`
- Create: `src/trading_os/portfolio/authority.py`
- Create: `src/trading_os/portfolio/normalizer.py`
- Create: `src/trading_os/portfolio/projector.py`
- Create: `tests/unit/portfolio/test_normalizer.py`
- Create: `tests/unit/portfolio/test_projector.py`

**Interfaces:**
- Consumes: broker observations, OS ledger fills/reservations and manual provenance records.
- Produces: `PositionBuckets`, `CashBuckets`, `PortfolioLine`, `AccountPortfolioProjection`,
  `ReconciliationConflict`, and deterministic merge rules.

- [ ] **Step 1: Write failing double-count and authority tests**

```python
from trading_os.portfolio.normalizer import merge_kite_holding_and_position


def test_zero_net_day_position_does_not_duplicate_delivery_holding() -> None:
    merged = merge_kite_holding_and_position(
        settled_available=7,
        unsettled=2,
        pledged=1,
        day_net=0,
        broker_saleable=7,
    )
    assert merged.total_owned == 10
    assert merged.saleable_before_local_reservations == 7


def test_manual_record_adds_provenance_not_quantity() -> None:
    merged = merge_kite_holding_and_position(
        settled_available=7,
        unsettled=2,
        pledged=1,
        day_net=0,
        broker_saleable=7,
        manual_quantity=10,
    )
    assert merged.total_owned == 10
    assert merged.provenance == "manual_matched_broker"
```

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run pytest tests/unit/portfolio/test_normalizer.py -v`

Expected: FAIL importing the portfolio normalizer.

- [ ] **Step 3: Implement non-overlapping buckets and conflict records**

```python
# src/trading_os/portfolio/models.py
from pydantic import BaseModel, Field

from trading_os.kernel.ids import AccountId, InstrumentId


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
        return max(0, self.broker_available_minor - self.os_reserved_minor - self.pending_debit_minor)


class ReconciliationConflict(BaseModel, frozen=True):
    account_id: AccountId
    field_name: str
    broker_value: str
    os_value: str
    fail_direction: str
```

- [ ] **Step 4: Implement explicit authority and broker-specific merge functions**

`authority.py` must enumerate which source is authoritative for custody, restrictions, broker order
state, OS intent/provenance, decision price and semantic classifications. `normalizer.py` must have
separate Kite and Alpaca functions; it must never apply generic summation to holdings and positions.
Manual imports match by account, canonical instrument, quantity, acquisition evidence and validity
range. Ambiguous matches create `ReconciliationConflict` and do not add quantity.

- [ ] **Step 5: Project account partitions and owner/global cuts**

`AccountPortfolioProjection` contains exactly one `account_id`. `OwnerPortfolioCut` contains an
ordered tuple of account projections and reporting-currency marks but exposes no combined buying
power, saleable quantity or order reservation. Add tests proving INR cash cannot fund an Alpaca order
and USD cash cannot fund a Kite order.

- [ ] **Step 6: Run property tests and commit**

Use Hypothesis to prove `saleable_now <= total_owned`, quantities never become negative, replay is
deterministic, and adding an external/manual provenance record never changes broker custody.

```python
from hypothesis import given, strategies as st

from trading_os.portfolio.models import PositionBuckets


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
```

Run: `uv run pytest tests/unit/portfolio -v && uv run mypy src/trading_os/portfolio`

Expected: all unit and property tests pass.

```bash
git add src/trading_os/portfolio tests/unit/portfolio
git commit -m "feat: project authority-aware current portfolios"
```

### Task 8: Seal portfolio snapshots, completeness vectors and the pre-trade analysis gate

**Files:**
- Create: `src/trading_os/portfolio/completeness.py`
- Create: `src/trading_os/portfolio/snapshot.py`
- Create: `src/trading_os/portfolio/analysis.py`
- Create: `src/trading_os/portfolio/gate.py`
- Create: `tests/unit/portfolio/test_completeness.py`
- Create: `tests/unit/portfolio/test_analysis_gate.py`

**Interfaces:**
- Consumes: account projections, ledger cut, validated-data snapshot, policy set and CAS version.
- Produces: `PortfolioCompletenessVector`, `AccountPortfolioSnapshot`, `CurrentPortfolioAnalysis`,
  `PortfolioRiskOverlaySet`, and `PortfolioGateDecision`.

- [ ] **Step 1: Write failing worst-state and external-position tests**

```python
from trading_os.portfolio.completeness import CompletenessState, PortfolioCompletenessVector
from trading_os.portfolio.gate import GateAction, decide_portfolio_gate


def test_missing_open_orders_blocks_new_exposure() -> None:
    vector = PortfolioCompletenessVector.complete().model_copy(
        update={"open_orders": CompletenessState.MISSING}
    )
    assert decide_portfolio_gate(vector).action is GateAction.BLOCK_NEW_EXPOSURE


def test_unknown_cost_history_does_not_hide_current_exposure() -> None:
    vector = PortfolioCompletenessVector.complete().model_copy(
        update={"provenance": CompletenessState.DEGRADED}
    )
    decision = decide_portfolio_gate(vector)
    assert decision.action is GateAction.ALLOW
    assert "partial performance history" in decision.warnings
```

- [ ] **Step 2: Run tests and confirm missing completeness contract**

Run: `uv run pytest tests/unit/portfolio/test_completeness.py tests/unit/portfolio/test_analysis_gate.py -v`

Expected: FAIL importing completeness modules.

- [ ] **Step 3: Implement orthogonal completeness and deterministic gate mapping**

```python
# src/trading_os/portfolio/completeness.py
from enum import StrEnum

from pydantic import BaseModel


class CompletenessState(StrEnum):
    COMPLETE = "complete"
    DEGRADED = "degraded"
    MISSING = "missing"
    STALE = "stale"
    CONFLICT = "conflict"


class PortfolioCompletenessVector(BaseModel, frozen=True):
    custody: CompletenessState
    cash: CompletenessState
    open_orders: CompletenessState
    protection_orders: CompletenessState
    identity: CompletenessState
    settlement: CompletenessState
    prices: CompletenessState
    fx: CompletenessState
    corporate_actions: CompletenessState
    provenance: CompletenessState
    policies: CompletenessState

    @classmethod
    def complete(cls) -> "PortfolioCompletenessVector":
        return cls(**{name: CompletenessState.COMPLETE for name in cls.model_fields})
```

`gate.py` maps missing/stale/conflicting custody, cash, open orders, identity, settlement, required
price/FX, corporate actions or policies to `BLOCK_NEW_EXPOSURE`; protection-order uncertainty maps
to `MANAGEMENT_ONLY`; provenance degradation warns but cannot erase current exposure.

- [ ] **Step 4: Seal snapshots and compute the V1 analysis**

`AccountPortfolioSnapshot` must bind broker observation IDs, ledger cut, validated-data snapshot ID,
policy release IDs, CAS version, build time and content hash. `CurrentPortfolioAnalysis` computes per
account and owner-cut gross exposure, symbol/issuer/sector/country/currency concentration, coarse
liquidity class, upcoming event flags, reserved cash, protection coverage and separately labelled
broker/OS/unknown P&L. Correlation/style factors may be `NOT_COMPUTED`; they may not be fabricated.

- [ ] **Step 5: Add the hard dependency test**

Build a candidate whose sector exposure appears safe without a manual holding and exceeds policy
with that holding. Assert the analysis emits a tighten-only `PortfolioRiskOverlaySet` and the later
sizer/risk seam receives the snapshot ID. Assert no function accepts a household aggregate as cash
or quantity.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest tests/unit/portfolio -v && make verify`

Expected: all portfolio tests pass and snapshot hashes are stable under replay.

```bash
git add src/trading_os/portfolio tests/unit/portfolio
git commit -m "feat: gate trades on current portfolio analysis"
```

---

## Day 4 — Market state, discovery and tradability

### Task 9: Build validated multi-clock market-data snapshots

**Files:**
- Create: `src/trading_os/market_data/models.py`
- Create: `src/trading_os/market_data/ports.py`
- Create: `src/trading_os/market_data/validator.py`
- Create: `src/trading_os/market_data/snapshot.py`
- Create: `src/trading_os/market_data/testing.py`
- Create: `tests/unit/market_data/test_snapshot.py`
- Create: `tests/unit/market_data/test_adjustments.py`

**Interfaces:**
- Consumes: broker/vendor bars, quotes, corporate actions, venue calendars and FX marks.
- Produces: `Bar`, `Quote`, `CorporateActionObservation`, `FxMark`, `ValidatedDataSnapshotId`,
  source freshness/entitlement receipts and raw/adjusted lineage.

- [ ] **Step 1: Write failing temporal and adjustment tests**

```python
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from trading_os.kernel.ids import InstrumentId
from trading_os.market_data.models import Bar
from trading_os.market_data.snapshot import build_validated_snapshot


def test_snapshot_rejects_bar_received_after_decision_cutoff() -> None:
    cutoff = datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    bar = Bar(
        instrument_id=InstrumentId("NSE:INE000000001"),
        timeframe="15m",
        start=cutoff - timedelta(minutes=15),
        end=cutoff,
        received_at=cutoff + timedelta(seconds=1),
        open=Decimal("100"), high=Decimal("102"), low=Decimal("99"),
        close=Decimal("101"), volume=Decimal("10000"),
        source_id="kite", entitlement="live", adjustment_set_id="raw",
    )
    result = build_validated_snapshot([bar], cutoff)
    assert result.rejected_count == 1
    assert result.bars == ()
```

- [ ] **Step 2: Run tests and verify failure**

Run: `uv run pytest tests/unit/market_data -v`

Expected: FAIL importing market-data models.

- [ ] **Step 3: Implement immutable bars, quotes and source lineage**

```python
# src/trading_os/market_data/models.py
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from trading_os.kernel.ids import InstrumentId


class Bar(BaseModel, frozen=True):
    instrument_id: InstrumentId
    timeframe: str
    start: datetime
    end: datetime
    received_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal = Field(ge=0)
    source_id: str
    entitlement: str
    adjustment_set_id: str


class Quote(BaseModel, frozen=True):
    instrument_id: InstrumentId
    observed_at: datetime
    received_at: datetime
    bid: Decimal | None
    ask: Decimal | None
    last: Decimal | None
    source_id: str
    entitlement: str
```

Add explicit `CorporateActionObservation` and `FxMark` models with publication, effective and
receipt times. Never overwrite raw bars with adjusted values; an adjustment set creates a new
derived series referencing raw IDs and the corporate-action evidence.

Create the deterministic test-bar builder used by discovery tests:

```python
# src/trading_os/market_data/testing.py
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from trading_os.kernel.ids import InstrumentId
from trading_os.market_data.models import Bar


def make_daily_bars(closes: list[Decimal], volumes: list[Decimal]) -> list[Bar]:
    if len(closes) != len(volumes):
        raise ValueError("closes and volumes must have the same length")
    start = datetime(2026, 7, 1, tzinfo=UTC)
    bars: list[Bar] = []
    previous = closes[0]
    for index, (close, volume) in enumerate(zip(closes, volumes, strict=True)):
        day = start + timedelta(days=index)
        bars.append(
            Bar(
                instrument_id=InstrumentId("BSE:INE000000001"),
                timeframe="1d",
                start=day,
                end=day + timedelta(days=1),
                received_at=day + timedelta(days=1, seconds=1),
                open=previous,
                high=max(previous, close),
                low=min(previous, close),
                close=close,
                volume=volume,
                source_id="fixture",
                entitlement="test",
                adjustment_set_id="raw",
            )
        )
        previous = close
    return bars
```

- [ ] **Step 4: Implement cutoff validation and content-addressed snapshots**

`build_validated_snapshot()` sorts accepted records by canonical identity, rejects receipt times
after the cutoff, verifies OHLC consistency and entitlement, records missing instruments/timeframes,
and hashes a canonical JSON manifest. Add `MarketDataPort` methods for historical bars, quotes and
stream subscriptions; implement an offline fixture port now.

- [ ] **Step 5: Prove multi-clock behavior**

Add tests for daily/hourly/15-minute discovery bars, 1-minute/5-minute shortlist bars, DST/holiday
calendar edges, duplicate bars, late corrections, missing SIP entitlement and stale FX. Assert an
IEX-only US record cannot claim SIP/whole-market coverage.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest tests/unit/market_data -v && uv run mypy src/trading_os/market_data`

Expected: all temporal, adjustment and entitlement tests pass.

```bash
git add src/trading_os/market_data tests/unit/market_data
git commit -m "feat: seal validated multi-clock market snapshots"
```

### Task 10: Implement broad discovery, CoverageReceipts and account tradability packets

**Files:**
- Create: `src/trading_os/discovery/models.py`
- Create: `src/trading_os/discovery/registry.py`
- Create: `src/trading_os/discovery/momentum.py`
- Create: `src/trading_os/tradability/models.py`
- Create: `src/trading_os/tradability/builder.py`
- Create: `tests/unit/discovery/test_momentum.py`
- Create: `tests/unit/discovery/test_coverage.py`
- Create: `tests/unit/tradability/test_builder.py`

**Interfaces:**
- Consumes: validated bars/quotes, broad discovery universe, account/broker/compliance state.
- Produces: `OpportunityCandidate`, `CoverageReceipt`, `TradabilityRiskPacket`, and a strict
  account-specific tradable allowlist.

- [ ] **Step 1: Write the Cropster-like discovery test**

```python
from decimal import Decimal

from trading_os.discovery.momentum import MomentumDetectorPolicy, MomentumOpportunityDetector
from trading_os.kernel.ids import SnapshotId
from trading_os.market_data.testing import make_daily_bars


def test_detector_finds_accelerating_price_and_volume_without_auto_buying() -> None:
    bars = make_daily_bars(
        closes=[Decimal(str(value)) for value in [80, 82, 84, 88, 94, 103, 115]],
        volumes=[Decimal(str(value)) for value in [10, 11, 12, 15, 22, 35, 58]],
    )
    detector = MomentumOpportunityDetector(
        MomentumDetectorPolicy(
            release_id="momentum-v1",
            return_lookback=5,
            minimum_return=Decimal("0.15"),
            volume_lookback=5,
            minimum_volume_ratio=Decimal("2"),
        )
    )
    candidates = detector.detect(bars, SnapshotId("data-1"))
    assert len(candidates) == 1
    assert candidates[0].setup == "momentum_acceleration"
    assert not hasattr(candidates[0], "quantity")
    assert not hasattr(candidates[0], "order")
```

- [ ] **Step 2: Run discovery tests and verify failure**

Run: `uv run pytest tests/unit/discovery tests/unit/tradability -v`

Expected: FAIL importing discovery modules.

- [ ] **Step 3: Implement candidates, detector registry and coverage**

```python
# src/trading_os/discovery/models.py
from datetime import datetime

from pydantic import BaseModel

from trading_os.kernel.ids import InstrumentId, SnapshotId


class OpportunityCandidate(BaseModel, frozen=True):
    candidate_id: str
    instrument_id: InstrumentId
    setup: str
    horizon: str
    direction: str
    detected_at: datetime
    data_snapshot_id: SnapshotId
    detector_release_id: str


class CoverageReceipt(BaseModel, frozen=True):
    receipt_id: str
    intended_instruments: tuple[InstrumentId, ...]
    scanned_instruments: tuple[InstrumentId, ...]
    omitted: dict[InstrumentId, str]
    started_at: datetime
    completed_at: datetime
    data_snapshot_id: SnapshotId
    detector_release_ids: tuple[str, ...]
```

`OpportunityDetectorRegistry.run()` executes registered deterministic detectors and emits one
receipt even when some instruments fail. The initial detector uses multi-timeframe relative
strength, breakout distance, volume acceleration, ATR-normalized movement and regime filters; its
thresholds come from a versioned detector policy rather than code constants.

```python
# src/trading_os/discovery/momentum.py
from decimal import Decimal
from hashlib import sha256

from pydantic import BaseModel, Field

from trading_os.discovery.models import OpportunityCandidate
from trading_os.kernel.ids import SnapshotId
from trading_os.market_data.models import Bar


class MomentumDetectorPolicy(BaseModel, frozen=True):
    release_id: str
    return_lookback: int = Field(ge=2)
    minimum_return: Decimal
    volume_lookback: int = Field(ge=2)
    minimum_volume_ratio: Decimal = Field(gt=0)


class MomentumOpportunityDetector:
    def __init__(self, policy: MomentumDetectorPolicy) -> None:
        self._policy = policy

    def detect(
        self,
        bars: list[Bar],
        snapshot_id: SnapshotId,
    ) -> list[OpportunityCandidate]:
        required = max(self._policy.return_lookback, self._policy.volume_lookback) + 2
        if len(bars) < required:
            return []
        recent_return = (
            bars[-1].close / bars[-self._policy.return_lookback].close - Decimal("1")
        )
        volume_window = bars[-(self._policy.volume_lookback + 2):-2]
        baseline_volume = sum(bar.volume for bar in volume_window) / Decimal(len(volume_window))
        volume_ratio = bars[-1].volume / baseline_volume if baseline_volume > 0 else Decimal("0")
        if (
            recent_return < self._policy.minimum_return
            or volume_ratio < self._policy.minimum_volume_ratio
        ):
            return []
        candidate_key = ":".join(
            (
                str(bars[-1].instrument_id),
                str(snapshot_id),
                self._policy.release_id,
                "momentum_acceleration",
            )
        )
        return [
            OpportunityCandidate(
                candidate_id=sha256(candidate_key.encode()).hexdigest(),
                instrument_id=bars[-1].instrument_id,
                setup="momentum_acceleration",
                horizon="swing",
                direction="long",
                detected_at=bars[-1].received_at,
                data_snapshot_id=snapshot_id,
                detector_release_id=self._policy.release_id,
            )
        ]
```

- [ ] **Step 4: Build strict account-specific tradability packets**

`TradabilityRiskPacket` must carry account, broker, instrument/listing, orderability, listing status,
circuits/bands, surveillance/restrictions, spread/depth/turnover, raw/adjusted lineage, stop
feasibility, account restrictions, data freshness, compliance release and `eligible` plus closed
reason codes. A candidate is never added to the tradable allowlist without a complete packet.

```python
# src/trading_os/tradability/models.py
from datetime import datetime

from pydantic import BaseModel

from trading_os.kernel.ids import AccountId, InstrumentId, SnapshotId


class TradabilityRiskPacket(BaseModel, frozen=True):
    packet_id: str
    account_id: AccountId
    instrument_id: InstrumentId
    broker: str
    listing_active: bool
    broker_orderable: bool
    surveillance_flags: tuple[str, ...]
    circuit_or_band_state: str
    liquidity_state: str
    stop_feasible: bool
    raw_adjusted_lineage_valid: bool
    account_restrictions: tuple[str, ...]
    data_snapshot_id: SnapshotId
    data_fresh_at: datetime
    compliance_release_id: str
    eligible: bool
    reason_codes: tuple[str, ...]
```

- [ ] **Step 5: Add adversarial coverage tests**

Test a BSE-only candidate outside NIFTY 500, an illiquid upper-circuit name, stale bars, a missing
instrument mapping, Alpaca IEX-only breadth, a halted asset and a packet whose stop cannot be placed.
Assert discovery can still record the candidate while tradability blocks execution.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest tests/unit/discovery tests/unit/tradability -v && make verify`

Expected: discovery and tradability tests pass; candidates contain no executable fields.

```bash
git add src/trading_os/discovery src/trading_os/tradability tests/unit/discovery tests/unit/tradability
git commit -m "feat: discover and gate broad-universe opportunities"
```

---

## Day 5 — Evidence, agents and ontology kernel

### Task 11: Build typed multi-domain evidence with a permanent relational champion

**Files:**
- Create: `src/trading_os/research/models.py`
- Create: `src/trading_os/research/ports.py`
- Create: `src/trading_os/research/watchers.py`
- Create: `src/trading_os/research/orchestrator.py`
- Create: `src/trading_os/ontology/releases.py`
- Create: `src/trading_os/ontology/relational.py`
- Create: `src/trading_os/ontology/projections.py`
- Create: `ontology/core.ttl`
- Create: `ontology/shapes/core.shacl.ttl`
- Create: `tests/unit/research/test_evidence_boundary.py`
- Create: `tests/unit/ontology/test_release.py`
- Create: `tests/integration/ontology/test_relational_fallback.py`

**Interfaces:**
- Consumes: candidate, tradability packet, source records, current portfolio analysis and semantic
  release manifests.
- Produces: domain `EvidencePacket`s, `InstrumentBeliefState`, `DecisionFeatureSet`,
  `RiskOverlaySet`, `OntologyRelease`, `SemanticSnapshot`, projection receipts and relational
  competency-query answers.

- [ ] **Step 1: Write the non-executable schema test**

```python
from datetime import UTC, datetime

from trading_os.kernel.ids import InstrumentId, SnapshotId
from trading_os.research.models import DecisionFeatureSet, EvidenceDomain, EvidencePacket


def test_research_models_have_no_executable_fields() -> None:
    forbidden = {"quantity", "price", "target_weight", "target_position", "order", "broker"}
    for model in (EvidencePacket, DecisionFeatureSet):
        assert forbidden.isdisjoint(model.model_fields)


def test_sentiment_is_risk_only_without_primary_corroboration() -> None:
    now = datetime.now(UTC)
    packet = EvidencePacket(
        packet_id="sentiment-1",
        instrument_id=InstrumentId("NSE:INE000000001"),
        domain=EvidenceDomain.SENTIMENT,
        assessment="attention_accelerating_unverified",
        support=("source-1",),
        contradictions=(),
        missing=("primary_corroboration",),
        as_of=now,
        cutoff=now,
        data_snapshot_id=SnapshotId("data-1"),
        source_record_ids=("source-1",),
        eligibility_effect="risk_only",
    )
    assert packet.eligibility_effect == "risk_only"
```

- [ ] **Step 2: Run research and ontology tests and verify failure**

Run: `uv run pytest tests/unit/research tests/unit/ontology tests/integration/ontology -v`

Expected: FAIL importing research and ontology modules.

- [ ] **Step 3: Implement closed evidence-domain packets**

```python
# src/trading_os/research/models.py
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from trading_os.kernel.ids import InstrumentId, SnapshotId


class EvidenceDomain(StrEnum):
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    CORPORATE_EVENT = "corporate_event"
    SENTIMENT = "sentiment"
    MACRO = "macro"
    ECONOMIC_RELATIONSHIP = "economic_relationship"
    GOVERNANCE = "governance"
    LIQUIDITY = "liquidity"
    PORTFOLIO = "portfolio"
    MARKET_MECHANICS = "market_mechanics"


class EvidencePacket(BaseModel, frozen=True):
    packet_id: str
    instrument_id: InstrumentId
    domain: EvidenceDomain
    assessment: str
    support: tuple[str, ...]
    contradictions: tuple[str, ...]
    missing: tuple[str, ...]
    as_of: datetime
    cutoff: datetime
    data_snapshot_id: SnapshotId
    source_record_ids: tuple[str, ...]
    eligibility_effect: str


class DecisionFeatureSet(BaseModel, frozen=True):
    feature_set_id: str
    instrument_id: InstrumentId
    categorical_features: dict[str, str]
    evidence_packet_ids: tuple[str, ...]
    semantic_snapshot_id: str | None
    activation_release_id: str | None
```

Create separate `RiskOverlaySet` fields limited to multipliers in `(0, 1]` and veto reason codes.
No free-form agent result crosses this boundary.

- [ ] **Step 4: Implement source watchers and the agent orchestration port**

Add deterministic NSE/BSE and SEC filing watcher interfaces that capture immutable source records
with publication and receipt times. `ResearchAgentPort` accepts a bounded research question plus
source record IDs and returns a candidate `EvidencePacket`; admission validates citations, cutoff,
closed enums and prompt-injection isolation. Use a deterministic fake agent in tests and make LLM
failure produce an explicit missing packet rather than block relational operation.

- [ ] **Step 5: Publish and validate the ontology kernel**

`core.ttl` and SHACL shapes cover LegalParty, Issuer, Security, Listing, SourceRecord, Observation,
Claim, WorldEvent, EvidencePacket, BrokerageAccount, PortfolioSnapshot and provenance/time fields.
`OntologyReleaseBuilder` hashes Git-owned Turtle/SHACL, runs pySHACL, and emits an immutable release.
Term IRIs stay release-independent; the release gets a version IRI.

- [ ] **Step 6: Implement relational champion and rebuildable projection receipts**

Relational competency queries answer candidate evidence, contradictions, freshness, tradability and
portfolio context from snapshot-scoped Postgres rows. Fuseki and Neo4j projection ports rebuild from
one manifest and emit hashes; application credentials cannot write arbitrary graph data. If either
graph is unavailable or disagrees, decisioning uses the relational answer and records degradation.

- [ ] **Step 7: Verify and commit**

Run: `uv run pytest tests/unit/research tests/unit/ontology tests/integration/ontology -v && make verify`

Expected: ontology validates; the relational fallback passes with Fuseki and Neo4j stopped; no
research model exposes executable fields.

```bash
git add src/trading_os/research src/trading_os/ontology ontology tests/unit/research tests/unit/ontology tests/integration/ontology
git commit -m "feat: add typed evidence and ontology baseline"
```

---

## Day 6 — Deterministic decisioning and compliance

### Task 12: Implement provisional sizing, portfolio risk and CAS reservations

**Files:**
- Create: `src/trading_os/decision/models.py`
- Create: `src/trading_os/decision/eligibility.py`
- Create: `src/trading_os/decision/sizing.py`
- Create: `src/trading_os/decision/risk.py`
- Create: `src/trading_os/execution/reservations.py`
- Create: `tests/unit/decision/test_sizing.py`
- Create: `tests/unit/decision/test_risk.py`
- Create: `tests/integration/execution/test_reservations.py`

**Interfaces:**
- Consumes: candidate, tradability, `DecisionFeatureSet`, fresh portfolio snapshot, price/stop,
  capital/exposure policies and tighten-only overlays.
- Produces: `ProvisionalSize`, `RiskDecision`, final allowed quantity and versioned
  `OrderReservation`.

- [ ] **Step 1: Write the conviction-blind sizing test**

```python
from trading_os.decision.sizing import SizingInput, size_cash_equity


def test_agent_conviction_cannot_change_quantity() -> None:
    base = SizingInput(
        available_cash_minor=1_250_000,
        capital_minor=5_000_000,
        risk_fraction_ppm=10_000,
        entry_price_minor=100_000,
        stop_price_minor=95_000,
        max_symbol_minor=500_000,
        lot_size=1,
    )
    assert size_cash_equity(base).quantity == 5
    assert "conviction" not in SizingInput.model_fields
```

- [ ] **Step 2: Run decision tests and verify failure**

Run: `uv run pytest tests/unit/decision tests/integration/execution/test_reservations.py -v`

Expected: FAIL importing decision models.

- [ ] **Step 3: Implement fixed-point provisional sizing**

```python
# src/trading_os/decision/sizing.py
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
```

- [ ] **Step 4: Apply post-trade risk and overlays after provisional sizing**

`RiskEngine.evaluate()` builds the hypothetical account and owner cut, applies symbol/issuer/sector/
country/currency, deployment and loss limits, then applies only multipliers `<= 1` or vetoes from
`RiskOverlaySet`. It returns the shrunken quantity plus reason codes and all snapshot/release IDs.
Add a test proving an external holding can shrink a candidate and an overlay can never increase it.

- [ ] **Step 5: Add CAS reservations**

Persist `OrderReservation` with account, snapshot CAS version, policy IDs, cash, quantity, risk,
expiry and status. Two concurrent reservations against the same version must allow at most one to
commit. Reservation release/expiry appends events and is idempotent.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest tests/unit/decision tests/integration/execution/test_reservations.py -v && make verify`

Expected: sizing order, overlay monotonicity and concurrency tests pass.

```bash
git add src/trading_os/decision src/trading_os/execution/reservations.py tests/unit/decision tests/integration/execution
git commit -m "feat: size and reserve deterministic trades"
```

### Task 13: Implement versioned India and US compliance gates

**Files:**
- Create: `src/trading_os/decision/compliance.py`
- Create: `src/trading_os/policy/compliance.py`
- Create: `tests/unit/decision/test_india_compliance.py`
- Create: `tests/unit/decision/test_us_compliance.py`
- Create: `tests/unit/policy/test_compliance_release.py`

**Interfaces:**
- Consumes: provisional order, account/broker state, effective compliance release, market session,
  settled cash, account flags and current order-rate state.
- Produces: `ComplianceDecision` with `ALLOW`, `SHRINK`, `VETO` or `REDUCE_ONLY` and closed reasons.

- [ ] **Step 1: Write failing venue-specific compliance tests**

```python
from trading_os.brokers.models import OrderType
from trading_os.decision.compliance import IndiaComplianceInput, evaluate_india


def test_india_algo_market_order_is_not_constructible() -> None:
    assert set(OrderType) == {OrderType.LIMIT, OrderType.STOP_LIMIT}


def test_unregistered_static_ip_vetoes_new_india_exposure() -> None:
    decision = evaluate_india(
        IndiaComplianceInput(
            static_ip_ready=False,
            algorithm_tag_ready=True,
            settled_cash_sufficient=True,
            order_rate_last_second=0,
            max_orders_per_second=10,
            instrument_allowed=True,
        )
    )
    assert decision.outcome == "veto"
    assert decision.reason == "static_ip_not_ready"
```

- [ ] **Step 2: Run compliance tests and verify failure**

Run: `uv run pytest tests/unit/decision/test_india_compliance.py tests/unit/decision/test_us_compliance.py -v`

Expected: FAIL importing compliance modules.

- [ ] **Step 3: Implement effective-dated compliance profiles**

`ComplianceProfileRelease` carries jurisdiction, broker, account/product scope, source URLs, reviewed
time, review expiry, static-IP requirement, allowed order types, order-rate ceiling, required tags,
cash/settlement rules and closed prohibitions. An expired or missing profile blocks new exposure.

- [ ] **Step 4: Implement India rules as data plus deterministic evaluation**

Check account identity, cash-only/long-only, settled cash, tradable allowlist, exchange/segment,
static-IP readiness, required algorithm tag, effective order type and order-rate ceiling. Use a
token-bucket projection whose state is scoped per account/exchange/segment and fail closed if its
state cannot be read.

- [ ] **Step 5: Implement US account-state rules**

Read Alpaca `trading_blocked`, `account_blocked`, `trade_suspended_by_user`, buying power, asset
tradability/fractionability, data entitlement and broker day-trade/PDT protection state. The $200
sleeve never assumes unrestricted same-day round trips. Model LRS/idle-FX records separately from
trade P&L and never let repatriation reset the fiscal-year remittance meter.

- [ ] **Step 6: Add policy-change and stale-profile tests**

Create a Day-10 compliance supersession, assert old decisions retain the previous release ID, and
assert a stale rule source blocks new exposure without cancelling existing protection.

- [ ] **Step 7: Verify and commit**

Run: `uv run pytest tests/unit/decision/test_*compliance.py tests/unit/policy/test_compliance_release.py -v && make verify`

Expected: India and US compliance suites pass.

```bash
git add src/trading_os/decision/compliance.py src/trading_os/policy/compliance.py tests/unit/decision tests/unit/policy/test_compliance_release.py
git commit -m "feat: enforce versioned India and US compliance"
```

---

## Day 7 — Protected execution and live broker writes

### Task 14: Implement durable intents, kill states and protection supervision

**Files:**
- Create: `src/trading_os/execution/models.py`
- Create: `src/trading_os/execution/kill_state.py`
- Create: `src/trading_os/execution/coordinator.py`
- Create: `src/trading_os/execution/protection.py`
- Create: `tests/unit/execution/test_kill_state.py`
- Create: `tests/integration/execution/test_coordinator.py`
- Create: `tests/integration/execution/test_protection.py`

**Interfaces:**
- Consumes: reservation, final decision, broker port, latest snapshot/policies, account capability
  assignment and kill generation.
- Produces: durable `OrderIntent`, broker acknowledgement/fill events, `ProtectionCoverage`, and
  `ACTIVE`, `ENTRY_DISABLED`, `REDUCE_ONLY`, `MANAGEMENT_ONLY`, `HALTED` account states.

- [ ] **Step 1: Write failing crash-window and stop-order tests**

```python
from trading_os.execution.kill_state import KillMode, KillState, transition


def test_safety_fault_fences_entries_before_human_acknowledgement() -> None:
    state = KillState.active(account_id="acct-1", generation=1)
    stopped = transition(state, "critical_portfolio_stale")
    assert stopped.mode is KillMode.ENTRY_DISABLED
    assert stopped.generation == 2


def test_entry_disabled_keeps_reconciliation_enabled() -> None:
    state = KillState(account_id="acct-1", generation=2, mode=KillMode.ENTRY_DISABLED)
    assert state.may_increase_exposure is False
    assert state.may_reconcile is True
```

Add an integration test that appends an order intent, simulates a crash before broker
acknowledgement, restarts, queries by client order ID and does not submit a duplicate.

- [ ] **Step 2: Run execution tests and verify failure**

Run: `uv run pytest tests/unit/execution tests/integration/execution -v`

Expected: FAIL importing execution models.

- [ ] **Step 3: Implement kill states with monotonic generations**

```python
# src/trading_os/execution/kill_state.py
from enum import StrEnum

from pydantic import BaseModel


class KillMode(StrEnum):
    ACTIVE = "active"
    ENTRY_DISABLED = "entry_disabled"
    REDUCE_ONLY = "reduce_only"
    MANAGEMENT_ONLY = "management_only"
    HALTED = "halted"


class KillState(BaseModel, frozen=True):
    account_id: str
    generation: int
    mode: KillMode

    @classmethod
    def active(cls, account_id: str, generation: int) -> "KillState":
        return cls(account_id=account_id, generation=generation, mode=KillMode.ACTIVE)

    @property
    def may_increase_exposure(self) -> bool:
        return self.mode is KillMode.ACTIVE

    @property
    def may_reconcile(self) -> bool:
        return True


def transition(state: KillState, reason: str) -> KillState:
    safety_reasons = {"critical_portfolio_stale", "reconciliation_conflict", "protection_failed"}
    mode = KillMode.ENTRY_DISABLED if reason in safety_reasons else KillMode.HALTED
    return state.model_copy(update={"generation": state.generation + 1, "mode": mode})
```

- [ ] **Step 4: Implement the durable execution coordinator**

The coordinator performs, in order: reload portfolio and policy IDs; verify reservation CAS;
verify kill generation and account capability; append `OrderIntentCreated`; submit with that intent
ID as `client_order_id`; append acknowledgement or explicit unknown-effect event; install protection
after fill; reconcile before any retry. Amend/cancel/replace paths re-run capability, compliance and
kill checks.

- [ ] **Step 5: Implement protection coverage as a state machine**

States are `UNREQUIRED`, `PENDING_FILL`, `PENDING_PROTECTION`, `PROTECTED`, `DEGRADED`, `FAILED`,
`CLOSED`. A fill is not accepted as fully managed until broker-native stop/stop-limit or approved
equivalent protection is observed and reconciled. Protection failure immediately fences entries,
alerts the owner and enters `MANAGEMENT_ONLY`; it never submits a guessed close quantity when
custody is stale.

- [ ] **Step 6: Prove crash recovery and commit**

Test crashes before/after intent append, broker acknowledgement, fill and protection placement;
duplicate callbacks; partial fills; rejected protection; stale-worker generation; and broker
unavailability during an emergency stop.

Run: `uv run pytest tests/unit/execution tests/integration/execution -v && make verify`

Expected: every crash replay converges without duplicate economic effect.

```bash
git add src/trading_os/execution tests/unit/execution tests/integration/execution
git commit -m "feat: coordinate crash-safe protected execution"
```

### Task 15: Enable live Kite and Alpaca writes behind account capability receipts

**Files:**
- Modify: `src/trading_os/brokers/kite.py`
- Modify: `src/trading_os/brokers/alpaca.py`
- Create: `src/trading_os/policy/capability.py`
- Create: `tests/contract/brokers/test_kite_write_contract.py`
- Create: `tests/contract/brokers/test_alpaca_write_contract.py`
- Create: `tests/unit/policy/test_capability_intersection.py`

**Interfaces:**
- Consumes: normalized `OrderRequest`, live endpoint clients, effective capability/account
  assignment, compliance, entitlement, readiness, kill generation and optional semantic activation.
- Produces: real broker calls only when `ExecutionAuthority.evaluate()` returns `ALLOW`.

- [ ] **Step 1: Write the deny-by-default authority test**

```python
from trading_os.policy.capability import ExecutionAuthority, ExecutionContext


def make_context(*, uses_semantic_features: bool) -> ExecutionContext:
    return ExecutionContext(
        capability_release_id="cash-equity-in-us-1",
        account_assignment="assignment-1",
        mandate_active=True,
        compliance_effective=True,
        entitlement_ready=True,
        broker_ready=True,
        portfolio_reconciled=True,
        kill_generation_matches=True,
        uses_semantic_features=uses_semantic_features,
        semantic_activation=None,
    )


def test_missing_account_capability_denies_live_write() -> None:
    context = make_context(uses_semantic_features=False).model_copy(
        update={"account_assignment": None}
    )
    decision = ExecutionAuthority().evaluate(context)
    assert decision.allowed is False
    assert decision.reason == "account_capability_missing"


def test_semantic_activation_is_required_only_when_semantic_features_are_used() -> None:
    baseline = make_context(uses_semantic_features=False)
    semantic = make_context(uses_semantic_features=True)
    assert ExecutionAuthority().evaluate(baseline).allowed is True
    assert ExecutionAuthority().evaluate(semantic).allowed is False
```

- [ ] **Step 2: Run authority and broker write tests and verify failure**

Run: `uv run pytest tests/unit/policy/test_capability_intersection.py tests/contract/brokers/test_*write_contract.py -v`

Expected: FAIL importing capability evaluation.

- [ ] **Step 3: Implement independent AND-gates**

`AssetClassCapabilityRelease` is reusable and names jurisdiction/residency context, product, venue/
segment, broker, data, valuation, risk, execution, protection and reconciliation requirements.
`AccountCapabilityAssignment` binds account, mandate, effective interval, product scope and capital
policy. `ExecutionAuthority` intersects those with compliance, entitlement, broker readiness,
fresh reconciled state, current kill generation and `DecisionFeatureActivation` only when semantic
features are present. There is no permission-bearing default.

```python
# src/trading_os/policy/capability.py
from pydantic import BaseModel


class ExecutionContext(BaseModel, frozen=True):
    capability_release_id: str | None
    account_assignment: str | None
    mandate_active: bool
    compliance_effective: bool
    entitlement_ready: bool
    broker_ready: bool
    portfolio_reconciled: bool
    kill_generation_matches: bool
    uses_semantic_features: bool
    semantic_activation: str | None


class AuthorityDecision(BaseModel, frozen=True):
    allowed: bool
    reason: str


class ExecutionAuthority:
    def evaluate(self, context: ExecutionContext) -> AuthorityDecision:
        checks = (
            (context.capability_release_id is not None, "capability_release_missing"),
            (context.account_assignment is not None, "account_capability_missing"),
            (context.mandate_active, "mandate_inactive"),
            (context.compliance_effective, "compliance_inactive"),
            (context.entitlement_ready, "data_entitlement_not_ready"),
            (context.broker_ready, "broker_not_ready"),
            (context.portfolio_reconciled, "portfolio_not_reconciled"),
            (context.kill_generation_matches, "kill_generation_stale"),
            (
                not context.uses_semantic_features or context.semantic_activation is not None,
                "semantic_activation_missing",
            ),
        )
        for passed, reason in checks:
            if not passed:
                return AuthorityDecision(allowed=False, reason=reason)
        return AuthorityDecision(allowed=True, reason="all_authorities_effective")
```

- [ ] **Step 4: Implement Kite limit and stop-limit writes**

Map canonical listing identity to current Kite `exchange` and `tradingsymbol`; submit CNC limit
orders with the durable client tag and effective algorithm identifier. Protection uses the
currently supported broker-native stop/GTT mechanism selected by policy. Reject market orders,
missing static-IP readiness, unmapped instruments and quantities outside broker lot rules before
SDK invocation. `cancel_order()` is idempotent after observing final broker status.

- [ ] **Step 5: Implement Alpaca limit and protected writes**

Use alpaca-py `TradingClient` with `paper=False` only when the account capability and
`LiveAuthorityReceipt` are effective. Submit limit orders with `client_order_id`; install the
policy-selected stop/stop-limit or bracket protection. Read account flags and asset fractionability
at revalidation time. Never switch from paper to live by URL/config alone.

- [ ] **Step 6: Run contract suites without live credentials**

Inject recording SDK fakes and assert exact broker payloads, client IDs, order types, product,
protection requests, error mapping and duplicate handling. The tests must fail if the SDK method is
called before authority evaluation.

- [ ] **Step 7: Verify and commit**

Run: `uv run pytest tests/contract/brokers tests/unit/policy/test_capability_intersection.py -v && make verify`

Expected: normalized broker contract and authority-intersection suites pass offline.

```bash
git add src/trading_os/brokers src/trading_os/policy/capability.py tests/contract/brokers tests/unit/policy/test_capability_intersection.py
git commit -m "feat: gate live broker writes by capability"
```

---

## Day 8 — Reconciliation, retrospective and operator console

### Task 16: Reconcile custody and build the governed retrospective loop

**Files:**
- Create: `src/trading_os/execution/reconciliation.py`
- Create: `src/trading_os/retrospective/models.py`
- Create: `src/trading_os/retrospective/linker.py`
- Create: `src/trading_os/retrospective/diagnosis.py`
- Create: `tests/integration/execution/test_reconciliation.py`
- Create: `tests/unit/retrospective/test_linker.py`
- Create: `tests/unit/retrospective/test_diagnosis.py`

**Interfaces:**
- Consumes: broker observations, event ledger, portfolio snapshots, decisions, costs, fills,
  protection and outcomes.
- Produces: typed reconciliation differences, `DecisionOutcomeRecord`, closed diagnosis and
  non-executable improvement proposals.

- [ ] **Step 1: Write failing divergence and attribution tests**

```python
from trading_os.execution.reconciliation import DifferenceClass, reconcile_quantity


def test_unexplained_broker_quantity_blocks_new_exposure() -> None:
    difference = reconcile_quantity(broker_quantity=12, os_expected_quantity=10)
    assert difference.kind is DifferenceClass.UNEXPLAINED_CUSTODY
    assert difference.fail_direction == "entry_disabled"
```

Add a retrospective test that links coverage, evidence, portfolio snapshot, sizing, risk,
compliance, order, fill, protection, fees and realized outcome without rewriting any source event.

- [ ] **Step 2: Run reconciliation and retrospective tests and verify failure**

Run: `uv run pytest tests/integration/execution/test_reconciliation.py tests/unit/retrospective -v`

Expected: FAIL importing reconciliation/retrospective modules.

- [ ] **Step 3: Implement typed reconciliation by field authority**

Reconcile account identity; holdings/positions buckets; open/protection orders; cash; fills and
fees; OS reservations; broker account flags; and policy/kill generations. Difference classes have
deterministic fail directions: explained timing, expected external/manual, stale observation,
unknown effect, unexplained custody, cash conflict, missing order, protection conflict and identity
conflict. Append observations and outcomes; never patch ledger history.

- [ ] **Step 4: Link decisions to outcomes and costs**

`DecisionOutcomeRecord` binds candidate, CoverageReceipt, TradabilityRiskPacket, EvidencePackets,
DecisionFeatureSet, portfolio/data/semantic snapshots, policy releases, provisional/final quantity,
orders/fills/protection, fees/taxes, exit and evaluation horizon. It retains broker-reported,
OS-ledger and unknown/partial P&L labels.

- [ ] **Step 5: Implement closed diagnosis and proposal boundaries**

Root causes are `DISCOVERY_COVERAGE`, `IDENTITY`, `TEMPORAL`, `DATA_QUALITY`, `EXTRACTION`,
`ONTOLOGY_QUERY`, `PORTFOLIO_NORMALIZATION`, `RISK`, `COMPLIANCE`, `EXECUTION`, `PROTECTION`,
`COST`, and `REGIME_SHIFT`. Proposals may name a detector, query, ontology, strategy or policy
release candidate but cannot activate it. Always compare the relational baseline before blaming a
semantic challenger.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest tests/integration/execution/test_reconciliation.py tests/unit/retrospective -v && make verify`

Expected: injected differences produce the documented entry fence or degradation and all outcomes
remain replayable.

```bash
git add src/trading_os/execution/reconciliation.py src/trading_os/retrospective tests/integration/execution/test_reconciliation.py tests/unit/retrospective
git commit -m "feat: reconcile and diagnose trading outcomes"
```

### Task 17: Compose scheduling, API and the non-technical operator console

**Files:**
- Create: `src/trading_os/app/container.py`
- Create: `src/trading_os/app/scheduler.py`
- Create: `src/trading_os/app/api.py`
- Create: `src/trading_os/app/cli.py`
- Create: `web/package.json`
- Create: `web/src/App.tsx`
- Create: `web/src/api.ts`
- Create: `web/src/components/Portfolio.tsx`
- Create: `web/src/components/Candidates.tsx`
- Create: `web/src/components/DecisionTrace.tsx`
- Create: `web/src/components/RiskControls.tsx`
- Create: `web/src/components/PriceChart.tsx`
- Create: `web/src/components/Retrospectives.tsx`
- Create: `tests/integration/app/conftest.py`
- Create: `tests/integration/app/test_cycle.py`
- Create: `web/src/App.test.tsx`
- Create: `web/e2e/operator.spec.ts`

**Interfaces:**
- Consumes: all application services from Tasks 1–16.
- Produces: idempotent multi-clock cycles, read-only operational APIs, explicit policy activation
  endpoints, CLI readiness commands and an understandable web console.

- [ ] **Step 1: Write the failing idempotent-cycle test**

```python
async def test_same_cycle_key_has_one_economic_effect(app) -> None:
    first = await app.run_cycle(account_id="acct-1", cycle_key="2026-07-22T10:00:00Z")
    second = await app.run_cycle(account_id="acct-1", cycle_key="2026-07-22T10:00:00Z")
    assert first.cycle_id == second.cycle_id
    assert first.order_intent_ids == second.order_intent_ids
```

- [ ] **Step 2: Run backend and frontend tests and verify failure**

Run: `uv run pytest tests/integration/app/test_cycle.py -v && npm --prefix web test -- --run`

Expected: FAIL because application wiring and web package do not exist.

- [ ] **Step 3: Wire one idempotent application cycle**

For each enabled account: observe broker; reconcile/project; seal portfolio and market snapshots;
run discovery; build tradability and evidence; generate deterministic features; size; risk/compliance;
reserve; revalidate; execute only with live authority; protect; reconcile; append outcome context.
Cycle keys are unique by account, decision window and policy release set.

`tests/integration/app/conftest.py` builds the application with Postgres, fake Kite/Alpaca brokers,
fixture market data, a deterministic research agent, fixed UTC clock and live writes disabled. The
fixture must expose both account IDs so the test proves partitioned orchestration.

- [ ] **Step 4: Add multi-clock scheduling without creating an intraday mandate**

APScheduler jobs trigger daily/hourly/15-minute broad scans, 1-minute/5-minute shortlist refresh,
configured decision windows, second-level protection/reconciliation checks and filing/event watcher
polls. Decision-window policy is checked again inside the cycle, so a scheduler misfire cannot trade.

- [ ] **Step 5: Expose safe APIs and CLI commands**

Provide endpoints for account/owner portfolio analysis, coverage, candidates, tradability, evidence,
decision trace, orders/protection, reconciliation, retrospective, effective policy releases and
kill state. Mutating endpoints are limited to owner-authenticated policy release activation,
entry-disable/reduce/halt and restart receipts; no endpoint accepts natural-language orders.

CLI commands: `readiness`, `observe`, `reconcile`, `replay`, `run-cycle --dry-effect`,
`activate-policy`, `entry-disable`, `reduce-only`, `halt`, `issue-live-authority`, and
`verify-live-authority`.

- [ ] **Step 6: Build the operator console**

The default view shows, in plain language, per-account and aggregate portfolio health, available OS
sleeve budget, current loss/tier, data freshness, candidates and why they are blocked/eligible,
open/protected positions, current kill state and retrospective findings. Preserve account partitions
in every aggregate. `PriceChart.tsx` uses TradingView Lightweight Charts with OS-validated bars and
event markers; it never fetches hidden third-party chart data and is not an agent input.

- [ ] **Step 7: Add browser acceptance tests**

Test that a user can see a manual holding affecting a candidate, distinguish Zerodha from Alpaca,
change a future-effective exposure policy without resetting loss, disable entries for one broker,
inspect a CoverageReceipt and understand why a momentum candidate is blocked. Confirm no family or
FX execution control is visible.

- [ ] **Step 8: Verify and commit**

Run: `uv run pytest tests/integration/app -v && npm --prefix web test -- --run && npm --prefix web run build && npm --prefix web run e2e`

Expected: backend cycle, component tests, production build and Playwright acceptance pass.

```bash
git add src/trading_os/app tests/integration/app web
git commit -m "feat: add Trading OS operator console"
```

---

## Day 9 — End-to-end proof and reversible go-live

### Task 18: Prove both broker sleeves and issue scoped T0 live authority

**Files:**
- Create: `src/trading_os/app/readiness.py`
- Create: `src/trading_os/policy/live_authority.py`
- Create: `tests/replay/test_two_broker_cycle.py`
- Create: `tests/live_readiness/test_kite_readiness.py`
- Create: `tests/live_readiness/test_alpaca_readiness.py`
- Create: `tests/live_readiness/test_authority_receipt.py`
- Create: `docs/runbooks/live-v1.md`
- Create: `docs/runbooks/incidents.md`
- Create: `docs/runbooks/day-10-policy-change.md`

**Interfaces:**
- Consumes: complete application, external credentials/readiness and approved initial releases.
- Produces: reproducible two-broker replay evidence, broker-scoped `LiveAuthorityReceipt`s and a
  reversible operator go-live procedure.

- [ ] **Step 1: Write the failing authority-receipt test**

```python
from datetime import UTC, datetime, timedelta

from trading_os.policy.live_authority import LiveAuthorityReceipt, verify_live_authority


def test_receipt_is_broker_scoped_and_expires() -> None:
    now = datetime.now(UTC)
    receipt = LiveAuthorityReceipt(
        receipt_id="live-kite-1",
        account_id="kite-1",
        broker="kite",
        product_scope="cash_equity",
        readiness_report_hash="sha256:readiness",
        policy_release_ids=("capital-1", "exposure-t0", "promotion-t0"),
        kill_generation=4,
        code_commit="27658af",
        schema_version="0001",
        effective_from=now - timedelta(seconds=1),
        effective_until=now + timedelta(hours=8),
        signer="owner-1",
    )
    assert verify_live_authority(
        receipt,
        account_id="kite-1",
        broker="kite",
        at=now,
        policy_release_ids=receipt.policy_release_ids,
        kill_generation=4,
        code_commit="27658af",
        schema_version="0001",
    ).allowed
    assert not verify_live_authority(
        receipt,
        account_id="alpaca-1",
        broker="alpaca",
        at=now,
        policy_release_ids=receipt.policy_release_ids,
        kill_generation=4,
        code_commit="27658af",
        schema_version="0001",
    ).allowed
    assert not verify_live_authority(
        receipt,
        account_id="kite-1",
        broker="kite",
        at=now + timedelta(days=1),
        policy_release_ids=receipt.policy_release_ids,
        kill_generation=4,
        code_commit="27658af",
        schema_version="0001",
    ).allowed
```

- [ ] **Step 2: Run replay/readiness tests and verify failure**

Run: `uv run pytest tests/replay/test_two_broker_cycle.py tests/live_readiness/test_authority_receipt.py -v`

Expected: FAIL importing live authority/readiness modules.

- [ ] **Step 3: Implement content-addressed readiness evidence**

`ReadinessReport` records account hash, broker, environment, credential/session status, static-IP/
tagging status where required, data entitlement, account flags, instrument mapping, compliance
release freshness, capital/exposure/promotion releases, portfolio completeness, reconciliation,
kill-switch exercise, protection protocol exercise, endpoint identity, test manifest hash and
operator approval. Any failed required item prevents receipt issuance.

- [ ] **Step 4: Implement broker-scoped live authority**

`LiveAuthorityReceipt` binds account, broker, cash-equity product scope, T0 capital/exposure/loss
releases, readiness report hash, effective interval, kill generation, code commit, database schema
version and signer. Verification is performed immediately before every submit/amend/cancel/replace.
Revocation appends a new event and fences entries without stopping reconciliation.

```python
# src/trading_os/policy/live_authority.py
from datetime import datetime

from pydantic import BaseModel


class LiveAuthorityReceipt(BaseModel, frozen=True):
    receipt_id: str
    account_id: str
    broker: str
    product_scope: str
    readiness_report_hash: str
    policy_release_ids: tuple[str, ...]
    kill_generation: int
    code_commit: str
    schema_version: str
    effective_from: datetime
    effective_until: datetime
    signer: str


class LiveAuthorityDecision(BaseModel, frozen=True):
    allowed: bool
    reason: str


def verify_live_authority(
    receipt: LiveAuthorityReceipt,
    *,
    account_id: str,
    broker: str,
    at: datetime,
    policy_release_ids: tuple[str, ...],
    kill_generation: int,
    code_commit: str,
    schema_version: str,
) -> LiveAuthorityDecision:
    if receipt.account_id != account_id or receipt.broker != broker:
        return LiveAuthorityDecision(allowed=False, reason="scope_mismatch")
    if not receipt.effective_from <= at < receipt.effective_until:
        return LiveAuthorityDecision(allowed=False, reason="receipt_inactive")
    if receipt.policy_release_ids != policy_release_ids:
        return LiveAuthorityDecision(allowed=False, reason="policy_release_mismatch")
    if receipt.kill_generation != kill_generation:
        return LiveAuthorityDecision(allowed=False, reason="kill_generation_mismatch")
    if receipt.code_commit != code_commit or receipt.schema_version != schema_version:
        return LiveAuthorityDecision(allowed=False, reason="runtime_version_mismatch")
    return LiveAuthorityDecision(allowed=True, reason="receipt_effective")
```

- [ ] **Step 5: Run deterministic two-broker replay**

Replay fabricated but realistic Kite and Alpaca observations through discovery, portfolio analysis,
research fallback, sizing, compliance, fake execution, protection, reconciliation and retrospective.
Inject stale data, missing orders, credential loss, partial fill, protection rejection, callback
duplication, process crash and Day-10 policy supersession. Compare final state and event hashes across
two clean runs.

- [ ] **Step 6: Run bounded broker protocol checks**

Use Kite's available sandbox/protocol facilities and Alpaca paper endpoints only for contract-level
order/ack/cancel/protection mapping checks; no calendar campaign is required. Then run live-account
read-only readiness: identity, balances, positions, open orders, account flags, data entitlement and
instrument orderability. Never place a meaningless live order solely to satisfy a test.

- [ ] **Step 7: Complete operator runbooks**

`live-v1.md` must contain exact commands for services, migrations, read-only observation,
reconciliation, dry-effect cycle, readiness issuance, per-broker T0 activation, verification and
shutdown. `incidents.md` covers stale custody, reconciliation conflict, protection failure,
credential expiry, data entitlement loss, broker outage, unknown order effect and full-envelope
loss. `day-10-policy-change.md` demonstrates increasing or reducing a ceiling through a new release
without resetting loss or rewriting prior receipts.

- [ ] **Step 8: Run the full verification gate**

Run:

```bash
make verify
uv run pytest tests/contract tests/integration tests/replay -v
npm --prefix web test -- --run
npm --prefix web run build
npm --prefix web run e2e
uv run python -m trading_os.app.cli readiness --all-accounts --read-only
```

Expected: all static, unit, contract, integration, replay and UI tests pass; readiness either returns
two broker-scoped PASS reports or names the exact external blocker. A code-complete system with an
external blocker remains `LIVE_AUTHORITY_DENIED` for that broker.

- [ ] **Step 9: Issue T0 receipts and activate independently**

When each report passes, issue one Zerodha receipt for the INR 50,000 envelope and one Alpaca
receipt for the USD 200 envelope, both initially limited to T0 deployment/per-symbol policy. Enable
the scheduler for eligible opportunities. If only one broker passes, do not weaken the other broker's
gate; activate the passing broker and keep the failing broker entry-disabled while remediation runs.

- [ ] **Step 10: Commit the verified launch surface**

```bash
git add src/trading_os/app/readiness.py src/trading_os/policy/live_authority.py tests/replay tests/live_readiness docs/runbooks
git commit -m "feat: prove and gate two-broker live v1"
```

## Specification coverage matrix

| Controlling spec section | Implementing tasks |
|---|---|
| 1–3 precedence, scope and non-negotiable boundaries | 1, 3, 15, 18 and Global constraints |
| 4 system shape | 4–18 |
| 5 identity/account model | 3, 7, 8, 15 |
| 6 current portfolio analysis | 5–8, 16 |
| 7 deterministic decision sequence | 12–15 |
| 8 discovery/research coverage | 9–11, 17 |
| 9 market data and charting | 9, 17 |
| 10 configurable live authority | 3, 13, 15, 18 |
| 11 execution/protection/stops | 14–16, 18 |
| 12 retrospective loop | 11, 16, 17 |
| 13 family extension boundary | 3, 7, 8; execution intentionally denied in 15/18 |
| 14 multi-asset/FX boundary | 2, 3, 11, 15; execution intentionally denied in 18 |
| 15 nine-day acceptance | 18 |
| 16 first iteration versus final state | Post-Day-9 expansion order |

## Final acceptance checklist

- [ ] Every requirement in the controlling architecture amendment maps to a task above.
- [ ] Both broker account partitions import existing/manual holdings and open orders.
- [ ] Missing critical portfolio dimensions block new exposure.
- [ ] Broad discovery and CoverageReceipts are independent from tradable allowlists.
- [ ] Agents cannot express executable fields and relational operation survives LLM/graph outage.
- [ ] Provisional sizing precedes risk/compliance tightening and CAS reservation.
- [ ] Live writes require broker-scoped capability and authority receipts.
- [ ] Protection, kill generations, crash recovery and reconciliation pass injected-failure tests.
- [ ] Exposure/budget gates can change on Day 10 through new immutable releases.
- [ ] Family and non-equity execution remain structurally denied.
- [ ] Operator console and runbooks explain current state without requiring technical interpretation.
- [ ] The current commit, schema and policy hashes can reproduce every decision.

## Post-Day-9 expansion order

1. Deepen data/source redundancy and portfolio factor, correlation, liquidity and tax-lot analysis.
2. Add read-only, consented family profiles and partition-preserving HouseholdPortfolioViews.
3. Add separately authenticated family accounts and per-account proposal/approval workflows.
4. Expand official events, sentiment corroboration, relationship evidence and ontology challengers.
5. Calibrate promotion/demotion and adaptive resource allocation from live receipts.
6. Begin an independent research-only currency/FX product specification; do not enable execution
   until its identity, accounting, margin, settlement, reconciliation and current legal gates pass.
