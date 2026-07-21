# Trading OS v1 Implementation Plan

> **Ontology coordination:** Execute Tasks 1–14 in this plan, then execute
> `docs/superpowers/plans/2026-07-21-trading-world-ontology-implementation.md` in full. That plan
> augments Tasks 12–13 and supersedes the semantic/KG/research responsibilities of Tasks 15–17 below. Resume here at Task
> 18 using `DecisionFeatureSet`; Task 32 calls `ReasoningCycle`; Task 34 consumes semantic promotion
> evidence; Task 35 remains the causal-replay specialization. Where the two plans conflict, the
> approved ontology design and ontology implementation plan win.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the paper-first v1 Trading OS for Zerodha and Alpaca with a strictly typed LLM seam, deterministic sizing/risk/compliance/execution, crash-safe broker effects, independently validated data, and a frozen promotion gate.

**Architecture:** Implement a ports-and-adapters Python package around an append-only event core. Slow LLM research and causal-KG classification produce only strict seam types; all numerical sizing, risk, compliance, protection, accounting, orchestration, and promotion logic remains deterministic. Deliver working software incrementally in four milestones: deterministic foundation, validated research/data, protected paper execution, then evaluation and operations.

**Tech Stack:** Python 3.11+, `uv`, Pydantic v2, SQLAlchemy 2 + asyncpg/Postgres/TimescaleDB, Valkey, Neo4j Community, APScheduler, exchange-calendars, pandas/NumPy/SciPy/statsmodels, Alpaca SDK, Kite Connect, FastAPI, python-telegram-bot, structlog, pytest/Hypothesis/mypy/ruff.

## Global Constraints

- D4/D30 is absolute: `ResearchTradeThesis` never enters a hot-path module; `Sizer`, `RiskEngine`, `ComplianceGate`, `ExitManager`, and `KillSwitch` cannot read LLM JSON, rationale, confidence statistics, prompt/model keys, or calibration values.
- Conviction is a closed enum used only by `GateRank` for admission and ordering. It never changes quantity, price, stop level, risk limit, or compliance.
- v1 is long-only, cash-only, daily-bar/EOD swing/positional trading for Zerodha NSE/BSE and Alpaca NYSE/NASDAQ. No intraday alpha, leverage, shorts, derivatives, Angel One, IBKR, Europe, or alt-data.
- Event-triggered LLM jobs may refresh labels for the next allowed decision window; they never trade off cadence.
- No LangGraph, broker MCP servers, Kafka, NATS, Kubernetes, continuous agent loop, or paid infrastructure dependency.
- Postgres/TimescaleDB is durable truth, Valkey is projection-only, and broker custody is reconciled into new append-only observations; history is never rewritten.
- Every broker effect is preceded by a durable `IntentId`; ambiguous outcomes reconcile before retry and never blind-retry.
- A position is `PROTECTED` only when broker-confirmed protective quantity covers broker-reconciled open quantity. Coverage deficits block new exposure and move the symbol to `REDUCING`.
- Fixed-point `Decimal` is mandatory for quantities, prices, money, FX rates, fees, taxes, and accounting. Binary floating point is allowed only inside statistical arrays and must be converted at typed boundaries.
- Every signal, traversal, simulation, and evaluation consumes a sealed `ValidatedDataSnapshotId`; no consumer reads mutable `latest` data.
- CI never places a live Kite order. Kite behavior is tested with recorded fixtures, the simulated broker, and human-gated out-of-band smoke procedures.
- Live mode remains mechanically disabled until the 90-day promotion gate and every D19 verify-before-live blocker are recorded as satisfied.
- Use async interfaces for broker, database, market-data, notification, and external-provider operations; pure calculations remain synchronous.
- All implementation follows red-green-refactor, strict typing, deterministic tests, and one reviewable commit per task.

---

## Planned File Structure

```text
src/trading_os/
  __init__.py                 # package version only
  cli.py                      # paper-mode commands and guarded live entrypoint
  config.py                   # validated settings; no secret values in logs
  domain/                     # immutable IDs, enums, money, orders, events, snapshots
  ports/                      # the 13 D29 external boundaries
  persistence/                # Postgres event store, migrations, projections, Valkey cache
  data/                       # CA/universe/cash ingest and ValidatedDataSnapshot creation
  signals/                    # momentum, trend, regime, GateRank, permanent rule-null
  kg/                         # graph admission, deterministic traversal, fitted weights
  research/                   # LLMRole, analysts, synthesizer, seam projector
  portfolio/                  # sizing, risk, reservations, strategy books, calibration
  compliance/                 # India, US, remittance, residency, idle-FX rules
  brokers/                    # normalized adapter, simulated, Alpaca, Kite
  execution/                  # intents, coordinator, kill switch, exits, protection, reconcile
  accounting/                 # FX-rate records, immutable ledger, tax/report exports
  hitl/                       # approval tokens, backend, Telegram and localhost transports
  control/                    # readiness gates, scheduler, EOD orchestrator, watchdog
  evaluation/                 # fill/cost fidelity, CPCV/DSR, scoreboards, promotion manifest
  observability/              # structlog configuration and redaction
tests/
  unit/                       # pure business rules and state machines
  contract/                   # port/adapter suites using fakes and recorded fixtures
  integration/                # opt-in Postgres/Valkey/Neo4j/Alpaca-paper tests
  fixtures/brokers/           # redacted Kite/Alpaca payload fixtures
alembic/                      # append-only schema migrations
config/                       # non-secret example configuration and frozen rule tables
scripts/                      # backup, fixture validation, paper-operation helpers
```

The spec spans several subsystems, but this single master plan keeps their dependency order
explicit. Milestone boundaries are safe split points if execution is distributed across sessions;
task numbers and interfaces remain authoritative across those splits.

---

## Milestone 1 — Deterministic Foundation and Durable State

### Task 1: Replace the superseded repository baseline

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `config/env.example`
- Create: `compose.yaml`
- Create: `src/trading_os/__init__.py`
- Create: `src/trading_os/config.py`
- Create: `tests/unit/test_config.py`

**Interfaces:**
- Consumes: none.
- Produces: `Settings`, package `trading_os`, local Postgres/TimescaleDB, Valkey, and Neo4j services used by all later tasks.

- [ ] **Step 1: Write the failing settings test**

```python
# tests/unit/test_config.py
from trading_os.config import RunMode, Settings


def test_settings_default_to_safe_paper_mode() -> None:
    settings = Settings(_env_file=None)

    assert settings.run_mode is RunMode.PAPER
    assert settings.live_trading_enabled is False
    assert settings.default_market == "india"


def test_live_mode_requires_explicit_enablement() -> None:
    settings = Settings(_env_file=None, run_mode="live")

    assert settings.run_mode is RunMode.LIVE
    assert settings.live_trading_enabled is False
```

- [ ] **Step 2: Run the test and confirm the package does not exist**

Run: `uv run pytest tests/unit/test_config.py -v`

Expected: FAIL during collection with `ModuleNotFoundError: No module named 'trading_os'`.

- [ ] **Step 3: Replace the dependency/configuration baseline and add safe settings**

Use this dependency direction in `pyproject.toml`; remove LangGraph, LangChain, SmartAPI,
IBKR, Polygon, and IEX dependencies from v1:

```toml
[project]
name = "trading-os"
version = "0.1.0"
description = "Paper-first India and US swing/positional equity trading OS"
requires-python = ">=3.11"
dependencies = [
  "alembic>=1.13,<2",
  "alpaca-py>=0.26,<1",
  "apscheduler>=3.10,<4",
  "asyncpg>=0.29,<1",
  "exchange-calendars>=4.5,<5",
  "fastapi>=0.115,<1",
  "httpx>=0.27,<1",
  "kiteconnect>=5,<6",
  "neo4j>=5.24,<6",
  "numpy>=1.26,<3",
  "orjson>=3.10,<4",
  "pandas>=2.2,<3",
  "pydantic>=2.7,<3",
  "pydantic-settings>=2.3,<3",
  "python-telegram-bot>=21,<23",
  "scipy>=1.13,<2",
  "sqlalchemy[asyncio]>=2.0,<3",
  "statsmodels>=0.14,<1",
  "structlog>=24,<26",
  "typer>=0.12,<1",
  "uvicorn>=0.30,<1",
  "valkey>=6,<7",
]

[project.optional-dependencies]
dev = [
  "hypothesis>=6.100,<7",
  "mypy>=1.10,<2",
  "pytest>=8,<9",
  "pytest-asyncio>=0.23,<1",
  "pytest-cov>=5,<7",
  "respx>=0.21,<1",
  "ruff>=0.4,<1",
]

[project.scripts]
trading-os = "trading_os.cli:app"

[build-system]
requires = ["hatchling>=1.25,<2"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/trading_os"]
```

Add the safe settings implementation:

```python
# src/trading_os/config.py
from enum import StrEnum

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunMode(StrEnum):
    SIMULATED = "simulated"
    PAPER = "paper"
    LIVE = "live"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="TRADING_OS_", extra="forbid")

    run_mode: RunMode = RunMode.PAPER
    live_trading_enabled: bool = False
    default_market: str = "india"
    database_url: str = "postgresql+asyncpg://trading_os:trading_os@localhost:5432/trading_os"
    valkey_url: str = "redis://localhost:6379/0"
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: SecretStr = Field(default=SecretStr("local-development-only"))
```

`compose.yaml` must pin three services: `timescale/timescaledb:latest-pg16`,
`valkey/valkey:8-alpine`, and `neo4j:5-community`, each with a healthcheck and named volume.
Rewrite `README.md`, the top status block in `CLAUDE.md`, and `config/env.example` so only the
finalized Zerodha/Alpaca two-market design and `TRADING_OS_` settings remain.

- [ ] **Step 4: Sync and verify the safe baseline**

Run: `uv sync --extra dev && uv run pytest tests/unit/test_config.py -v`

Expected: dependency resolution succeeds and both tests PASS.

- [ ] **Step 5: Run static checks**

Run: `uv run ruff check src tests && uv run mypy src`

Expected: both commands exit 0.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml README.md CLAUDE.md config/env.example compose.yaml src/trading_os tests/unit/test_config.py uv.lock
git commit -m "chore: align repository with approved trading os design"
```

### Task 2: Add immutable IDs, enums, and fixed-point value objects

**Files:**
- Create: `src/trading_os/domain/__init__.py`
- Create: `src/trading_os/domain/enums.py`
- Create: `src/trading_os/domain/ids.py`
- Create: `src/trading_os/domain/money.py`
- Create: `tests/unit/domain/test_values.py`

**Interfaces:**
- Consumes: Pydantic v2 from Task 1.
- Produces: `IntentId`, `SnapshotId`, `StrategyBookId`, `Money`, `Quantity`, `Price`,
  `Direction`, `Market`, `Currency`, `KillState`, and `CoverageState` for every later task.

- [ ] **Step 1: Write failing value-object tests**

```python
# tests/unit/domain/test_values.py
from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading_os.domain.enums import Currency, Direction
from trading_os.domain.ids import IntentId
from trading_os.domain.money import Money, Quantity


def test_money_requires_matching_currency_for_addition() -> None:
    with pytest.raises(ValueError, match="currency mismatch"):
        _ = Money(amount=Decimal("10.00"), currency=Currency.INR) + Money(
            amount=Decimal("1.00"), currency=Currency.USD
        )


def test_quantity_rejects_binary_float() -> None:
    with pytest.raises(ValidationError):
        Quantity(value=1.5)


def test_direction_is_long_only() -> None:
    assert set(Direction) == {Direction.LONG, Direction.FLAT}


def test_intent_id_is_stable_text() -> None:
    value = IntentId.new()
    assert IntentId.parse(str(value)) == value
```

- [ ] **Step 2: Run the tests and observe missing domain modules**

Run: `uv run pytest tests/unit/domain/test_values.py -v`

Expected: FAIL with missing `trading_os.domain` imports.

- [ ] **Step 3: Implement strict values**

```python
# src/trading_os/domain/enums.py
from enum import StrEnum


class Currency(StrEnum):
    INR = "INR"
    USD = "USD"


class Market(StrEnum):
    INDIA = "india"
    US = "us"


class Direction(StrEnum):
    LONG = "long"
    FLAT = "flat"


class KillState(StrEnum):
    ACTIVE = "active"
    REDUCING = "reducing"
    HALTED = "halted"
    HALTED_UNVERIFIED = "halted_unverified"


class CoverageState(StrEnum):
    SUBMITTED_UNCONFIRMED = "submitted_unconfirmed"
    PARTIALLY_FILLED_UNPROTECTED = "partially_filled_unprotected"
    PROTECTION_PENDING = "protection_pending"
    PROTECTED = "protected"
```

```python
# src/trading_os/domain/ids.py
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict


class _Id(BaseModel):
    model_config = ConfigDict(frozen=True)
    value: UUID

    @classmethod
    def new(cls) -> Self:
        return cls(value=uuid4())

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)


class IntentId(_Id): ...
class SnapshotId(_Id): ...
class StrategyBookId(_Id): ...
class PositionEpisodeId(_Id): ...
class EventId(_Id): ...
```

```python
# src/trading_os/domain/money.py
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Strict
from typing_extensions import Annotated

from trading_os.domain.enums import Currency

StrictDecimal = Annotated[Decimal, Strict()]


class Money(BaseModel):
    model_config = ConfigDict(frozen=True, allow_inf_nan=False)
    amount: StrictDecimal
    currency: Currency

    def __add__(self, other: Self) -> Self:
        if self.currency is not other.currency:
            raise ValueError("currency mismatch")
        return type(self)(amount=self.amount + other.amount, currency=self.currency)


class Quantity(BaseModel):
    model_config = ConfigDict(frozen=True, allow_inf_nan=False)
    value: StrictDecimal


class Price(BaseModel):
    model_config = ConfigDict(frozen=True, allow_inf_nan=False)
    value: StrictDecimal
    currency: Currency
```

- [ ] **Step 4: Verify values and strict typing**

Run: `uv run pytest tests/unit/domain/test_values.py -v && uv run mypy src/trading_os/domain`

Expected: all tests PASS and mypy exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/domain tests/unit/domain/test_values.py
git commit -m "feat: add strict trading domain value objects"
```

### Task 3: Enforce the D30 seam with separate slow- and hot-path types

**Files:**
- Create: `src/trading_os/research/__init__.py`
- Create: `src/trading_os/research/models.py`
- Create: `src/trading_os/research/seam.py`
- Create: `src/trading_os/domain/candidates.py`
- Create: `tests/unit/research/test_seam.py`
- Create: `tests/unit/research/test_hot_path_imports.py`

**Interfaces:**
- Consumes: `Direction` and immutable IDs from Task 2.
- Produces: `ResearchTradeThesis`, `HotPathCandidate`, `ConvictionBand`, and
  `SeamProjector.project(thesis, symbol)`.

- [ ] **Step 1: Write seam rejection and import-boundary tests**

```python
# tests/unit/research/test_seam.py
from uuid import uuid4

import pytest
from pydantic import ValidationError

from trading_os.domain.candidates import ConvictionBand
from trading_os.research.models import ResearchTradeThesis
from trading_os.research.seam import SeamProjector


def test_research_thesis_rejects_prompt_injected_sizing_fields() -> None:
    with pytest.raises(ValidationError):
        ResearchTradeThesis.model_validate(
            {
                "thesis_id": str(uuid4()),
                "conviction_band": "high",
                "direction": "long",
                "rationale": "valid text",
                "target_vol": 0.25,
                "stop_hint": "5%",
                "size_pct": 10,
            }
        )


def test_projector_excludes_rationale() -> None:
    thesis = ResearchTradeThesis(
        thesis_id=uuid4(),
        conviction_band=ConvictionBand.HIGH,
        direction="long",
        rationale="slow-plane only",
    )
    candidate = SeamProjector().project(thesis, symbol="INFY")

    assert set(candidate.model_dump()) == {"thesis_id", "symbol", "conviction_band", "direction"}
```

```python
# tests/unit/research/test_hot_path_imports.py
from pathlib import Path


def test_hot_path_does_not_import_research_models() -> None:
    forbidden = "trading_os.research.models"
    hot_paths = ["portfolio", "compliance", "execution", "brokers"]
    offenders = [
        str(path)
        for package in hot_paths
        for path in Path("src/trading_os", package).rglob("*.py")
        if forbidden in path.read_text(encoding="utf-8")
    ]
    assert offenders == []
```

- [ ] **Step 2: Run the seam tests and confirm missing types**

Run: `uv run pytest tests/unit/research/test_seam.py tests/unit/research/test_hot_path_imports.py -v`

Expected: FAIL with missing research/candidate modules.

- [ ] **Step 3: Implement strict slow-plane and seam types**

```python
# src/trading_os/domain/candidates.py
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from trading_os.domain.enums import Direction


class ConvictionBand(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HotPathCandidate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    thesis_id: UUID
    symbol: str
    conviction_band: ConvictionBand
    direction: Direction
```

```python
# src/trading_os/research/models.py
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from trading_os.domain.candidates import ConvictionBand
from trading_os.domain.enums import Direction


class ResearchTradeThesis(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    thesis_id: UUID
    conviction_band: ConvictionBand
    direction: Direction
    rationale: str
```

```python
# src/trading_os/research/seam.py
from trading_os.domain.candidates import HotPathCandidate
from trading_os.research.models import ResearchTradeThesis


class SeamProjector:
    def project(self, thesis: ResearchTradeThesis, *, symbol: str) -> HotPathCandidate:
        return HotPathCandidate(
            thesis_id=thesis.thesis_id,
            symbol=symbol,
            conviction_band=thesis.conviction_band,
            direction=thesis.direction,
        )
```

- [ ] **Step 4: Verify seam containment**

Run: `uv run pytest tests/unit/research/test_seam.py tests/unit/research/test_hot_path_imports.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/domain/candidates.py src/trading_os/research tests/unit/research
git commit -m "feat: enforce strict slow-to-hot path seam"
```

### Task 4: Define orders, fills, positions, and global portfolio snapshots

**Files:**
- Create: `src/trading_os/domain/orders.py`
- Create: `src/trading_os/domain/portfolio.py`
- Create: `src/trading_os/domain/snapshots.py`
- Create: `tests/unit/domain/test_orders.py`
- Create: `tests/unit/domain/test_portfolio.py`

**Interfaces:**
- Consumes: IDs, enums, `Price`, `Quantity`, and `Money` from Task 2.
- Produces: `OrderRequest`, `OrderStatus`, `Fill`, `Position`, `AccountSnapshot`,
  `GlobalPortfolioSnapshot`, and `OrderReservation` used by brokers, risk, execution, and replay.

- [ ] **Step 1: Write failing invariant tests**

```python
# tests/unit/domain/test_orders.py
from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading_os.domain.enums import Currency, Market
from trading_os.domain.ids import IntentId, SnapshotId, StrategyBookId
from trading_os.domain.money import Price, Quantity
from trading_os.domain.orders import OrderRequest, OrderSide, OrderType


def test_order_request_rejects_sell_to_open() -> None:
    with pytest.raises(ValidationError):
        OrderRequest(
            intent_id=IntentId.new(),
            snapshot_id=SnapshotId.new(),
            strategy_book_id=StrategyBookId.new(),
            market=Market.US,
            symbol="AAPL",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=Quantity(value=Decimal("1")),
            limit_price=Price(value=Decimal("180"), currency=Currency.USD),
            reduce_only=False,
            kill_generation=0,
        )
```

```python
# tests/unit/domain/test_portfolio.py
from trading_os.domain.portfolio import GlobalPortfolioSnapshot


def test_global_snapshot_version_is_non_negative() -> None:
    snapshot = GlobalPortfolioSnapshot.empty(version=0)
    assert snapshot.version == 0
    assert snapshot.positions == ()
    assert snapshot.pending_orders == ()
```

- [ ] **Step 2: Run tests and confirm models are absent**

Run: `uv run pytest tests/unit/domain/test_orders.py tests/unit/domain/test_portfolio.py -v`

Expected: FAIL on missing order and portfolio modules.

- [ ] **Step 3: Implement immutable order and portfolio models**

Define `OrderSide={BUY,SELL}`, `OrderType={LIMIT,STOP,STOP_LIMIT}`, and
`OrderStatus={PENDING,ACCEPTED,PARTIALLY_FILLED,FILLED,CANCELLED,REJECTED,EXPIRED,OUTCOME_UNKNOWN}`.
Implement `OrderRequest` with `extra="forbid"`, and enforce:

```python
from pydantic import model_validator
from typing import Self

@model_validator(mode="after")
def enforce_long_only(self) -> Self:
    if self.side is OrderSide.SELL and not self.reduce_only:
        raise ValueError("sell orders must be reduce_only in v1")
    if self.order_type is OrderType.LIMIT and self.limit_price is None:
        raise ValueError("limit order requires limit_price")
    return self
```

`GlobalPortfolioSnapshot` must be frozen and contain `snapshot_id`, `version`, `positions`,
`pending_orders`, `settled_cash_by_currency`, `protection_deficits`, `fx_rate_record_ids`, and
`kill_generation`. Its `empty(version)` constructor returns immutable empty tuples/maps rather
than mutable defaults.

- [ ] **Step 4: Verify domain invariants**

Run: `uv run pytest tests/unit/domain -v && uv run mypy src/trading_os/domain`

Expected: all domain tests PASS and mypy exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/domain tests/unit/domain
git commit -m "feat: model immutable orders and portfolio snapshots"
```

### Task 5: Define all D29 typed ports and reusable offline fakes

**Files:**
- Create: `src/trading_os/ports/__init__.py`
- Create: `src/trading_os/ports/clock.py`
- Create: `src/trading_os/ports/calendar.py`
- Create: `src/trading_os/ports/market_data.py`
- Create: `src/trading_os/ports/fx.py`
- Create: `src/trading_os/ports/security_master.py`
- Create: `src/trading_os/ports/graph.py`
- Create: `src/trading_os/ports/event_store.py`
- Create: `src/trading_os/ports/state_cache.py`
- Create: `src/trading_os/ports/broker.py`
- Create: `src/trading_os/ports/llm.py`
- Create: `src/trading_os/ports/secrets.py`
- Create: `src/trading_os/ports/hitl.py`
- Create: `src/trading_os/ports/notifier.py`
- Create: `tests/fakes/ports.py`
- Create: `tests/unit/ports/test_fakes.py`

**Interfaces:**
- Consumes: domain models from Tasks 2–4.
- Produces: the 13 protocol boundaries named in D29 and deterministic in-memory fakes used by all later tests.

- [ ] **Step 1: Write a failing protocol/fake test**

```python
# tests/unit/ports/test_fakes.py
from datetime import UTC, datetime

from trading_os.ports.clock import ClockPort
from tests.fakes.ports import FrozenClock


def test_frozen_clock_implements_clock_port() -> None:
    now = datetime(2026, 7, 21, 12, tzinfo=UTC)
    clock: ClockPort = FrozenClock(now)
    assert clock.now() == now
```

- [ ] **Step 2: Run the test and observe missing protocols**

Run: `uv run pytest tests/unit/ports/test_fakes.py -v`

Expected: FAIL with missing `trading_os.ports.clock`.

- [ ] **Step 3: Add small protocols with explicit signatures**

Use `typing.Protocol` and immutable DTOs. The core signatures are:

```python
class ClockPort(Protocol):
    def now(self) -> datetime: ...

class CalendarPort(Protocol):
    def session(self, market: Market, trade_date: date) -> MarketSession | None: ...

class MarketDataPort(Protocol):
    async def fetch_bars(self, request: BarRequest) -> tuple[RawBar, ...]: ...
    async def fetch_corporate_actions(self, market: Market, as_of: date) -> tuple[CorporateAction, ...]: ...

class FxRatePort(Protocol):
    async def live_rate(self, base: Currency, quote: Currency) -> FxRateRecord: ...
    async def rule115_rate(self, transaction_date: date) -> FxRateRecord: ...

class EventStorePort(Protocol):
    async def append(self, event: EventEnvelope, expected_stream_version: int) -> int: ...
    async def read_stream(self, stream_id: str, after_version: int = -1) -> tuple[EventEnvelope, ...]: ...

class StateCachePort(Protocol):
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes) -> None: ...

class BrokerTransportPort(Protocol):
    async def submit(self, order: OrderRequest) -> BrokerOrder: ...
    async def cancel(self, intent_id: IntentId, broker_order_id: str) -> BrokerOrder: ...
    async def orders(self, market: Market, since: datetime) -> tuple[BrokerOrder, ...]: ...
    async def positions(self, market: Market) -> tuple[Position, ...]: ...
```

Define equivalent explicit protocols for `SecurityMasterPort`, `GraphStorePort`, `LLMRolePort`,
`SecretsPort`, `HITLTransportPort`, and `NotifierPort`. `tests/fakes/ports.py` must provide
`FrozenClock`, `InMemoryEventStore`, `InMemoryStateCache`, `FakeBrokerTransport`,
`FakeMarketData`, `FakeFxRates`, `FakeGraphStore`, `FakeLLMRole`, `FakeHITLTransport`, and
`CollectingNotifier`; each stores calls in typed lists for assertions.

- [ ] **Step 4: Verify protocols and fakes**

Run: `uv run pytest tests/unit/ports/test_fakes.py -v && uv run mypy src/trading_os/ports tests/fakes`

Expected: test PASS and mypy confirms every assigned fake satisfies its protocol.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/ports tests/fakes tests/unit/ports
git commit -m "feat: define typed external ports and offline fakes"
```

### Task 6: Create the append-only event envelope and recovery event catalogue

**Files:**
- Create: `src/trading_os/domain/events.py`
- Create: `src/trading_os/persistence/__init__.py`
- Create: `src/trading_os/persistence/memory_event_store.py`
- Create: `tests/unit/persistence/test_event_store.py`
- Create: `tests/unit/domain/test_events.py`

**Interfaces:**
- Consumes: IDs, fixed-point values, `EventStorePort`, and order/portfolio types.
- Produces: `EventEnvelope`, `EventType`, typed payload union, and optimistic stream versions.

- [ ] **Step 1: Write failing append-only and event-catalogue tests**

```python
# tests/unit/persistence/test_event_store.py
import pytest

from trading_os.domain.events import EventEnvelope, EventType, KillSwitchGenerationBumped
from trading_os.persistence.memory_event_store import InMemoryEventStore, StreamConflict


@pytest.mark.asyncio
async def test_append_requires_expected_stream_version() -> None:
    store = InMemoryEventStore()
    event = EventEnvelope.new(
        stream_id="control:global",
        event_type=EventType.KILL_SWITCH_GENERATION_BUMPED,
        payload=KillSwitchGenerationBumped(generation=1, reason="manual halt"),
    )
    assert await store.append(event, expected_stream_version=-1) == 0
    with pytest.raises(StreamConflict):
        await store.append(event, expected_stream_version=-1)
```

```python
# tests/unit/domain/test_events.py
from trading_os.domain.events import EventType


def test_recovery_event_catalogue_is_complete() -> None:
    required = {
        "position_episode_opened", "position_episode_closed", "fill_allocated",
        "stop_intent_placed", "stop_ack_received", "protection_coverage_changed",
        "trail_ratcheted", "time_stop_deadline_set", "entry_regime_recorded",
        "approval_decision", "order_reservation_committed", "order_reservation_released",
        "strategy_attribution", "fx_lot_opened", "fx_lot_consumed",
        "idle_fx_lot_opened", "idle_fx_lot_disposed", "calibration_recorded",
        "kill_switch_generation_bumped",
    }
    assert required <= {item.value for item in EventType}
```

- [ ] **Step 2: Run tests and confirm event types are missing**

Run: `uv run pytest tests/unit/domain/test_events.py tests/unit/persistence/test_event_store.py -v`

Expected: FAIL with missing event modules.

- [ ] **Step 3: Implement the immutable envelope and typed payloads**

`EventEnvelope` must contain `event_id`, `stream_id`, `stream_version`, `event_type`,
`occurred_at`, `recorded_at`, `correlation_id`, `causation_id`, `schema_version`, and a
discriminated typed payload. Use UTC-aware datetimes and `extra="forbid"`. Provide one payload
model for every `EventType` in the test. The factory sets `stream_version=-1`; the store assigns
the committed version without mutating the caller's instance by returning a copied envelope.

```python
class StreamConflict(RuntimeError):
    pass


class InMemoryEventStore:
    def __init__(self) -> None:
        self._streams: dict[str, list[EventEnvelope]] = {}

    async def append(self, event: EventEnvelope, expected_stream_version: int) -> int:
        stream = self._streams.setdefault(event.stream_id, [])
        current = len(stream) - 1
        if current != expected_stream_version:
            raise StreamConflict(f"expected {expected_stream_version}, found {current}")
        version = current + 1
        stream.append(event.model_copy(update={"stream_version": version}))
        return version

    async def read_stream(self, stream_id: str, after_version: int = -1) -> tuple[EventEnvelope, ...]:
        return tuple(self._streams.get(stream_id, [])[after_version + 1 :])
```

- [ ] **Step 4: Verify catalogue, serialization, and optimistic concurrency**

Run: `uv run pytest tests/unit/domain/test_events.py tests/unit/persistence/test_event_store.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/domain/events.py src/trading_os/persistence tests/unit/domain/test_events.py tests/unit/persistence
git commit -m "feat: add append-only recovery event model"
```

### Task 7: Persist events atomically in Postgres

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/20260721_0001_event_log.py`
- Create: `src/trading_os/persistence/database.py`
- Create: `src/trading_os/persistence/postgres_event_store.py`
- Create: `tests/integration/persistence/test_postgres_event_store.py`

**Interfaces:**
- Consumes: `EventEnvelope` and `EventStorePort` from Tasks 5–6.
- Produces: the D15 `EventLog` implementation as `PostgresEventStore`, with atomic expected-version enforcement and immutable JSONB payloads.

- [ ] **Step 1: Write the integration contract before the schema exists**

```python
# tests/integration/persistence/test_postgres_event_store.py
import pytest

from trading_os.domain.events import EventEnvelope, EventType, KillSwitchGenerationBumped
from trading_os.persistence.postgres_event_store import PostgresEventStore


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgres_store_preserves_order_and_rejects_conflict(pg_store: PostgresEventStore) -> None:
    first = EventEnvelope.new(
        stream_id="control:global",
        event_type=EventType.KILL_SWITCH_GENERATION_BUMPED,
        payload=KillSwitchGenerationBumped(generation=1, reason="test"),
    )
    assert await pg_store.append(first, expected_stream_version=-1) == 0
    loaded = await pg_store.read_stream("control:global")
    assert loaded[0].payload == first.payload
```

- [ ] **Step 2: Start Postgres and confirm the schema/store test fails**

Run: `docker compose up -d postgres && uv run pytest tests/integration/persistence/test_postgres_event_store.py -v`

Expected: FAIL because the migration/store/fixture is absent.

- [ ] **Step 3: Add the migration and async store**

The `event_log` table must contain:

```sql
event_id UUID PRIMARY KEY,
stream_id TEXT NOT NULL,
stream_version BIGINT NOT NULL,
event_type TEXT NOT NULL,
occurred_at TIMESTAMPTZ NOT NULL,
recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
correlation_id UUID,
causation_id UUID,
schema_version INTEGER NOT NULL,
payload JSONB NOT NULL,
UNIQUE (stream_id, stream_version)
```

`PostgresEventStore.append()` must start a transaction, acquire
`pg_advisory_xact_lock(hashtextextended(stream_id, 0))`, read the current maximum version,
compare it with `expected_stream_version`, insert the next version, and commit. It must map a
unique violation or version mismatch to the same `StreamConflict` used by the in-memory store.
`read_stream()` orders by `stream_version ASC` and reconstructs the discriminated payload model.

- [ ] **Step 4: Apply migration and run the integration contract**

Run: `uv run alembic upgrade head && uv run pytest tests/integration/persistence/test_postgres_event_store.py -v`

Expected: integration test PASS.

- [ ] **Step 5: Commit**

```bash
git add alembic.ini alembic src/trading_os/persistence tests/integration/persistence
git commit -m "feat: persist append-only events in postgres"
```

### Task 8: Build replayable portfolio projections and a disposable Valkey cache

**Files:**
- Create: `src/trading_os/persistence/projections.py`
- Create: `src/trading_os/persistence/valkey_cache.py`
- Create: `tests/unit/persistence/test_projections.py`
- Create: `tests/integration/persistence/test_valkey_cache.py`

**Interfaces:**
- Consumes: ordered `EventEnvelope` streams and `StateCachePort`.
- Produces: `PortfolioProjection.apply(event)`, `replay(events)`, and `ValkeyStateCache`.

- [ ] **Step 1: Write a replay-equivalence test**

```python
# tests/unit/persistence/test_projections.py
from trading_os.persistence.projections import PortfolioProjection, replay


def test_replay_after_each_boundary_matches_single_pass(recovery_events) -> None:
    expected = replay(recovery_events)
    for boundary in range(len(recovery_events) + 1):
        first = replay(recovery_events[:boundary])
        resumed = PortfolioProjection.from_state(first).apply_all(recovery_events[boundary:])
        assert resumed == expected


def test_replaying_same_event_id_is_rejected(recovery_events) -> None:
    projection = PortfolioProjection.empty().apply(recovery_events[0])
    assert projection.apply(recovery_events[0]).duplicate_event_ids == (recovery_events[0].event_id,)
```

- [ ] **Step 2: Run and confirm projection support is absent**

Run: `uv run pytest tests/unit/persistence/test_projections.py -v`

Expected: FAIL with missing projection module.

- [ ] **Step 3: Implement pure folds and cache serialization**

`PortfolioProjection` is a frozen model containing positions, pending intents, protection
coverage, trailing stops, deadlines, entry regimes, approvals, reservations, strategy
attribution, FX/idle-FX lots, calibration keys, kill generation, last stream versions, and applied
event IDs. Each `EventType` gets one total deterministic handler. Unknown schema versions fail
closed with `UnsupportedEventSchema`; duplicate event IDs are recorded and do not reapply effects.

`ValkeyStateCache` stores only `projection.model_dump_json()` under a namespaced key. Deleting all
Valkey keys and replaying Postgres must reproduce the same projection hash.

```python
def replay(events: tuple[EventEnvelope, ...]) -> PortfolioProjection:
    state = PortfolioProjection.empty()
    for event in events:
        state = state.apply(event)
    return state
```

- [ ] **Step 4: Verify replay and disposable-cache behavior**

Run: `uv run pytest tests/unit/persistence/test_projections.py -v`

Run: `docker compose up -d valkey && uv run pytest tests/integration/persistence/test_valkey_cache.py -v`

Expected: both suites PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/persistence tests/unit/persistence tests/integration/persistence
git commit -m "feat: rebuild portfolio state from durable events"
```

### Task 9: Implement kill-switch scopes and stale-worker fencing

**Files:**
- Create: `src/trading_os/execution/__init__.py`
- Create: `src/trading_os/execution/kill_switch.py`
- Create: `tests/unit/execution/test_kill_switch.py`

**Interfaces:**
- Consumes: `KillState`, event store, `KillSwitchGenerationBumped`, `Market`, and symbol scopes.
- Produces: `KillSwitch.snapshot()`, `halt(scope, reason)`, `reduce(scope, reason)`,
  `activate(scope, authenticated_localhost)`, and `assert_submission_allowed(order)`.

- [ ] **Step 1: Write failing state, scope, and fencing tests**

```python
# tests/unit/execution/test_kill_switch.py
import pytest

from trading_os.domain.enums import KillState, Market
from trading_os.execution.kill_switch import KillScope, KillSwitch, StaleGeneration


@pytest.mark.asyncio
async def test_halt_bumps_generation_and_fences_stale_worker(event_store) -> None:
    switch = KillSwitch(event_store)
    before = await switch.snapshot()
    after = await switch.halt(KillScope.global_scope(), reason="dead-man")

    assert after.state is KillState.HALTED
    assert after.generation == before.generation + 1
    with pytest.raises(StaleGeneration):
        await switch.assert_submission_allowed(
            market=Market.US,
            symbol="AAPL",
            reduce_only=False,
            generation=before.generation,
        )


@pytest.mark.asyncio
async def test_halt_allows_protective_reduce_only_order(event_store) -> None:
    switch = KillSwitch(event_store)
    snapshot = await switch.halt(KillScope.global_scope(), reason="test")
    await switch.assert_submission_allowed(
        market=Market.INDIA,
        symbol="INFY",
        reduce_only=True,
        generation=snapshot.generation,
    )
```

- [ ] **Step 2: Run the tests and confirm the kill switch is absent**

Run: `uv run pytest tests/unit/execution/test_kill_switch.py -v`

Expected: FAIL with missing `execution.kill_switch`.

- [ ] **Step 3: Implement monotonic generation and scope precedence**

Use scopes `GLOBAL`, `MARKET`, and `SYMBOL`. Effective state is the strictest matching state,
ordered `ACTIVE < REDUCING < HALTED < HALTED_UNVERIFIED`. Both HALT and authenticated reactivation
append `KillSwitchGenerationBumped`; reactivation requires `authenticated_localhost=True` and
raises `UnauthorizedStateChange` otherwise. Submission checks reject stale generations first,
then reject non-reduce-only orders under `REDUCING` or stricter states. Reduce-only protective
orders remain allowed unless broker/reconciliation health is unknown, in which case the caller
must reconcile before submission.

```python
async def assert_submission_allowed(
    self, *, market: Market, symbol: str, reduce_only: bool, generation: int
) -> None:
    snapshot = await self.snapshot()
    if generation != snapshot.generation:
        raise StaleGeneration(f"submitted={generation}, current={snapshot.generation}")
    effective = snapshot.effective_state(market=market, symbol=symbol)
    if effective is not KillState.ACTIVE and not reduce_only:
        raise NewExposureBlocked(f"{market}:{symbol} is {effective}")
```

- [ ] **Step 4: Verify state transitions and event replay**

Run: `uv run pytest tests/unit/execution/test_kill_switch.py tests/unit/persistence/test_projections.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/execution tests/unit/execution
git commit -m "feat: add scoped kill switch and worker fencing"
```

### Task 10: Add global cash/risk reservations and separate strategy books

**Files:**
- Create: `src/trading_os/portfolio/__init__.py`
- Create: `src/trading_os/portfolio/reservations.py`
- Create: `src/trading_os/portfolio/strategy_books.py`
- Create: `tests/unit/portfolio/test_reservations.py`
- Create: `tests/unit/portfolio/test_strategy_books.py`

**Interfaces:**
- Consumes: `GlobalPortfolioSnapshot`, `OrderReservationCommitted/Released`, event store, money, and IDs.
- Produces: `ReservationGate.reserve(request)`, `release(reservation_id)`, `StrategyBook`, and deterministic fill/cost attribution.

- [ ] **Step 1: Write concurrent reservation and attribution tests**

```python
# tests/unit/portfolio/test_reservations.py
import asyncio
from decimal import Decimal

import pytest

from trading_os.portfolio.reservations import ReservationGate, ReservationRequest, StaleSnapshot


@pytest.mark.asyncio
async def test_only_one_reservation_commits_against_same_version(event_store, portfolio_snapshot) -> None:
    gate = ReservationGate(event_store)
    request = ReservationRequest(
        snapshot_id=portfolio_snapshot.snapshot_id,
        expected_version=portfolio_snapshot.version,
        cash_inr=Decimal("80000"),
        risk_inr=Decimal("80000"),
    )
    results = await asyncio.gather(
        gate.reserve(request), gate.reserve(request), return_exceptions=True
    )
    assert sum(not isinstance(result, Exception) for result in results) == 1
    assert sum(isinstance(result, StaleSnapshot) for result in results) == 1
```

```python
# tests/unit/portfolio/test_strategy_books.py
from trading_os.portfolio.strategy_books import StrategyBookKind, allocate_fill


def test_fill_costs_are_attributed_to_requested_book(fill, llm_order) -> None:
    allocation = allocate_fill(fill, llm_order)
    assert allocation.book is StrategyBookKind.LLM
    assert allocation.quantity == fill.quantity
    assert allocation.fees == fill.fees
```

- [ ] **Step 2: Run tests and observe missing portfolio services**

Run: `uv run pytest tests/unit/portfolio/test_reservations.py tests/unit/portfolio/test_strategy_books.py -v`

Expected: FAIL with missing modules.

- [ ] **Step 3: Implement CAS reservation and immutable books**

`ReservationGate.reserve()` appends `OrderReservationCommitted` to the single global portfolio
stream with `expected_stream_version=request.expected_version`; `StreamConflict` maps to
`StaleSnapshot`. A reservation contains snapshot ID/version, INR cash, INR risk, symbols,
strategy-book ID, expiry, and status. Release is idempotent by reservation ID and appends exactly
one release event. `GlobalPortfolioSnapshot.version` is defined as the committed global portfolio
stream version, so the snapshot version and reservation CAS version are the same concurrency token.

Create two required book kinds: `LLM` and `RULE_NULL`. Each order carries one book ID. Sim/paper
fills remain fully separated even if symbols overlap. `allocate_fill()` copies quantity, native
notional, fees, and tax amounts into exactly one book; global risk aggregates both books.

```python
async def reserve(self, request: ReservationRequest) -> OrderReservation:
    event = request.to_committed_event()
    try:
        await self._events.append(event, expected_stream_version=request.expected_version)
    except StreamConflict as exc:
        raise StaleSnapshot(str(exc)) from exc
    return OrderReservation.from_request(request)
```

- [ ] **Step 4: Verify concurrency and attribution**

Run: `uv run pytest tests/unit/portfolio/test_reservations.py tests/unit/portfolio/test_strategy_books.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/portfolio tests/unit/portfolio
git commit -m "feat: serialize portfolio reservations and strategy books"
```

### Task 11: Add session and credential readiness gates

**Files:**
- Create: `src/trading_os/control/__init__.py`
- Create: `src/trading_os/control/session_readiness.py`
- Create: `src/trading_os/control/credential_readiness.py`
- Create: `tests/unit/control/test_session_readiness.py`
- Create: `tests/unit/control/test_credential_readiness.py`

**Interfaces:**
- Consumes: `ClockPort`, `CalendarPort`, `SecretsPort`, broker health methods, `KillSwitch`, and notifier.
- Produces: `SessionReady`, `CredentialReady`, and typed `ReadinessFailure` results that gate every cycle and broker/protection job.

- [ ] **Step 1: Write fail-closed readiness tests**

```python
# tests/unit/control/test_session_readiness.py
from datetime import date

from trading_os.control.session_readiness import SessionReadiness
from trading_os.domain.enums import Market


def test_unknown_market_session_fails_closed(frozen_clock, empty_calendar) -> None:
    result = SessionReadiness(frozen_clock, empty_calendar).check(Market.INDIA, date(2026, 11, 8))
    assert result.ready is False
    assert result.reason == "unknown_session"
```

```python
# tests/unit/control/test_credential_readiness.py
import pytest

from trading_os.control.credential_readiness import CredentialReadiness


@pytest.mark.asyncio
async def test_kite_403_halts_new_exposure_without_retry(kite_403_transport, kill_switch, notifier) -> None:
    result = await CredentialReadiness(kite_403_transport, kill_switch, notifier).check()
    assert result.ready is False
    assert kite_403_transport.calls == 1
    assert (await kill_switch.snapshot()).blocks_new_exposure is True
```

- [ ] **Step 2: Run and observe missing readiness gates**

Run: `uv run pytest tests/unit/control/test_session_readiness.py tests/unit/control/test_credential_readiness.py -v`

Expected: FAIL with missing control modules.

- [ ] **Step 3: Implement explicit readiness results**

`SessionReadiness.check()` returns ready only if a versioned calendar entry exists, the observed
session close is present, current time is after that close, and the entry is not marked ambiguous.
The calendar DTO includes market, exchange date, UTC open/close, calendar version, and exceptional
session kind, covering DST and Muhurat without local-time arithmetic.

`CredentialReadiness.check()` performs exactly one read-only broker authentication probe. A Kite
403/`TokenException` appends an operational failure, moves the relevant market to REDUCING or
HALTED according to whether broker custody can still be reconciled, notifies HITL, and returns
`reauth_required=True`. It never retries 403. Resume requires successful re-authentication followed
by broker positions/orders/protection reconciliation.

```python
def check(self, market: Market, trade_date: date) -> ReadinessResult:
    session = self._calendar.session(market, trade_date)
    if session is None or session.ambiguous:
        return ReadinessResult(ready=False, reason="unknown_session")
    if session.observed_close_at is None or self._clock.now() < session.observed_close_at:
        return ReadinessResult(ready=False, reason="session_not_closed")
    return ReadinessResult(ready=True, reason="ready")
```

- [ ] **Step 4: Verify fail-closed behavior**

Run: `uv run pytest tests/unit/control/test_session_readiness.py tests/unit/control/test_credential_readiness.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/control tests/unit/control
git commit -m "feat: gate cycles on session and credential readiness"
```

---

## Milestone 2 — Validated Data, Signals, Causal KG, and Slow Research

### Task 12: Model raw bars, corporate actions, universes, and cash events

**Files:**
- Create: `src/trading_os/data/__init__.py`
- Create: `src/trading_os/data/models.py`
- Create: `src/trading_os/data/corporate_actions.py`
- Create: `src/trading_os/data/universe.py`
- Create: `src/trading_os/data/cash_events.py`
- Create: `tests/unit/data/test_corporate_actions.py`
- Create: `tests/unit/data/test_universe.py`
- Create: `tests/unit/data/test_cash_events.py`

**Interfaces:**
- Consumes: fixed-point values, market/currency enums, and market-data/security-master ports.
- Produces: immutable `RawBar`, three-series `AdjustedBarSet`, `CorporateAction`, `UniverseMembership`, `BrokerCashEvent`, and their validation functions.

- [ ] **Step 1: Write data-correctness tests**

```python
# tests/unit/data/test_corporate_actions.py
from trading_os.data.corporate_actions import apply_split


def test_split_adjustment_changes_price_and_volume_reciprocally(raw_bar, two_for_one_split) -> None:
    adjusted = apply_split(raw_bar, two_for_one_split)
    assert adjusted.close == raw_bar.close / 2
    assert adjusted.volume == raw_bar.volume * 2
```

```python
# tests/unit/data/test_universe.py
from trading_os.data.universe import membership_as_of


def test_delisted_symbol_is_absent_after_delisting(membership_history) -> None:
    assert "OLDCO" in membership_as_of(membership_history, "2025-01-31")
    assert "OLDCO" not in membership_as_of(membership_history, "2025-02-28")
```

```python
# tests/unit/data/test_cash_events.py
from trading_os.data.cash_events import CashEventKind, normalize_cash_event


def test_us_dividend_opens_idle_fx_eligible_credit(raw_us_dividend) -> None:
    event = normalize_cash_event(raw_us_dividend)
    assert event.kind is CashEventKind.DIVIDEND
    assert event.opens_idle_fx_lot is True
    assert event.gross_amount.amount > event.withholding.amount
```

- [ ] **Step 2: Run and confirm data modules are absent**

Run: `uv run pytest tests/unit/data/test_corporate_actions.py tests/unit/data/test_universe.py tests/unit/data/test_cash_events.py -v`

Expected: FAIL on missing data modules.

- [ ] **Step 3: Implement immutable source and normalized data models**

Every record includes source, source record ID, publication/received time, effective date, as-of
time, content hash, and market. Store raw, split/bonus-adjusted, and total-return series separately;
never overwrite raw bars. CA types cover split, bonus, dividend, rights, merger, symbol change,
delisting, and cash-in-lieu. Universe history uses half-open `[valid_from, valid_to)` intervals.
Cash events cover dividend, withholding, interest, fee, reversal, remittance, repatriation, and
cash-in-lieu with gross/net components and broker transaction ID.

```python
def apply_split(bar: RawBar, action: CorporateAction) -> AdjustedBar:
    ratio = action.new_shares / action.old_shares
    return AdjustedBar(
        source_bar_hash=bar.content_hash,
        open=bar.open / ratio,
        high=bar.high / ratio,
        low=bar.low / ratio,
        close=bar.close / ratio,
        volume=bar.volume * ratio,
    )
```

- [ ] **Step 4: Verify deterministic normalization**

Run: `uv run pytest tests/unit/data -v && uv run mypy src/trading_os/data`

Expected: all tests PASS and mypy exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/data tests/unit/data
git commit -m "feat: model corporate actions universes and cash events"
```

### Task 13: Seal content-addressed validated data snapshots

**Files:**
- Create: `src/trading_os/data/snapshot.py`
- Create: `src/trading_os/data/correctness.py`
- Create: `src/trading_os/domain/data_snapshot.py`
- Create: `tests/unit/data/test_snapshot.py`
- Create: `tests/unit/data/test_correctness.py`

**Interfaces:**
- Consumes: normalized data from Task 12, calendar/FX/KG versions, and enabled-signal config.
- Produces: `ValidatedDataSnapshotId`, immutable `ValidatedDataSnapshotManifest`, `DataFault`, and `CorrectnessLayer.validate_and_seal(inputs)`.

- [ ] **Step 1: Write hash stability and fail-closed tests**

```python
# tests/unit/data/test_snapshot.py
from trading_os.data.snapshot import canonical_snapshot_hash


def test_snapshot_hash_is_order_independent(valid_manifest) -> None:
    reordered = valid_manifest.model_copy(
        update={"component_hashes": dict(reversed(tuple(valid_manifest.component_hashes.items())))}
    )
    assert canonical_snapshot_hash(valid_manifest) == canonical_snapshot_hash(reordered)
```

```python
# tests/unit/data/test_correctness.py
from trading_os.data.correctness import CorrectnessLayer, DataFaultKind


def test_future_dated_ca_invalidates_snapshot(valid_inputs, future_corporate_action) -> None:
    inputs = valid_inputs.with_corporate_action(future_corporate_action)
    result = CorrectnessLayer().validate_and_seal(inputs)
    assert result.snapshot is None
    assert DataFaultKind.FUTURE_DATED_COMPONENT in {fault.kind for fault in result.faults}


def test_quality_stays_disabled_without_valid_pit_panel(valid_inputs) -> None:
    result = CorrectnessLayer().validate_and_seal(valid_inputs)
    assert result.snapshot is not None
    assert result.snapshot.enabled_signals["quality"] is False
```

- [ ] **Step 2: Run tests and observe missing snapshot boundary**

Run: `uv run pytest tests/unit/data/test_snapshot.py tests/unit/data/test_correctness.py -v`

Expected: FAIL with missing snapshot/correctness modules.

- [ ] **Step 3: Implement canonical sealing and typed validity**

Canonicalize the manifest using sorted-key ORJSON and SHA-256. The manifest includes hashes and
versions for raw/split-adjusted/total-return OHLCV, CA/dividend/delisting ledger, PIT universe,
calendar, news cutoff, KG edge set, FX rate records, and enabled signals with per-factor series
binding. `CorrectnessLayer` rejects missing required components, stale components beyond their
declared maximum age, future publication/as-of dates, post-seal revisions, non-PIT membership,
unknown calendars, and unavailable Rule-115/live FX records for the US sleeve.

Expose data to downstream code only through a repository method requiring the exact
`ValidatedDataSnapshotId`; do not implement a no-argument `latest()` method.

```python
def canonical_snapshot_hash(manifest: ValidatedDataSnapshotManifest) -> ValidatedDataSnapshotId:
    canonical = orjson.dumps(manifest.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS)
    return ValidatedDataSnapshotId(value=hashlib.sha256(canonical).hexdigest())
```

- [ ] **Step 4: Verify the immutable gate**

Run: `uv run pytest tests/unit/data/test_snapshot.py tests/unit/data/test_correctness.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/data src/trading_os/domain/data_snapshot.py tests/unit/data
git commit -m "feat: seal validated content-addressed data snapshots"
```

### Task 14: Implement deterministic factor signals and the independent rule-null

**Files:**
- Create: `src/trading_os/signals/__init__.py`
- Create: `src/trading_os/signals/momentum.py`
- Create: `src/trading_os/signals/trend.py`
- Create: `src/trading_os/signals/regime.py`
- Create: `src/trading_os/signals/regime_fit.py`
- Create: `src/trading_os/signals/gate_rank.py`
- Create: `src/trading_os/signals/rule_null.py`
- Create: `config/signals/paper_v1.yaml`
- Create: `tests/unit/signals/test_factors.py`
- Create: `tests/unit/signals/test_gate_rank.py`
- Create: `tests/unit/signals/test_rule_null.py`

**Interfaces:**
- Consumes: `ValidatedDataSnapshotId`, snapshot-scoped series repository, deterministic signal config, `HotPathCandidate`, and read-only calibration summaries for gate/rank only.
- Produces: `FactorScore`, `RegimeState`, `AdmittedCandidate`, `GateRank.rank()`, and `RuleNullJob.run()`.

- [ ] **Step 1: Write factor and independence tests**

```python
# tests/unit/signals/test_factors.py
from trading_os.signals.momentum import twelve_minus_one_momentum


def test_twelve_minus_one_excludes_most_recent_month(monthly_total_returns) -> None:
    score = twelve_minus_one_momentum(monthly_total_returns)
    assert score == monthly_total_returns.iloc[-12:-1].add(1).prod() - 1
```

```python
# tests/unit/signals/test_rule_null.py
import inspect

from trading_os.signals.rule_null import RuleNullJob


def test_rule_null_constructor_has_no_llm_or_kg_dependencies() -> None:
    parameters = set(inspect.signature(RuleNullJob).parameters)
    forbidden = {"llm", "thesis", "graph", "traversal", "calibration"}
    assert parameters.isdisjoint(forbidden)
```

```python
# tests/unit/signals/test_gate_rank.py
from trading_os.signals.gate_rank import GateRank


def test_conviction_changes_order_not_candidate_size(high_and_low_candidates) -> None:
    ranked = GateRank().rank(high_and_low_candidates)
    assert ranked[0].conviction_band.value == "high"
    assert all(not hasattr(item, "quantity") for item in ranked)
```

- [ ] **Step 2: Run tests and confirm signals are absent**

Run: `uv run pytest tests/unit/signals -v`

Expected: FAIL with missing signal modules.

- [ ] **Step 3: Implement the 3-factor null and gate/rank**

`config/signals/paper_v1.yaml` freezes `momentum_lookback_months: 12`,
`momentum_skip_recent_months: 1`, `trend_sma_days: 200`, `regime_states: 2`,
`regime_training_days: 1260`, `regime_refit_cadence: monthly`, and `quality_enabled: false`.
Momentum uses total-return monthly observations. Trend uses split-adjusted close. `regime_fit.py`
fits the two-state HMM only from observations at or before the artifact cutoff and writes a versioned
parameter artifact with a training-data hash; runtime inference never refits. Quality remains absent
until the snapshot manifest enables it. `RuleNullJob` accepts exactly snapshot ID, deterministic
signal config, and deterministic portfolio state and emits admitted candidates; it imports no
research, KG, LLM, or calibration module. `GateRank` may veto a mature poorly performing conviction
bucket at N>=30 or sort by band, but returns no quantity or numeric multiplier.

```python
def twelve_minus_one_momentum(monthly_total_returns: pd.Series) -> Decimal:
    window = monthly_total_returns.iloc[-12:-1]
    return Decimal(str(window.add(1).prod() - 1))


def trend_signal(split_adjusted_close: pd.Series, days: int = 200) -> bool:
    return bool(split_adjusted_close.iloc[-1] > split_adjusted_close.iloc[-days:].mean())
```

- [ ] **Step 4: Verify factors and module independence**

Run: `uv run pytest tests/unit/signals -v && uv run mypy src/trading_os/signals`

Expected: all tests PASS and mypy exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/signals config/signals/paper_v1.yaml tests/unit/signals
git commit -m "feat: add deterministic factors and independent rule null"
```

### Task 15: Enforce causal-KG edge admission and deterministic confidence

**Files:**
- Create: `src/trading_os/kg/__init__.py`
- Create: `src/trading_os/kg/models.py`
- Create: `src/trading_os/kg/admission.py`
- Create: `src/trading_os/kg/neo4j_store.py`
- Create: `tests/unit/kg/test_admission.py`
- Create: `tests/contract/kg/test_graph_store.py`

**Interfaces:**
- Consumes: `GraphStorePort`, clock, citations, source metadata, and human approval decisions.
- Produces: `EdgeProposal`, `AdmittedEdge`, deterministic `EvidenceConfidence`, `EdgeAdmissionPolicy.evaluate()`, and `Neo4jGraphStore`.

- [ ] **Step 1: Write all six admission-gate tests**

```python
# tests/unit/kg/test_admission.py
import pytest

from trading_os.kg.admission import EdgeAdmissionPolicy, RejectionReason


@pytest.mark.parametrize(
    ("proposal_fixture", "reason"),
    [
        ("without_human_approval", RejectionReason.NOT_APPROVED),
        ("without_provenance", RejectionReason.MISSING_PROVENANCE),
        ("high_confidence_one_source", RejectionReason.INSUFFICIENT_CORROBORATION),
        ("precision_below_bar", RejectionReason.AUTHOR_PRECISION_BELOW_BAR),
        ("future_dated", RejectionReason.FUTURE_DATED),
        ("stale_not_deprecated", RejectionReason.STALE),
    ],
)
def test_edge_requires_every_admission_gate(request, proposal_fixture, reason) -> None:
    proposal = request.getfixturevalue(proposal_fixture)
    result = EdgeAdmissionPolicy().evaluate(proposal)
    assert result.rejection_reason is reason
```

```python
def test_llm_proposal_cannot_supply_numeric_confidence(valid_edge_payload) -> None:
    valid_edge_payload["confidence"] = 0.9
    with pytest.raises(ValidationError):
        EdgeProposal.model_validate(valid_edge_payload)
```

- [ ] **Step 2: Run and confirm KG modules are absent**

Run: `uv run pytest tests/unit/kg/test_admission.py -v`

Expected: FAIL with missing KG modules.

- [ ] **Step 3: Implement proposal/admission types and Neo4j mapping**

`EdgeProposal` contains source node, target node, relation, citations, source metadata,
`valid_from`, `last_confirmed`, author model/version, and human decision—never a numeric weight or
confidence. `EvidenceConfidence` is computed by a versioned table from independent source count,
source class, age, admission state, and measured author precision. Cap confidence at 0.5 until a
second independent source exists. Apply approximately 30% annual decay to unconfirmed edges and
require explicit deprecation once the stale threshold is crossed. Neo4j writes only `AdmittedEdge`
records and includes valid-time fields and content hashes.

```python
def evidence_confidence(metadata: EvidenceMetadata, as_of: date) -> Decimal:
    base = SOURCE_CLASS_WEIGHT[metadata.strongest_source_class]
    corroboration_cap = Decimal("1") if metadata.independent_source_count >= 2 else Decimal("0.5")
    age_years = Decimal((as_of - metadata.last_confirmed).days) / Decimal("365.25")
    decay = Decimal("0.70") ** age_years
    return min(base * decay, corroboration_cap)
```

- [ ] **Step 4: Verify gates and graph-store contract with a test container**

Run: `uv run pytest tests/unit/kg/test_admission.py -v`

Run: `docker compose up -d neo4j && uv run pytest tests/contract/kg/test_graph_store.py -v`

Expected: both suites PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/kg tests/unit/kg tests/contract/kg
git commit -m "feat: enforce causal graph edge admission gates"
```

### Task 16: Implement deterministic causal traversal and fitted-weight artifacts

**Files:**
- Create: `src/trading_os/kg/traversal.py`
- Create: `src/trading_os/kg/weights.py`
- Create: `config/kg_weight_rungs.yaml`
- Create: `tests/unit/kg/test_traversal.py`
- Create: `tests/unit/kg/test_weights.py`

**Interfaces:**
- Consumes: `MacroEventLabel`, admitted graph version, deterministic confidence, fitted weight artifact, and snapshot as-of date.
- Produces: `ExposureVector`, audited contributing paths, `EdgeWeightFitter.fit()`, and deterministic `Traversal.compute()`.

- [ ] **Step 1: Write look-ahead, hub, and tighten-only tests**

```python
# tests/unit/kg/test_traversal.py
from trading_os.kg.traversal import Traversal


def test_future_dated_edge_never_enters_vector(graph_with_planted_future_edge, macro_event) -> None:
    result = Traversal().compute(graph_with_planted_future_edge, macro_event)
    assert "FUTURECO" not in result.by_symbol


def test_hub_penalty_prevents_every_symbol_from_receiving_exposure(hub_graph, macro_event) -> None:
    result = Traversal().compute(hub_graph, macro_event)
    assert len(result.by_symbol) < len(hub_graph.company_nodes)


def test_stronger_llm_ordinal_can_only_tighten_exposure(base_graph, weak_event, strong_event) -> None:
    weak = Traversal().compute(base_graph, weak_event)
    strong = Traversal().compute(base_graph, strong_event)
    assert strong.max_allowed_exposure <= weak.max_allowed_exposure
```

- [ ] **Step 2: Run tests and observe missing traversal**

Run: `uv run pytest tests/unit/kg/test_traversal.py tests/unit/kg/test_weights.py -v`

Expected: FAIL with missing traversal/weight modules.

- [ ] **Step 3: Implement rule-admissible traversal**

Use an explicit motif registry, not free graph walks. Score paths from admitted edges using
deterministic evidence confidence, offline-fitted structural weight, `beta ** hops`,
`gamma ** age_days`, and inverse-degree anti-hub penalty. Reject depth >3 and edges whose
`valid_from` exceeds the snapshot as-of date. The LLM magnitude/confidence ordinals map through
the frozen `config/kg_weight_rungs.yaml` only to multipliers in `(0, 1]`; they can tighten but
never inflate base exposure. Emit per-symbol exposure and top contributing paths for audit.

`EdgeWeightFitter` accepts labeled historical shocks and returns a versioned artifact containing
driver class, coefficient, uncertainty, training cutoff, dataset hash, and code version. Its API
does not accept a price-correlation matrix.

```python
def path_score(path: AdmissiblePath, *, beta: Decimal, gamma: Decimal, as_of: date) -> Decimal:
    edge_confidence = math.prod(edge.evidence_confidence for edge in path.edges)
    structural_weight = math.prod(edge.structural_weight for edge in path.edges)
    age_days = max((as_of - edge.last_confirmed).days for edge in path.edges)
    anti_hub = Decimal("1") / Decimal(max(path.maximum_node_degree, 1))
    return edge_confidence * structural_weight * (beta ** path.hops) * (gamma ** age_days) * anti_hub
```

- [ ] **Step 4: Verify deterministic vector output**

Run: `uv run pytest tests/unit/kg/test_traversal.py tests/unit/kg/test_weights.py -v`

Expected: all tests PASS, including identical serialized output across two runs.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/kg config/kg_weight_rungs.yaml tests/unit/kg
git commit -m "feat: compute deterministic causal exposure vectors"
```

### Task 17: Add swappable LLM roles, analysts, and on-cadence synthesis

**Files:**
- Create: `src/trading_os/research/llm_role.py`
- Create: `src/trading_os/research/analyst.py`
- Create: `src/trading_os/research/macro_analyst.py`
- Create: `src/trading_os/research/synthesizer.py`
- Create: `src/trading_os/research/meta_analyst.py`
- Create: `src/trading_os/research/cadence.py`
- Create: `tests/unit/research/test_llm_role.py`
- Create: `tests/unit/research/test_macro_analyst.py`
- Create: `tests/unit/research/test_cadence.py`

**Interfaces:**
- Consumes: `LLMRolePort`, strict research schemas, vetted feed snapshot, and calendar/cadence config.
- Produces: `AnalystReport`, categorical/ordinal `MacroEventLabel`, `ResearchTradeThesis`, provider-quorum result, and cached `ResearchRun`.

- [ ] **Step 1: Write schema, quorum, and cadence tests**

```python
# tests/unit/research/test_macro_analyst.py
import pytest
from pydantic import ValidationError

from trading_os.research.macro_analyst import MacroEventLabel


def test_macro_event_rejects_numeric_confidence() -> None:
    with pytest.raises(ValidationError):
        MacroEventLabel.model_validate(
            {"driver": "oil", "source": "supply", "phase": "act", "direction": "+", "confidence": 0.9}
        )
```

```python
# tests/unit/research/test_cadence.py
from trading_os.research.cadence import DecisionCadence


def test_event_refresh_cannot_authorize_off_cadence_trade(monthly_cadence) -> None:
    result = DecisionCadence(monthly_cadence).evaluate(event_triggered=True, rebalance_due=False)
    assert result.refresh_labels is True
    assert result.may_trade is False
```

- [ ] **Step 2: Run and observe missing role orchestration**

Run: `uv run pytest tests/unit/research -v`

Expected: FAIL on missing new research modules.

- [ ] **Step 3: Implement role-keyed structured invocation**

`LLMRole.invoke(role, prompt, schema)` delegates to a configured provider and validates with the
exact Pydantic schema using `extra="forbid"`. Store provider, model, prompt hash, schema version,
request/response content hashes, and latency as slow-plane events. Analysts emit only structured
reports. The concrete `NewsMacroAnalyst` emits `MacroEventLabel` with closed
driver/source/phase/direction enums plus LOW/MED/HIGH and WEAK/MODERATE/STRONG ordinals—no scalar
confidence/magnitude. `MoASynthesizer` emits the existing `ResearchTradeThesis`. `MetaAnalyst`
emits only the Task-15 `EdgeProposal` endpoints, relation, and citations into the human review queue;
it cannot represent a numeric edge weight/confidence or write directly to `GraphStore`. Quorum policy
distinguishes an optional analyst failure from synthesizer failure and records a deterministic capped
conviction band when diversity falls below its floor.

`DecisionCadence` permits label/rationale refresh on event triggers but produces `may_trade=True`
only when the slowest active signal's rebalance window is due.

```python
from typing import TypeVar

from pydantic import BaseModel


TModel = TypeVar("TModel", bound=BaseModel)


class LLMRole:
    def __init__(self, providers: Mapping[str, StructuredProvider]) -> None:
        self._providers = providers

    async def invoke(self, role: str, prompt: str, schema: type[TModel]) -> TModel:
        raw = await self._providers[role].invoke(prompt=prompt, schema=schema.model_json_schema())
        return schema.model_validate(raw)
```

- [ ] **Step 4: Verify provider swapping and containment**

Run: `uv run pytest tests/unit/research -v && uv run mypy src/trading_os/research`

Expected: all tests PASS and mypy exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/research tests/unit/research
git commit -m "feat: add structured on-cadence llm research path"
```

---

## Milestone 3 — Deterministic Decisioning and Protected Paper Execution

### Task 18: Implement conviction-blind fixed-fractional sizing

**Files:**
- Create: `src/trading_os/portfolio/sizing.py`
- Create: `config/risk/paper_v1.yaml`
- Create: `tests/unit/portfolio/test_sizing.py`
- Create: `tests/unit/portfolio/test_sizing_properties.py`

**Interfaces:**
- Consumes: admitted symbol/direction, account equity, deterministic volatility/stop distance, venue precision, and `SizingConfig`.
- Produces: `TargetPosition` and `Sizer.size(request)`; no thesis, conviction, calibration, LLM, or KG input exists in the signature.

- [ ] **Step 1: Write formula and seam property tests**

```python
# tests/unit/portfolio/test_sizing.py
from decimal import Decimal

from trading_os.portfolio.sizing import Sizer, SizingRequest


def test_fixed_fractional_size_is_floored_to_venue_precision() -> None:
    request = SizingRequest.example(
        account_equity_inr=Decimal("100000"),
        risk_fraction=Decimal("0.01"),
        stop_distance_inr=Decimal("125"),
        vol_multiplier=Decimal("0.80"),
        quantity_step=Decimal("1"),
    )
    assert Sizer().size(request).quantity.value == Decimal("6")
```

```python
# tests/unit/portfolio/test_sizing_properties.py
import inspect

from hypothesis import given, strategies as st

from trading_os.portfolio.sizing import Sizer, SizingRequest


def test_sizer_signature_cannot_accept_llm_values() -> None:
    fields = set(SizingRequest.model_fields)
    forbidden = {"conviction", "thesis", "model", "prompt", "calibration", "rationale"}
    assert fields.isdisjoint(forbidden)


@given(st.decimals(min_value="0.001", max_value="0.02", places=3))
def test_quantity_never_exceeds_account_risk(risk_fraction) -> None:
    request = SizingRequest.safe_example(risk_fraction=risk_fraction)
    target = Sizer().size(request)
    assert target.quantity.value * request.stop_distance_inr <= request.account_equity_inr * risk_fraction
```

- [ ] **Step 2: Run and observe missing sizing module**

Run: `uv run pytest tests/unit/portfolio/test_sizing.py tests/unit/portfolio/test_sizing_properties.py -v`

Expected: FAIL with missing `portfolio.sizing`.

- [ ] **Step 3: Implement deterministic size arithmetic**

`config/risk/paper_v1.yaml` freezes the first paper campaign at `risk_fraction: 0.01`,
`annual_vol_target: 0.10`, `max_position_fraction: 0.10`, `max_cluster_fraction: 0.25`,
`var_confidence: 0.95`, `cvar_confidence: 0.95`, `max_live_fx_age_seconds: 900`,
`disconnect_halt_seconds: 15`, and drawdown bands `soft_alert: -0.08`,
`reducing: -0.15`, `halted: -0.25`. Compute
`raw_risk_budget = account_equity_inr * risk_fraction * vol_multiplier`, then
`raw_quantity = raw_risk_budget / stop_distance_inr`. Apply hard per-position notional cap,
available settled-cash cap, and venue quantity precision by flooring, never rounding up. Reject
non-positive prices, stops, vol inputs, or account equity. After rounding, recompute actual risk and
return both requested and realized risk in `TargetPosition`. Keep the 1–2% range in config; use 1%
as the safe default until the frozen promotion manifest selects a value.

```python
def size(self, request: SizingRequest) -> TargetPosition:
    budget = request.account_equity_inr * request.risk_fraction * request.vol_multiplier
    raw = min(
        budget / request.stop_distance_inr,
        request.position_notional_cap_inr / request.entry_price_inr,
        request.settled_cash_inr / request.entry_price_inr,
    )
    quantity = (raw // request.quantity_step) * request.quantity_step
    return TargetPosition(
        quantity=Quantity(value=quantity),
        actual_risk_inr=quantity * request.stop_distance_inr,
    )
```

- [ ] **Step 4: Verify sizing and property tests**

Run: `uv run pytest tests/unit/portfolio/test_sizing.py tests/unit/portfolio/test_sizing_properties.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/portfolio/sizing.py config/risk/paper_v1.yaml tests/unit/portfolio/test_sizing.py tests/unit/portfolio/test_sizing_properties.py
git commit -m "feat: add deterministic fixed-fractional sizing"
```

### Task 19: Implement INR-numeraire portfolio risk and tighten-only KG overlays

**Files:**
- Create: `src/trading_os/portfolio/risk.py`
- Create: `src/trading_os/portfolio/covariance.py`
- Create: `tests/unit/portfolio/test_risk.py`
- Create: `tests/unit/portfolio/test_covariance.py`

**Interfaces:**
- Consumes: `TargetPosition`, global portfolio snapshot, live FX rate records, daily return matrix, deterministic cluster map, `ExposureVector`, and risk config.
- Produces: `RiskDecision{approved_target, reasons, metrics}` and common-INR VaR/CVaR/cluster exposure.

- [ ] **Step 1: Write common-numeraire and tighten-only tests**

```python
# tests/unit/portfolio/test_risk.py
from trading_os.portfolio.risk import RiskEngine


def test_defensive_overlay_can_shrink_but_never_inflate(base_risk_request, defensive_vector) -> None:
    baseline = RiskEngine().evaluate(base_risk_request.without_exposure_vector())
    defended = RiskEngine().evaluate(base_risk_request.with_exposure_vector(defensive_vector))
    assert defended.approved_target.quantity.value <= baseline.approved_target.quantity.value


def test_cluster_cap_includes_both_markets_and_pending_orders(cross_market_risk_request) -> None:
    decision = RiskEngine().evaluate(cross_market_risk_request)
    assert decision.approved is False
    assert "cluster_cap" in decision.reasons
```

```python
# tests/unit/portfolio/test_covariance.py
from trading_os.portfolio.covariance import inr_returns


def test_us_returns_include_fx_move_without_changing_accounting_ledger(usd_returns, fx_returns) -> None:
    converted = inr_returns(usd_returns, fx_returns)
    assert converted.equals((1 + usd_returns) * (1 + fx_returns) - 1)
```

- [ ] **Step 2: Run tests and confirm risk engine is absent**

Run: `uv run pytest tests/unit/portfolio/test_risk.py tests/unit/portfolio/test_covariance.py -v`

Expected: FAIL with missing risk modules.

- [ ] **Step 3: Implement deterministic risk evaluation**

Convert US sleeve returns and exposures to INR using pinned live-rate records. Calculate historical
VaR/CVaR at configured levels, drawdown, gross per-position exposure, and correlation-cluster
exposure across positions plus pending orders in both strategy books. Reject stale FX records.
Apply exposure-vector multipliers only through `min(Decimal("1"), multiplier)` and include the
applied graph/weight/rung versions in audit metrics. Risk may shrink or veto; it cannot increase the
Sizer target. Return a new rounded target and require compliance to rerun after risk rounding.

```python
def apply_defensive_tilt(target: TargetPosition, multiplier: Decimal) -> TargetPosition:
    safe_multiplier = min(Decimal("1"), max(Decimal("0"), multiplier))
    return target.with_quantity_floor(target.quantity.value * safe_multiplier)


def inr_returns(asset_returns_usd: pd.Series, usd_inr_returns: pd.Series) -> pd.Series:
    return (1 + asset_returns_usd) * (1 + usd_inr_returns) - 1
```

- [ ] **Step 4: Verify common-INR and cap behavior**

Run: `uv run pytest tests/unit/portfolio/test_risk.py tests/unit/portfolio/test_covariance.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/portfolio/risk.py src/trading_os/portfolio/covariance.py tests/unit/portfolio
git commit -m "feat: enforce common-inr portfolio risk caps"
```

### Task 20: Implement India pre-order compliance rules

**Files:**
- Create: `src/trading_os/compliance/__init__.py`
- Create: `src/trading_os/compliance/models.py`
- Create: `src/trading_os/compliance/india.py`
- Create: `config/compliance/india.yaml`
- Create: `tests/unit/compliance/test_india.py`

**Interfaces:**
- Consumes: canonical order, account/holding state, current egress IP evidence, cadence history, algo-tag metadata, and versioned India rules.
- Produces: `ComplianceDecision`, rule IDs, evidence hashes, and `IndiaComplianceGate.evaluate()`.

- [ ] **Step 1: Write one test per locked India rule**

```python
# tests/unit/compliance/test_india.py
import pytest

from trading_os.compliance.india import IndiaComplianceGate


@pytest.mark.parametrize(
    ("mutation", "rule_id"),
    [
        ("unlisted_owner", "IN-OWNER-001"),
        ("wrong_egress_ip", "IN-IP-001"),
        ("missing_algo_tag", "IN-ALGO-001"),
        ("ops_above_internal_cap", "IN-OPS-001"),
        ("off_cadence", "IN-CADENCE-001"),
        ("sell_above_settled_holding", "IN-CNC-001"),
        ("missing_ddpi", "IN-DDPI-001"),
        ("unprotected_market_order", "IN-PRICE-001"),
    ],
)
def test_india_rule_rejects(request, compliant_india_context, mutation, rule_id) -> None:
    context = request.getfixturevalue(mutation)(compliant_india_context)
    decision = IndiaComplianceGate.from_config().evaluate(context)
    assert decision.approved is False
    assert rule_id in decision.failed_rule_ids
```

- [ ] **Step 2: Run and observe missing India gate**

Run: `uv run pytest tests/unit/compliance/test_india.py -v`

Expected: FAIL with missing compliance modules.

- [ ] **Step 3: Implement versioned deterministic rules**

Load `config/compliance/india.yaml` into a frozen `IndiaRules` model containing effective date,
registered IPs, internal OPS cap of 2/s, account owner allowlist, algo-tag requirement, audit
retention years, and price-protection bounds. Evaluate rules in a stable order and collect all
failures without short-circuiting. The gate requires long-delivery/CNC, settled demat holdings for
sells, current DDPI capability, an exchange-issued broker-provisioned tag, and the slowest-signal
cadence proof. Record rule version and evidence hashes; never record TPIN or secret material.

```python
def evaluate(self, context: IndiaOrderContext) -> ComplianceDecision:
    failures = tuple(rule.rule_id for rule in self._rules if not rule.passes(context))
    return ComplianceDecision(
        approved=not failures,
        failed_rule_ids=failures,
        rules_version=self._rules_version,
        evidence_hash=context.evidence_hash,
    )
```

- [ ] **Step 4: Verify every India rule**

Run: `uv run pytest tests/unit/compliance/test_india.py -v`

Expected: all parameterized cases PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/compliance config/compliance/india.yaml tests/unit/compliance
git commit -m "feat: enforce india pre-order compliance"
```

### Task 21: Implement US security, LRS, residency, and idle-FX compliance

**Files:**
- Create: `src/trading_os/compliance/us.py`
- Create: `src/trading_os/compliance/lrs.py`
- Create: `src/trading_os/compliance/idle_fx.py`
- Create: `config/compliance/us.yaml`
- Create: `tests/unit/compliance/test_us.py`
- Create: `tests/unit/compliance/test_lrs.py`
- Create: `tests/unit/compliance/test_idle_fx.py`

**Interfaces:**
- Consumes: security-master classification, cash-account flags, settled cash, residency attestation, PAN-wide remittance state, and idle-FX lots.
- Produces: `USComplianceGate`, `PreRemittanceGate`, `IdleFxDispositionPolicy`, and deterministic compliance decisions.

- [ ] **Step 1: Write security and PAN-wide LRS tests**

```python
# tests/unit/compliance/test_us.py
import pytest

from trading_os.compliance.us import USComplianceGate


@pytest.mark.parametrize(
    "classification",
    ["margin_account", "short_order", "option", "crypto", "leveraged_etf",
     "inverse_etf", "commodity_etf", "synthetic_etf", "indian_issuer_adr"],
)
def test_prohibited_us_exposure_is_rejected(classification, us_context_factory) -> None:
    decision = USComplianceGate.from_config().evaluate(us_context_factory(classification))
    assert decision.approved is False
```

```python
# tests/unit/compliance/test_lrs.py
from decimal import Decimal

from trading_os.compliance.lrs import PreRemittanceGate


def test_external_bank_usage_is_included_in_pan_meter(lrs_context) -> None:
    context = lrs_context.with_usage(local_usd=Decimal("20000"), external_usd=Decimal("230000"))
    decision = PreRemittanceGate().evaluate(context, proposed_usd=Decimal("1000"))
    assert decision.approved is False


def test_stale_external_lrs_state_fails_closed(stale_lrs_context) -> None:
    assert PreRemittanceGate().evaluate(stale_lrs_context, proposed_usd=Decimal("1")).approved is False
```

```python
# tests/unit/compliance/test_idle_fx.py
from datetime import timedelta

from trading_os.compliance.idle_fx import IdleFxDispositionPolicy


def test_day_175_requires_disposition_not_just_alert(idle_fx_lot, frozen_clock) -> None:
    frozen_clock.advance(timedelta(days=175))
    action = IdleFxDispositionPolicy(frozen_clock).evaluate(idle_fx_lot)
    assert action.requires_confirmed_disposition is True
    assert action.allowed_outcomes == {"reinvested_opi", "repatriated"}
```

- [ ] **Step 2: Run and observe missing US/LRS modules**

Run: `uv run pytest tests/unit/compliance/test_us.py tests/unit/compliance/test_lrs.py tests/unit/compliance/test_idle_fx.py -v`

Expected: FAIL with missing modules.

- [ ] **Step 3: Implement staged US compliance**

`USComplianceGate` permits only long, fully paid, US-listed common stock and qualifying >50%-equity
non-leveraged/non-inverse/non-commodity/non-synthetic ETFs in a contractually cash account with
settled cash. It rejects Indian-company securities listed abroad and stale/unknown security-master
classification. Residency attestation must be current and must say resident-and-ordinarily-resident
India, not NRI/RNOR/US-tax-resident.

`PreRemittanceGate` sums current-FY gross outward remittances across local and externally attested
banks/purposes, never subtracts repatriation, hard-stops before USD 250,000, and warns at 80% and the
date-versioned INR 10 lakh TCS threshold. Unknown/stale external state fails closed. Record designated
AD bank, Form A2, and S0001 evidence.

Each realized USD credit opens an `IdleFxLot` with value date, deadline, original/remaining amount,
and source event. Consumption uses frozen FIFO unless the written legal opinion changes the config.
At the operational deadline it requires broker/bank-confirmed `reinvested_opi` or `repatriated`.
Cash sweep is treated as idle. The service never forces a speculative trade.

```python
def evaluate(self, context: LrsContext, proposed_usd: Decimal) -> ComplianceDecision:
    if context.external_state_age > context.maximum_external_state_age:
        return ComplianceDecision.reject("US-LRS-STALE-001")
    cumulative = context.local_gross_usd + context.external_gross_usd + proposed_usd
    if cumulative > Decimal("250000"):
        return ComplianceDecision.reject("US-LRS-CAP-001")
    return ComplianceDecision.approve(warnings=context.threshold_warnings(cumulative))
```

- [ ] **Step 4: Verify US and LRS gates**

Run: `uv run pytest tests/unit/compliance/test_us.py tests/unit/compliance/test_lrs.py tests/unit/compliance/test_idle_fx.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/compliance config/compliance/us.yaml tests/unit/compliance
git commit -m "feat: enforce us lrs and idle-fx compliance"
```

### Task 22: Define the normalized BrokerAdapter and shared contract suite

**Files:**
- Create: `src/trading_os/brokers/__init__.py`
- Create: `src/trading_os/brokers/base.py`
- Create: `src/trading_os/brokers/models.py`
- Create: `tests/contract/brokers/base.py`
- Create: `tests/contract/brokers/test_fake_broker.py`

**Interfaces:**
- Consumes: canonical order/position models, `IntentId`, broker transport, and market enums.
- Produces: `BrokerAdapter`, `BrokerCapabilities`, `BrokerOrder`, `BrokerAccount`, `ReconciliationReport`, and reusable `BrokerContract` tests.

- [ ] **Step 1: Write the adapter contract against a fake**

```python
# tests/contract/brokers/base.py
import pytest

from trading_os.domain.orders import OrderStatus


class BrokerContract:
    @pytest.mark.asyncio
    async def test_submit_and_query_round_trip(self, adapter, valid_order) -> None:
        submitted = await adapter.submit(valid_order)
        queried = await adapter.get_order_status(valid_order.intent_id)
        assert queried.broker_order_id == submitted.broker_order_id

    @pytest.mark.asyncio
    async def test_ack_loss_does_not_duplicate_economic_effect(self, ack_loss_adapter, valid_order) -> None:
        await ack_loss_adapter.submit_with_lost_ack(valid_order)
        recovered = await ack_loss_adapter.reconcile_intent(valid_order.intent_id)
        assert recovered.status in {OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED}
        assert ack_loss_adapter.economic_order_count(valid_order.intent_id) == 1
```

- [ ] **Step 2: Run the fake contract and observe missing adapter**

Run: `uv run pytest tests/contract/brokers/test_fake_broker.py -v`

Expected: FAIL with missing broker modules.

- [ ] **Step 3: Implement the normalized ABC**

Define async methods `submit`, `modify`, `cancel`, `get_order_status`, `get_positions`,
`get_account`, `list_orders`, `list_protective_orders`, `reconcile_intent`, and `reconcile`.
`BrokerCapabilities` explicitly states native client-order correlation, native bracket support,
fractional quantity support, protective order kinds, paper support, max quantity precision, and
whether CA-adjusted stops are broker-managed. No core service may branch on adapter class; it
branches only on capabilities.

```python
class BrokerAdapter(ABC):
    @abstractmethod
    def capabilities(self) -> BrokerCapabilities:
        raise NotImplementedError

    @abstractmethod
    async def submit(self, order: OrderRequest) -> BrokerOrder:
        raise NotImplementedError

    @abstractmethod
    async def reconcile_intent(self, intent_id: IntentId) -> BrokerOrder:
        raise NotImplementedError

    @abstractmethod
    async def reconcile(self) -> ReconciliationReport:
        raise NotImplementedError
```

- [ ] **Step 4: Verify the shared contract**

Run: `uv run pytest tests/contract/brokers/test_fake_broker.py -v && uv run mypy src/trading_os/brokers`

Expected: all contract tests PASS and mypy exits 0.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/brokers tests/contract/brokers
git commit -m "feat: define normalized broker adapter contract"
```

### Task 23: Build the simulated broker with India/US market mechanics

**Files:**
- Create: `src/trading_os/brokers/simulated.py`
- Create: `src/trading_os/evaluation/fill_model.py`
- Create: `src/trading_os/evaluation/cost_model.py`
- Create: `config/costs/india_delivery.yaml`
- Create: `config/costs/us_cash.yaml`
- Create: `tests/contract/brokers/test_simulated_broker.py`
- Create: `tests/unit/evaluation/test_fill_model.py`
- Create: `tests/unit/evaluation/test_cost_model.py`

**Interfaces:**
- Consumes: canonical orders, validated daily bars, CA/circuit/calendar/settlement data, and versioned cost tables.
- Produces: `SimulatedBrokerAdapter`, deterministic `FillModel`, fee/tax breakdown, settled-cash timeline, GTT/stop lifecycle, and rejection reasons.

- [ ] **Step 1: Write mechanics tests**

```python
# tests/unit/evaluation/test_fill_model.py
from trading_os.evaluation.fill_model import FillModel


def test_gap_through_stop_limit_does_not_assume_fill(gap_through_bar, stop_limit_order) -> None:
    result = FillModel().evaluate(stop_limit_order, gap_through_bar)
    assert result.triggered is True
    assert result.filled_quantity.value == 0


def test_order_outside_circuit_band_is_rejected(circuit_bar, outside_band_order) -> None:
    assert FillModel().evaluate(outside_band_order, circuit_bar).rejection == "outside_price_band"
```

```python
# tests/unit/evaluation/test_cost_model.py
def test_india_dp_charge_is_flat_per_isin_per_sell_day(india_cost_model, same_day_sell_fills) -> None:
    breakdown = india_cost_model.costs(same_day_sell_fills)
    assert breakdown.dp_charge_count == 1
```

- [ ] **Step 2: Run and confirm simulation mechanics are absent**

Run: `uv run pytest tests/unit/evaluation/test_fill_model.py tests/unit/evaluation/test_cost_model.py -v`

Expected: FAIL with missing evaluation modules.

- [ ] **Step 3: Implement deterministic fills, costs, and settlement**

For daily bars, model limit reachability, stop trigger, gap-through without assumed fill, partial
fill schedule, queue-at-band behavior, circuit rejection/halts, DAY expiry, market-protection
bands, GTT fire-once semantics, CA cancellation, and T+1 settlement for both sleeves. India costs
include date-versioned STT, stamp duty, exchange fee, SEBI fee, GST, brokerage config, and flat
per-ISIN-per-sell-day DP charge. US costs include configured commissions/regulatory fees and
fractional precision. Seeded deterministic randomness is permitted only for declared fill
probabilities and the seed is stored in the run manifest.

Make `SimulatedBrokerAdapter` pass every shared broker contract and expose honest capabilities.

```python
def evaluate_stop_limit(order: OrderRequest, bar: DailyBar) -> FillEvaluation:
    if order.side is OrderSide.SELL:
        triggered = bar.low <= order.stop_price.value
        reachable = bar.high >= order.limit_price.value
    else:
        triggered = bar.high >= order.stop_price.value
        reachable = bar.low <= order.limit_price.value
    if not triggered:
        return FillEvaluation.not_triggered()
    return FillEvaluation.filled(order.quantity) if reachable else FillEvaluation.triggered_unfilled()
```

- [ ] **Step 4: Verify mechanics and broker contract**

Run: `uv run pytest tests/unit/evaluation tests/contract/brokers/test_simulated_broker.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/brokers/simulated.py src/trading_os/evaluation config/costs tests/unit/evaluation tests/contract/brokers/test_simulated_broker.py
git commit -m "feat: simulate broker fills costs and settlement"
```

### Task 24: Add the Alpaca adapter against paper API fixtures

**Files:**
- Create: `src/trading_os/brokers/alpaca.py`
- Create: `tests/fixtures/brokers/alpaca/submit.json`
- Create: `tests/fixtures/brokers/alpaca/partial_fill.json`
- Create: `tests/fixtures/brokers/alpaca/account_cash.json`
- Create: `tests/contract/brokers/test_alpaca_adapter.py`
- Create: `tests/integration/brokers/test_alpaca_paper.py`

**Interfaces:**
- Consumes: Alpaca transport/client, canonical orders, and `IntentId` mapped to `client_order_id`.
- Produces: `AlpacaBrokerAdapter` satisfying `BrokerAdapter` and an opt-in read/write paper smoke test.

- [ ] **Step 1: Write fixture-backed mapping and acknowledgement-loss tests**

```python
# tests/contract/brokers/test_alpaca_adapter.py
from tests.contract.brokers.base import BrokerContract


class TestAlpacaAdapter(BrokerContract):
    def test_capabilities_are_honest(self, adapter) -> None:
        capabilities = adapter.capabilities()
        assert capabilities.has_native_client_order_id is True
        assert capabilities.supports_fractional_quantity is True
        assert capabilities.paper_supported is True
```

- [ ] **Step 2: Run fixture tests and confirm adapter is absent**

Run: `uv run pytest tests/contract/brokers/test_alpaca_adapter.py -v`

Expected: FAIL with missing Alpaca adapter.

- [ ] **Step 3: Implement canonical mapping and reconcile-first behavior**

Map `IntentId` to Alpaca `client_order_id` before submission. Normalize statuses, quantities,
prices, fills, rejection messages, account cash/margin flags, and stop orders without leaking SDK
objects outside the adapter. A duplicate active client ID is correlation, not proof of replay
idempotency: on timeout/ack loss, query by client ID before any resubmission. Unknown/terminally
unqueryable outcomes return `OUTCOME_UNKNOWN`. Validate cash-account/no-margin flags on every
readiness check.

```python
async def reconcile_intent(self, intent_id: IntentId) -> BrokerOrder:
    try:
        raw = await self._client.get_order_by_client_id(str(intent_id))
    except AlpacaOrderNotFound:
        return BrokerOrder.outcome_unknown(intent_id, reason="client_order_id_not_found")
    return self._mapper.order(raw)
```

- [ ] **Step 4: Verify fixtures and opt-in paper smoke**

Run: `uv run pytest tests/contract/brokers/test_alpaca_adapter.py -v`

Expected: fixture contract PASS.

Run only with paper credentials: `uv run pytest tests/integration/brokers/test_alpaca_paper.py -v -m integration`

Expected: creates and cancels one minimum-value paper order, then confirms no live endpoint was used.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/brokers/alpaca.py tests/fixtures/brokers/alpaca tests/contract/brokers/test_alpaca_adapter.py tests/integration/brokers/test_alpaca_paper.py
git commit -m "feat: add alpaca paper broker adapter"
```

### Task 25: Add the Kite adapter using recorded fixtures only in CI

**Files:**
- Create: `src/trading_os/brokers/kite.py`
- Create: `src/trading_os/brokers/kite_reconcile.py`
- Create: `tests/fixtures/brokers/kite/order_accepted.json`
- Create: `tests/fixtures/brokers/kite/order_partial.json`
- Create: `tests/fixtures/brokers/kite/gtt_active.json`
- Create: `tests/fixtures/brokers/kite/gtt_triggered_unfilled.json`
- Create: `tests/fixtures/brokers/kite/token_exception.json`
- Create: `tests/contract/brokers/test_kite_adapter.py`

**Interfaces:**
- Consumes: Kite transport, recorded payloads, canonical orders, and durable intent metadata.
- Produces: `KiteBrokerAdapter` and deterministic heuristic reconciliation for brokers without a unique client order ID.

- [ ] **Step 1: Write fixture-backed capability and heuristic tests**

```python
# tests/contract/brokers/test_kite_adapter.py
from tests.contract.brokers.base import BrokerContract


class TestKiteAdapter(BrokerContract):
    def test_capabilities_are_honest(self, adapter) -> None:
        capabilities = adapter.capabilities()
        assert capabilities.has_native_client_order_id is False
        assert capabilities.paper_supported is False
        assert capabilities.protective_order_kinds == {"gtt_single", "gtt_oco"}

    def test_ambiguous_multiple_matches_remain_unknown(self, adapter, two_matching_orders, intent) -> None:
        result = adapter.match_intent(intent, two_matching_orders)
        assert result.status.value == "outcome_unknown"
```

- [ ] **Step 2: Run and confirm Kite adapter is absent**

Run: `uv run pytest tests/contract/brokers/test_kite_adapter.py -v`

Expected: FAIL with missing Kite adapter.

- [ ] **Step 3: Implement strict mapping and conservative reconciliation**

Map canonical orders to Kite delivery/CNC LIMIT or protected stop/GTT requests. Include the
broker-provisioned algo tag, price-protection band, and market/venue metadata. Never treat Kite tag
as unique. Reconcile an intent by exact market, symbol, side, quantity, price, tag, and bounded
submission-time window; zero or multiple matches remain `OUTCOME_UNKNOWN`. Normalize GTT active,
triggered, rejected, expired, CA-cancelled, and DAY-order-unfilled states. Map 403 TokenException to
the non-retryable readiness failure. Do not add any CI path that submits a live order.

```python
def match_intent(intent: BrokerIntent, orders: tuple[BrokerOrder, ...]) -> BrokerOrder:
    matches = tuple(order for order in orders if intent.matches(order))
    if len(matches) != 1:
        return BrokerOrder.outcome_unknown(intent.intent_id, reason=f"match_count={len(matches)}")
    return matches[0]
```

- [ ] **Step 4: Verify all recorded Kite behavior**

Run: `uv run pytest tests/contract/brokers/test_kite_adapter.py -v`

Expected: all fixture-backed contract tests PASS with no network access.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/brokers/kite.py src/trading_os/brokers/kite_reconcile.py tests/fixtures/brokers/kite tests/contract/brokers/test_kite_adapter.py
git commit -m "feat: add fixture-tested kite broker adapter"
```

### Task 26: Coordinate durable intents, approval revalidation, and reconciliation-before-retry

**Files:**
- Create: `src/trading_os/execution/intents.py`
- Create: `src/trading_os/execution/coordinator.py`
- Create: `src/trading_os/execution/reconciliation.py`
- Create: `tests/unit/execution/test_coordinator.py`
- Create: `tests/unit/execution/test_reconciliation.py`

**Interfaces:**
- Consumes: event store, reservation gate, kill switch, compliance/risk revalidators, HITL decision, and `BrokerAdapter`.
- Produces: `ExecutionCoordinator.submit(order_set)`, durable intent states, and `Reconciler.reconcile()`.

- [ ] **Step 1: Write crash/ack-loss and stale-approval tests**

```python
# tests/unit/execution/test_coordinator.py
import pytest

from trading_os.execution.coordinator import ExecutionCoordinator


@pytest.mark.asyncio
async def test_ack_loss_reconciles_before_retry(coordinator_with_ack_loss, approved_order_set) -> None:
    result = await coordinator_with_ack_loss.submit(approved_order_set)
    assert result.recovered_by_reconciliation is True
    assert coordinator_with_ack_loss.adapter.submit_call_count == 1


@pytest.mark.asyncio
async def test_snapshot_change_invalidates_approval(coordinator, approved_order_set, advance_snapshot) -> None:
    advance_snapshot()
    result = await coordinator.submit(approved_order_set)
    assert result.submitted is False
    assert result.reason == "stale_approval_snapshot"
```

- [ ] **Step 2: Run and observe missing coordinator**

Run: `uv run pytest tests/unit/execution/test_coordinator.py tests/unit/execution/test_reconciliation.py -v`

Expected: FAIL with missing coordinator/reconciliation modules.

- [ ] **Step 3: Implement the ordered side-effect protocol**

For each order set: verify immutable HITL hash/expiry/snapshot; rerun cash/risk/compliance/
protection/kill checks; acquire global reservation; append intent before broker call; submit with
current kill generation; append acknowledgement/fill observation; release reservation on terminal
failure or confirmed commit. A timeout/transport failure invokes `reconcile_intent` exactly once
before any retry decision. `OUTCOME_UNKNOWN` retains reservation, blocks symbol exposure, and alerts
HITL. Startup reconciliation compares projected intentions with broker orders, positions, cash,
and protective orders and appends observations; any unresolved mismatch halts new exposure.

```python
async def submit(self, order_set: ApprovedOrderSet) -> ExecutionResult:
    await self._revalidate(order_set)
    reservation = await self._reservations.reserve(order_set.reservation_request())
    await self._events.append(
        order_set.intent_event(reservation),
        expected_stream_version=order_set.intent_stream_version,
    )
    try:
        broker_order = await self._broker.submit(order_set.order)
    except BrokerOutcomeAmbiguous:
        broker_order = await self._broker.reconcile_intent(order_set.order.intent_id)
    if broker_order.status is OrderStatus.OUTCOME_UNKNOWN:
        await self._kill_switch.reduce(order_set.symbol_scope(), "outcome_unknown")
    return ExecutionResult.from_broker_order(broker_order, reservation)
```

- [ ] **Step 4: Verify crash boundaries and no duplicate economic effect**

Run: `uv run pytest tests/unit/execution/test_coordinator.py tests/unit/execution/test_reconciliation.py tests/contract/brokers -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/execution tests/unit/execution
git commit -m "feat: make broker effects crash-safe and reconcilable"
```

### Task 27: Implement layered exits and the protection-coverage supervisor

**Files:**
- Create: `src/trading_os/execution/exits.py`
- Create: `src/trading_os/execution/protection.py`
- Create: `src/trading_os/execution/protection_policy.py`
- Create: `src/trading_os/execution/corporate_action_monitor.py`
- Create: `config/exits/paper_v1.yaml`
- Create: `tests/unit/execution/test_exits.py`
- Create: `tests/unit/execution/test_protection.py`
- Create: `tests/unit/execution/test_protection_races.py`
- Create: `tests/unit/execution/test_corporate_action_monitor.py`

**Interfaces:**
- Consumes: broker fills/positions/protective orders, ATR/regime inputs, clock, event store, adapter capabilities, kill switch, and notifier.
- Produces: `ExitManager.on_fill()`, deterministic trail/time/regime exit intents, `ProtectionSupervisor.check_once()`, and coverage state events.

- [ ] **Step 1: Write coverage and race tests**

```python
# tests/unit/execution/test_protection.py
from trading_os.domain.enums import CoverageState, KillState


async def test_later_partial_fill_moves_symbol_back_to_reducing(protection_supervisor, position) -> None:
    await protection_supervisor.observe(position.with_quantities(open="10", protected="5"))
    result = await protection_supervisor.check_once()
    assert result.coverage_state is CoverageState.PARTIALLY_FILLED_UNPROTECTED
    assert result.symbol_kill_state is KillState.REDUCING
```

```python
# tests/unit/execution/test_protection_races.py
async def test_gtt_triggered_unfilled_is_repaired_before_eod(supervisor_with_unfilled_gtt) -> None:
    result = await supervisor_with_unfilled_gtt.check_once()
    assert result.action in {"replace_protection", "controlled_liquidation"}
    assert result.deferred_to_eod is False


async def test_halt_never_cancels_active_protection(supervisor, halted_state, active_stop) -> None:
    await supervisor.check_once()
    assert active_stop.broker_order_id not in supervisor.adapter.cancelled_order_ids
```

- [ ] **Step 2: Run and observe missing exit/protection services**

Run: `uv run pytest tests/unit/execution/test_exits.py tests/unit/execution/test_protection.py tests/unit/execution/test_protection_races.py -v`

Expected: FAIL with missing modules.

- [ ] **Step 3: Implement deterministic exit and coverage state machines**

`config/exits/paper_v1.yaml` freezes `atr_period_days: 14`, `initial_stop_atr_multiple: 3`,
`chandelier_atr_multiple: 3`, `time_stop_calendar_days: 30`, `risk_clock_poll_seconds: 2`,
`alpaca_fill_to_stop_deadline_seconds: 5`, `kite_fill_to_stop_deadline_seconds: 15`, and
`market_close_unprotected_escalation_seconds: 300`. On every fill, compute an ATR stop with frozen deterministic config and place protection without
HITL. Coverage is `PROTECTED` only when broker-confirmed protective quantity is at least reconciled
open quantity. Monitor rejection, cancellation, expiry, DAY unfilled, CA adjustment, later partial
fills, and duplicate/overlapping protection. Repair using adapter capabilities; if the protection
deadline expires, emit a controlled reduce-only liquidation intent or `HALTED_UNVERIFIED` if broker
state is unavailable.

Trailing stops ratchet only toward lower risk. Time-stop and regime-flip exits create reduce-only
intents and durable events. Replacing protection uses a stateful replace sequence that never treats
the position as protected until the new broker acknowledgement exists; temporary duplicate exits
must be safe against sell-to-open and reconciled immediately.

`CorporateActionMonitor` consumes the independent CA ledger and open positions before each session.
It computes adjusted quantity/trigger values, detects broker CA cancellation, and drives the same
coverage-deficit state machine; it never mutates an active stop record in place.

```python
def coverage_state(position_qty: Decimal, confirmed_exit_qty: Decimal) -> CoverageState:
    if confirmed_exit_qty >= position_qty and position_qty > 0:
        return CoverageState.PROTECTED
    if confirmed_exit_qty > 0:
        return CoverageState.PARTIALLY_FILLED_UNPROTECTED
    return CoverageState.PROTECTION_PENDING
```

- [ ] **Step 4: Verify every D25 failure path**

Run: `uv run pytest tests/unit/execution/test_exits.py tests/unit/execution/test_protection.py tests/unit/execution/test_protection_races.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/execution config/exits/paper_v1.yaml tests/unit/execution
git commit -m "feat: supervise broker-confirmed position protection"
```

### Task 28: Build the exposure-aware HITL backend

**Files:**
- Create: `src/trading_os/hitl/__init__.py`
- Create: `src/trading_os/hitl/models.py`
- Create: `src/trading_os/hitl/tokens.py`
- Create: `src/trading_os/hitl/backend.py`
- Create: `src/trading_os/hitl/telegram.py`
- Create: `src/trading_os/hitl/dashboard.py`
- Create: `config/hitl/paper_v1.yaml`
- Create: `tests/unit/hitl/test_tokens.py`
- Create: `tests/unit/hitl/test_backend.py`
- Create: `tests/contract/hitl/test_transports.py`

**Interfaces:**
- Consumes: order-set hash, snapshot version, expiry, exposure sign, HMAC secret, event store, clock, and transport ports.
- Produces: immutable `ApprovalRequest`, `ApprovalDecision`, signed tokens, entry approval/default-deny, exit veto/default-proceed, emergency HALT, and localhost-only un-HALT request.

- [ ] **Step 1: Write token binding and timeout-default tests**

```python
# tests/unit/hitl/test_backend.py
from trading_os.hitl.models import ExposureEffect


async def test_entry_timeout_denies_order(hitl_backend, expired_entry_request) -> None:
    result = await hitl_backend.resolve(expired_entry_request)
    assert result.approved is False
    assert result.reason == "entry_timeout_default_deny"


async def test_exit_timeout_proceeds(hitl_backend, expired_exit_request) -> None:
    assert expired_exit_request.exposure_effect is ExposureEffect.REDUCING
    result = await hitl_backend.resolve(expired_exit_request)
    assert result.approved is True
    assert result.reason == "exit_timeout_default_proceed"
```

```python
# tests/unit/hitl/test_tokens.py
import pytest

from trading_os.hitl.tokens import InvalidApprovalToken


def test_token_is_bound_to_order_hash_snapshot_and_expiry(token_service, approval_request) -> None:
    token = token_service.sign(approval_request)
    tampered = approval_request.model_copy(update={"snapshot_version": approval_request.snapshot_version + 1})
    with pytest.raises(InvalidApprovalToken):
        token_service.verify(token, tampered)
```

- [ ] **Step 2: Run and observe missing HITL backend**

Run: `uv run pytest tests/unit/hitl tests/contract/hitl -v`

Expected: FAIL with missing HITL modules.

- [ ] **Step 3: Implement one backend and two transports**

`config/hitl/paper_v1.yaml` freezes `entry_approval_window_seconds: 1800`,
`exit_veto_window_seconds: 300`, and `localhost_bind: 127.0.0.1`. The concrete `HITLBackend` uses HMAC-SHA256 over canonical order-set hash, snapshot version, expiry, request ID, exposure effect,
and authorized user ID. Persist every request and decision. Telegram permits approve/reject and
emergency HALT but never un-HALT. FastAPI binds to `127.0.0.1`, uses re-authentication for un-HALT,
and exposes no public network binding. Protective stop placement bypasses HITL entirely. Transport
messages carry opaque request IDs and summaries, never secrets or raw provider payloads.

```python
def sign(self, request: ApprovalRequest) -> str:
    payload = orjson.dumps(request.signing_fields(), option=orjson.OPT_SORT_KEYS)
    digest = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
    return f"{base64.urlsafe_b64encode(payload).decode()}.{digest}"
```

- [ ] **Step 4: Verify timeout, tamper, authorization, and transport contracts**

Run: `uv run pytest tests/unit/hitl tests/contract/hitl -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/hitl config/hitl/paper_v1.yaml tests/unit/hitl tests/contract/hitl
git commit -m "feat: add exposure-aware hitl approval backend"
```

---

## Milestone 4 — Accounting, Orchestration, Evaluation, and Paper Operations

### Task 29: Persist Timescale market data and snapshot-scoped source records

**Files:**
- Create: `alembic/versions/20260721_0002_market_data.py`
- Create: `src/trading_os/data/repository.py`
- Create: `src/trading_os/data/adapters/__init__.py`
- Create: `src/trading_os/data/adapters/nse_bse.py`
- Create: `src/trading_os/data/adapters/alpaca.py`
- Create: `src/trading_os/data/adapters/vetted_news.py`
- Create: `src/trading_os/data/fundamentals_panel.py`
- Create: `tests/integration/data/test_repository.py`
- Create: `tests/contract/data/test_feed_adapters.py`

**Interfaces:**
- Consumes: raw/normalized models, market-data ports, independent CA/universe sources, and snapshot IDs.
- Produces: append-only source tables, Timescale OHLCV hypertables, source adapters, and `SnapshotDataRepository` methods that always require a snapshot ID.

- [ ] **Step 1: Write snapshot-scoped repository tests**

```python
# tests/integration/data/test_repository.py
import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_returns_only_rows_pinned_by_snapshot(data_repository, sealed_snapshot) -> None:
    rows = await data_repository.total_return_bars(sealed_snapshot.snapshot_id, symbols=("INFY",))
    assert rows
    assert {row.component_hash for row in rows} <= set(sealed_snapshot.component_hashes.values())


def test_repository_has_no_unscoped_latest_method() -> None:
    from trading_os.data.repository import SnapshotDataRepository
    assert not hasattr(SnapshotDataRepository, "latest")
```

- [ ] **Step 2: Apply the missing migration test and observe failure**

Run: `docker compose up -d postgres && uv run alembic upgrade head && uv run pytest tests/integration/data/test_repository.py -v`

Expected: FAIL because market-data schema and repository do not exist.

- [ ] **Step 3: Add immutable tables, hypertables, and feed mappings**

Create append-only tables for source records, raw bars, adjusted series, corporate actions,
universe memberships, security classifications, news snapshots, cash events, FX rate records, and
validated snapshot manifests. `raw_bars` is a Timescale hypertable on exchange timestamp with
symbol/market dimensions. Natural source revisions create a new source version/hash rather than
updating old rows. Enforce unique source/source-record/version and snapshot/content-hash keys.

Implement NSE/BSE adapters for bhavcopy, CA, announcement, universe membership, and delisting
inputs; Alpaca adapter for US bars/news/corporate actions; and vetted news adapter for GDELT plus
NSE/BSE announcements. Every adapter maps external fields into immutable source DTOs and records
retrieval/cutoff timestamps. No news adapter writes compliance or CA truth tables.

`fundamentals_panel.py` stores weekly observed filing/fundamental snapshots with received-at and
source-publication timestamps, applies a frozen 45-calendar-day reporting lag, and exposes a quality
panel only after at least 24 monthly observations per security plus a successful restatement/replay
validation. Until then the validated snapshot manifest keeps quality disabled.

```python
async def total_return_bars(
    self, snapshot_id: ValidatedDataSnapshotId, *, symbols: tuple[str, ...]
) -> tuple[AdjustedBar, ...]:
    manifest = await self._load_manifest(snapshot_id)
    allowed_hash = manifest.component_hashes["total_return_ohlcv"]
    return await self._select_bars(
        symbols=symbols,
        series="total_return",
        component_hash=allowed_hash,
    )
```

- [ ] **Step 4: Verify migrations and fixture-backed adapters**

Run: `uv run alembic upgrade head && uv run pytest tests/integration/data/test_repository.py tests/contract/data/test_feed_adapters.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alembic/versions/20260721_0002_market_data.py src/trading_os/data tests/integration/data tests/contract/data
git commit -m "feat: persist snapshot-scoped market data"
```

### Task 30: Implement immutable FX/accounting ledgers and broker cash-event ingestion

**Files:**
- Create: `alembic/versions/20260721_0003_accounting.py`
- Create: `src/trading_os/accounting/__init__.py`
- Create: `src/trading_os/accounting/fx.py`
- Create: `src/trading_os/accounting/ledger.py`
- Create: `src/trading_os/accounting/tax_reports.py`
- Create: `src/trading_os/data/broker_cash_ingestor.py`
- Create: `tests/unit/accounting/test_fx.py`
- Create: `tests/unit/accounting/test_ledger.py`
- Create: `tests/unit/accounting/test_tax_reports.py`
- Create: `tests/unit/data/test_broker_cash_ingestor.py`

**Interfaces:**
- Consumes: fills, fees, cash events, immutable live/Rule-115 rate records, strategy attribution, and broker transaction IDs.
- Produces: balanced native/INR journal entries, FX lots, tax/report views, and idempotent cash-event ingestion.

- [ ] **Step 1: Write rate, replay, and no-double-count tests**

```python
# tests/unit/accounting/test_ledger.py
from decimal import Decimal


def test_accounting_identity_holds_after_us_round_trip(accounting_ledger, us_round_trip_events) -> None:
    ledger = accounting_ledger.replay(us_round_trip_events)
    assert ledger.debits_total == ledger.credits_total
    assert ledger.unexplained_balance == Decimal("0")


def test_live_fx_risk_mark_is_not_booked_as_realized_gain(accounting_ledger, live_fx_mark_event) -> None:
    before = accounting_ledger.realized_fx_gain
    after = accounting_ledger.apply(live_fx_mark_event)
    assert after.realized_fx_gain == before
```

```python
# tests/unit/data/test_broker_cash_ingestor.py
async def test_duplicate_broker_transaction_is_ingested_once(cash_ingestor, dividend_payload) -> None:
    first = await cash_ingestor.ingest(dividend_payload)
    second = await cash_ingestor.ingest(dividend_payload)
    assert first.created is True
    assert second.created is False
```

- [ ] **Step 2: Run and observe missing accounting modules**

Run: `uv run pytest tests/unit/accounting tests/unit/data/test_broker_cash_ingestor.py -v`

Expected: FAIL with missing modules.

- [ ] **Step 3: Implement fixed-point journals and immutable rate assignment**

Each economic event records occurred-at, exchange trade date, settlement/value date, and tax
recognition date. A native fill is immutable. `TaxFxRateAssigned`, `LiveFxMarkObserved`, and
corrections are separate events referencing immutable rate-record IDs. Rule-115 lookup selects SBI
TT buying rate from the last day of the prior month with a versioned previous-published-business-day
fallback. Live rate staleness is explicit.

Book equity P&L at a held-constant anchor rate, realized currency movement only in the FX-lot
ledger, and live INR marks only in risk projections; never sum all three views. Use FIFO FX lots
until legal config changes. Record gross remittance, USD received, bank spread, fee, and TCS as
separate entries. Tax report views include Schedule FA calendar-year peak/closing balances,
dividend gross/withholding, Form 67 data, CG/FSI/TR/OS fields, and source rate IDs.

`BrokerCashEventIngestor` deduplicates by broker plus broker transaction ID and opens idle-FX lots
for eligible USD credits.

```python
def assign_rule115_rate(transaction_date: date, published: Sequence[FxRateRecord]) -> FxRateRecord:
    prior_month_end = transaction_date.replace(day=1) - timedelta(days=1)
    eligible = [rate for rate in published if rate.rate_date <= prior_month_end]
    if not eligible:
        raise MissingTaxFxRate(str(transaction_date))
    return max(eligible, key=lambda rate: rate.rate_date)


def post(entry: JournalEntry, balances: LedgerBalances) -> LedgerBalances:
    if entry.debit.amount != entry.credit.amount or entry.debit.currency is not entry.credit.currency:
        raise UnbalancedEntry(str(entry.entry_id))
    return balances.apply(entry)
```

- [ ] **Step 4: Verify accounting and migration**

Run: `uv run alembic upgrade head && uv run pytest tests/unit/accounting tests/unit/data/test_broker_cash_ingestor.py -v`

Expected: all tests PASS and every journal fixture balances.

- [ ] **Step 5: Commit**

```bash
git add alembic/versions/20260721_0003_accounting.py src/trading_os/accounting src/trading_os/data/broker_cash_ingestor.py tests/unit/accounting tests/unit/data/test_broker_cash_ingestor.py
git commit -m "feat: add immutable fx and tax accounting"
```

### Task 31: Add the calibration store without creating a sizing wire

**Files:**
- Create: `alembic/versions/20260721_0004_calibration.py`
- Create: `src/trading_os/portfolio/calibration.py`
- Create: `tests/unit/portfolio/test_calibration.py`
- Create: `tests/unit/portfolio/test_calibration_seam.py`

**Interfaces:**
- Consumes: one closed `PositionEpisode`, entry conviction band/regime/market/model metadata, and realized outcome.
- Produces: `CalibrationStore`, idempotent `CalibrationRecorded`, Beta-Bernoulli summaries, maturity status at N=30, and a gate/rank-only read view.

- [ ] **Step 1: Write idempotency, maturity, and no-sizing-import tests**

```python
# tests/unit/portfolio/test_calibration.py
async def test_episode_is_recorded_exactly_once(calibration_store, closed_episode) -> None:
    assert await calibration_store.record(closed_episode) is True
    assert await calibration_store.record(closed_episode) is False


def test_cell_matures_at_thirty_observations(calibration_summary_factory) -> None:
    assert calibration_summary_factory(sample_n=29).mature is False
    assert calibration_summary_factory(sample_n=30).mature is True
```

```python
# tests/unit/portfolio/test_calibration_seam.py
from pathlib import Path


def test_sizing_and_risk_do_not_import_calibration() -> None:
    offenders = [
        str(path)
        for path in [Path("src/trading_os/portfolio/sizing.py"), Path("src/trading_os/portfolio/risk.py")]
        if "portfolio.calibration" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []
```

- [ ] **Step 2: Run and observe missing calibration store**

Run: `uv run pytest tests/unit/portfolio/test_calibration.py tests/unit/portfolio/test_calibration_seam.py -v`

Expected: FAIL with missing calibration module.

- [ ] **Step 3: Implement an episode-keyed, gate/rank-only store**

Persist the D9b key `(model, prompt_version, conviction_bucket, market, regime)` plus hit, payoff,
sample count, estimate time, and unique `position_episode_id`. A unique database constraint makes
replay idempotent. Use Beta(1,1) prior unless a frozen manifest selects another prior. Expose only
`GateRankCalibrationView` to `signals.gate_rank`; the view contains mature/not-mature and
demote/veto classification, not a probability, Kelly fraction, size multiplier, volatility, price,
or stop value. Add an import-boundary test covering every hot-path numeric module.

```python
async def record(self, episode: ClosedPositionEpisode) -> bool:
    statement = (
        insert(calibration_table)
        .values(**episode.to_calibration_row())
        .on_conflict_do_nothing(index_elements=["position_episode_id"])
    )
    result = await self._session.execute(statement)
    await self._session.commit()
    return result.rowcount == 1
```

- [ ] **Step 4: Verify store behavior and seam isolation**

Run: `uv run alembic upgrade head && uv run pytest tests/unit/portfolio/test_calibration.py tests/unit/portfolio/test_calibration_seam.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add alembic/versions/20260721_0004_calibration.py src/trading_os/portfolio/calibration.py tests/unit/portfolio/test_calibration.py tests/unit/portfolio/test_calibration_seam.py
git commit -m "feat: record calibration for gate rank only"
```

### Task 32: Compose the idempotent scheduler and EOD cycle

**Files:**
- Create: `src/trading_os/control/scheduler.py`
- Create: `src/trading_os/control/jobs.py`
- Create: `src/trading_os/control/eod_cycle.py`
- Create: `tests/unit/control/test_scheduler.py`
- Create: `tests/unit/control/test_eod_cycle.py`
- Create: `tests/unit/control/test_job_idempotency.py`

**Interfaces:**
- Consumes: readiness gates, data ingest/correctness, research, traversal, signals, sizing/risk/compliance, HITL, coordinator, reconciliation, accounting, and event store.
- Produces: calendar-aware job definitions, unique cycle/job keys, and `EodCycle.run_market_day(market, trade_date)` phase results.

- [ ] **Step 1: Write phase-order and duplicate-fire tests**

```python
# tests/unit/control/test_eod_cycle.py
async def test_no_signal_runs_before_validated_snapshot(eod_cycle, failing_correctness_layer) -> None:
    result = await eod_cycle.run_market_day("india", "2026-07-21")
    assert result.status == "data_failed_closed"
    assert eod_cycle.signal_engine.call_count == 0
    assert eod_cycle.llm_research.call_count == 0
```

```python
# tests/unit/control/test_job_idempotency.py
import asyncio


async def test_duplicate_scheduler_fire_executes_cycle_once(scheduler, cycle_key) -> None:
    results = await asyncio.gather(scheduler.fire(cycle_key), scheduler.fire(cycle_key))
    assert sum(result.started for result in results) == 1
```

- [ ] **Step 2: Run and observe missing scheduler/orchestrator**

Run: `uv run pytest tests/unit/control/test_scheduler.py tests/unit/control/test_eod_cycle.py tests/unit/control/test_job_idempotency.py -v`

Expected: FAIL with missing modules.

- [ ] **Step 3: Implement the exact seven-phase workflow**

Use APScheduler only to trigger durable job intents; business ordering lives in `EodCycle`.
Acquire a unique job lease on `(job_kind, market, exchange_trade_date, config_hash)`. Run phases in
this order: session/credential readiness; ingest/correctness seal; on-cadence slow research and
deterministic traversal; seam projection; deterministic gate/rank/sizing/risk/compliance;
exposure-aware HITL and revalidation; durable execution/protection; reconciliation/accounting/
calibration and cycle completion. Each phase appends started/completed/failed events and resumes
from the first incomplete phase. Label-refresh events may run off cadence but cannot enter the
decision phase. Research jobs may run per sleeve concurrently; reservation commit remains global.

```python
async def run_market_day(self, market: Market, trade_date: date) -> CycleResult:
    cycle = await self._jobs.acquire(CycleKey.eod(market, trade_date))
    for phase in self._ordered_phases:
        if await cycle.is_completed(phase.name):
            continue
        await cycle.mark_started(phase.name)
        outcome = await phase.run(cycle.context)
        await cycle.mark_finished(phase.name, outcome)
        if outcome.fail_closed:
            return CycleResult.failed(phase.name, outcome.reason)
    return CycleResult.completed(cycle.cycle_id)
```

- [ ] **Step 4: Verify order, restart, and duplicate suppression**

Run: `uv run pytest tests/unit/control/test_scheduler.py tests/unit/control/test_eod_cycle.py tests/unit/control/test_job_idempotency.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/control tests/unit/control
git commit -m "feat: orchestrate idempotent calendar-aware eod cycles"
```

### Task 33: Add watchdog, structured logging, notifications, and backup verification

**Files:**
- Create: `src/trading_os/control/watchdog.py`
- Create: `src/trading_os/observability/__init__.py`
- Create: `src/trading_os/observability/logging.py`
- Create: `src/trading_os/observability/redaction.py`
- Create: `src/trading_os/observability/secrets.py`
- Create: `config/ops/paper_v1.yaml`
- Create: `deploy/systemd/trading-os.service`
- Create: `deploy/systemd/trading-os-watchdog.service`
- Create: `deploy/systemd/trading-os-backup.service`
- Create: `deploy/systemd/trading-os-backup.timer`
- Create: `scripts/backup_postgres.sh`
- Create: `scripts/verify_backup.sh`
- Create: `tests/unit/control/test_watchdog.py`
- Create: `tests/unit/observability/test_redaction.py`
- Create: `tests/unit/observability/test_secrets.py`
- Create: `tests/contract/ops/test_backup_scripts.py`
- Create: `tests/contract/ops/test_systemd_units.py`

**Interfaces:**
- Consumes: heartbeat events, clock, kill switch, event store, notifier, database config, and secrets redaction rules.
- Produces: dead-man HALT, structured JSON logs, daily reconciliation notification, encrypted backup artifacts, and restore-verification result.

- [ ] **Step 1: Write dead-man and secret-redaction tests**

```python
# tests/unit/control/test_watchdog.py
from datetime import timedelta


async def test_silent_main_loop_halts_and_bumps_generation(watchdog, frozen_clock, kill_switch) -> None:
    frozen_clock.advance(timedelta(seconds=watchdog.dead_man_seconds + 1))
    await watchdog.check_once()
    snapshot = await kill_switch.snapshot()
    assert snapshot.blocks_new_exposure is True
    assert snapshot.generation == 1
```

```python
# tests/unit/observability/test_redaction.py
from trading_os.observability.redaction import redact_event


def test_secret_fields_never_reach_structured_logs() -> None:
    redacted = redact_event({"api_key": "secret", "token": "secret", "symbol": "INFY"})
    assert redacted == {"api_key": "[REDACTED]", "token": "[REDACTED]", "symbol": "INFY"}
```

```python
# tests/contract/ops/test_systemd_units.py
from pathlib import Path


def test_services_are_unprivileged_restartable_and_paper_only() -> None:
    for name in ("trading-os.service", "trading-os-watchdog.service"):
        unit = (Path("deploy/systemd") / name).read_text()
        assert "User=trading-os" in unit
        assert "Restart=on-failure" in unit
        assert " live" not in unit
        assert "API_KEY=" not in unit
```

- [ ] **Step 2: Run and observe missing ops services**

Run: `uv run pytest tests/unit/control/test_watchdog.py tests/unit/observability/test_redaction.py -v`

Expected: FAIL with missing modules.

- [ ] **Step 3: Implement independent watchdog and recoverable backups**

`config/ops/paper_v1.yaml` freezes `heartbeat_seconds: 5`, `dead_man_seconds: 20`,
`daily_reconciliation_report: true`, `backup_hour_ist: 2`, and
`kite_reauth_not_before_ist: 07:30`. The concrete `Watchdog` reads durable/independent heartbeats, not an in-process boolean. Silence beyond the
configured deadline appends a failure and HALTs through the kill switch, ensuring generation
fencing. It cannot un-HALT. Structured JSON logging includes correlation/intent/snapshot IDs,
market, rule/version hashes, and outcomes while redacting configured secret-key patterns and all
Pydantic `SecretStr` values.

The deployment units make the always-on-host requirement executable: the service manager restarts
the paper process and independent watchdog on failure, orders startup after network/database
readiness, supplies secrets through a restricted file descriptor, and schedules the encrypted
backup plus restore verification. Units run as a dedicated unprivileged user, set a fixed working
directory, use `Restart=on-failure`, and must never contain credentials or a live-mode command. The
contract test parses every unit and proves these invariants before deployment.

Implement `MacOSKeychainSecrets` by invoking `/usr/bin/security find-generic-password` with a fixed
service allowlist and capturing stdout without logging it. Implement `AgeEncryptedEnvSecrets` by
reading an already-decrypted file descriptor supplied by the service manager; it never shells out
with plaintext or stores decrypted bytes in the repository. Both satisfy `SecretsPort`, return
`SecretStr`, and clear temporary bytearrays after parsing where Python permits.

`backup_postgres.sh` uses `pg_dump --format=custom` to an explicitly configured backup directory,
then encrypts with `age` using a configured public recipient; it never reads a plaintext secret
from command arguments. `verify_backup.sh` restores into an explicitly named disposable database,
checks event counts and maximum stream versions, then drops only that validated disposable
database. The contract test runs scripts against a temporary Postgres instance and confirms a
round trip.

```python
async def check_once(self) -> None:
    heartbeat = await self._heartbeats.latest("main_loop")
    expired = heartbeat is None or self._clock.now() - heartbeat.recorded_at > self._dead_man
    if expired:
        await self._kill_switch.halt(KillScope.global_scope(), reason="dead_man_timeout")
        await self._notifier.urgent("Trading OS halted: main-loop heartbeat expired")
```

- [ ] **Step 4: Verify watchdog and backup round trip**

Run: `uv run pytest tests/unit/control/test_watchdog.py tests/unit/observability/test_redaction.py tests/contract/ops/test_backup_scripts.py tests/contract/ops/test_systemd_units.py -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/control/watchdog.py src/trading_os/observability config/ops/paper_v1.yaml deploy/systemd scripts tests/unit/control/test_watchdog.py tests/unit/observability tests/contract/ops
git commit -m "feat: add dead-man observability and backup verification"
```

### Task 34: Implement CPCV, Deflated Sharpe, scoreboards, and frozen promotion manifests

**Files:**
- Create: `src/trading_os/evaluation/cpcv.py`
- Create: `src/trading_os/evaluation/deflated_sharpe.py`
- Create: `src/trading_os/evaluation/scoreboard.py`
- Create: `src/trading_os/evaluation/promotion.py`
- Create: `config/promotion/paper_v1.yaml`
- Create: `tests/unit/evaluation/test_cpcv.py`
- Create: `tests/unit/evaluation/test_deflated_sharpe.py`
- Create: `tests/unit/evaluation/test_scoreboard.py`
- Create: `tests/unit/evaluation/test_promotion.py`

**Interfaces:**
- Consumes: separately attributed LLM/null/index returns, trial registry, costs, decision windows, sim-vs-paper fills, manifest thresholds, and event store.
- Produces: CPCV paths, DSR, per-book net scoreboard, content-hashed `PromotionManifest`, and `PromotionDecision`.

- [ ] **Step 1: Write frozen-ruler and all-gates tests**

```python
# tests/unit/evaluation/test_promotion.py
from trading_os.evaluation.promotion import PromotionEvaluator


def test_manifest_hash_changes_when_threshold_changes(promotion_manifest) -> None:
    changed = promotion_manifest.model_copy(update={"max_tracking_error": promotion_manifest.max_tracking_error * 2})
    assert changed.content_hash != promotion_manifest.content_hash


def test_promotion_fails_when_any_single_gate_fails(passing_evidence, promotion_manifest) -> None:
    for field in passing_evidence.gate_fields:
        failed = passing_evidence.fail_only(field)
        assert PromotionEvaluator(promotion_manifest).evaluate(failed).approved is False
```

```python
# tests/unit/evaluation/test_scoreboard.py
def test_rule_null_and_llm_costs_remain_separate(scoreboard, attributed_returns) -> None:
    result = scoreboard.compute(attributed_returns)
    assert result.llm.net_return == result.llm.gross_return - result.llm.total_cost
    assert result.null.net_return == result.null.gross_return - result.null.total_cost
```

- [ ] **Step 2: Run and observe missing evaluation statistics**

Run: `uv run pytest tests/unit/evaluation/test_cpcv.py tests/unit/evaluation/test_deflated_sharpe.py tests/unit/evaluation/test_scoreboard.py tests/unit/evaluation/test_promotion.py -v`

Expected: FAIL with missing modules.

- [ ] **Step 3: Implement precommitted evaluation**

Implement purged combinatorial cross-validation with embargo, trial-registry-aware Deflated Sharpe,
and effective sample size clustered by independent decision/shock event rather than stock-day cells.
The scoreboard reads separate strategy books and matched NIFTY/SPY total-return benchmarks in INR,
net of each path's actual costs. `PromotionManifest` is strict/frozen and includes numeric bounds for
minimum windows, DSR, max drawdown, sim-paper tracking error, cost-model error, KG rank correlation,
trial count, calibration N=30, cost assumptions, benchmark IDs, config/prompt/model hashes, data
snapshot rules, and required historical replays. Seal its content hash to the event log before paper
day 1; later mutation creates a new paper campaign and cannot promote the old one.

Write `config/promotion/paper_v1.yaml` with exact initial values:

```yaml
campaign_days: 90
minimum_decision_windows: 3
minimum_dsr_exclusive: 0.0
maximum_drawdown_fraction: 0.08
maximum_sim_paper_fill_tracking_mae_bps: 50
maximum_slippage_model_mae_bps: 25
minimum_llm_net_excess_return_bps: 1
minimum_null_net_excess_return_bps: 1
minimum_kg_spearman_rank_correlation: 0.10
calibration_cell_minimum_n: 30
maximum_llm_annual_cost_usd: 730
maximum_total_annual_cost_fraction_of_disposable_capital: 0.10
required_replays: [covid_2020, russia_ukraine_2022]
```

The parser treats percentage fields as fractions and basis-point fields as integer bps. Any change
before sealing is reviewable configuration; any change after sealing creates a new campaign and
resets the 90-day clock. The total-cost gate annualizes broker subscriptions, always-on hosting,
market/fundamental data, storage/backups, and LLM spend; promotion fails if their combined committed
cost exceeds the frozen fraction of the explicitly attested disposable capital balance.

- [ ] **Step 4: Verify every promotion gate**

Run: `uv run pytest tests/unit/evaluation -v`

Expected: all evaluation tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/evaluation config/promotion/paper_v1.yaml tests/unit/evaluation
git commit -m "feat: freeze rigorous paper promotion scorecard"
```

### Task 35: Add causal-KG historical replay and rank-correlation validation

**Files:**
- Create: `src/trading_os/evaluation/kg_replay.py`
- Create: `config/replays/covid_2020.yaml`
- Create: `config/replays/russia_ukraine_2022.yaml`
- Create: `tests/unit/evaluation/test_kg_replay.py`
- Create: `tests/fixtures/replays/covid_2020_expected.json`
- Create: `tests/fixtures/replays/russia_ukraine_2022_expected.json`

**Interfaces:**
- Consumes: historical sealed snapshots, versioned graph/weight artifacts available as of event date, realized cross-sectional returns, and cost model.
- Produces: audited rank correlation, beneficiary/harm ranking, net-of-cost replay result, and promotion evidence.

- [ ] **Step 1: Write no-look-ahead and reproducibility tests**

```python
# tests/unit/evaluation/test_kg_replay.py
def test_replay_uses_only_edges_available_on_event_date(covid_replay) -> None:
    result = covid_replay.run()
    assert all(path.edge_valid_from <= result.event_as_of for path in result.audited_paths)


def test_replay_is_byte_reproducible(russia_ukraine_replay) -> None:
    assert russia_ukraine_replay.run().model_dump_json() == russia_ukraine_replay.run().model_dump_json()
```

- [ ] **Step 2: Run and observe missing replay evaluator**

Run: `uv run pytest tests/unit/evaluation/test_kg_replay.py -v`

Expected: FAIL with missing KG replay module.

- [ ] **Step 3: Implement frozen historical replay definitions**

Each YAML pins event as-of, snapshot ID, graph/weight versions, universe, driver/source/phase/
direction/ordinal labels, evaluation horizon, realized-return source, cost model, and expected
minimum rank-correlation rule. Replay rejects graph edges or source material published after event
as-of. Compute Spearman rank correlation, top/bottom bucket spread, turnover, and net costs. Store
top contributing paths for audit but never feed replay results into live size. The two named replay
results are required promotion evidence, not optional examples.

```python
def run(self, definition: ReplayDefinition) -> KgReplayResult:
    graph = self._graphs.load(definition.graph_version, as_of=definition.event_as_of)
    if any(edge.valid_from > definition.event_as_of for edge in graph.edges):
        raise LookAheadDetected(definition.replay_id)
    vector = self._traversal.compute(graph, definition.macro_event)
    rho = scipy.stats.spearmanr(
        vector.ranks(), definition.realized_return_ranks()
    ).statistic
    return KgReplayResult.from_metrics(
        definition,
        spearman_rho=Decimal(str(rho)),
        vector=vector,
    )
```

- [ ] **Step 4: Verify both mandatory historical replays**

Run: `uv run pytest tests/unit/evaluation/test_kg_replay.py -v`

Expected: tests PASS against versioned fixture expectations.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/evaluation/kg_replay.py config/replays tests/unit/evaluation/test_kg_replay.py tests/fixtures/replays
git commit -m "feat: validate causal kg with historical replays"
```

### Task 36: Compose the paper CLI and mechanically guard live mode

**Files:**
- Create: `src/trading_os/bootstrap.py`
- Create: `src/trading_os/cli.py`
- Create: `src/trading_os/live_blockers.py`
- Create: `config/live_blockers.yaml`
- Create: `tests/unit/test_live_blockers.py`
- Create: `tests/integration/test_paper_bootstrap.py`

**Interfaces:**
- Consumes: settings, all ports/adapters/services, promotion decision, legal/operational blocker attestations, and run mode.
- Produces: `build_application(settings)`, CLI commands `doctor`, `migrate`, `paper-run`, `reconcile`, `promotion-status`, and a guarded `live-run`.

- [ ] **Step 1: Write paper boot and live refusal tests**

```python
# tests/unit/test_live_blockers.py
import pytest

from trading_os.live_blockers import LiveBlockerRegistry, LiveTradingBlocked


def test_live_refuses_when_any_required_blocker_is_open(open_blocker_evidence) -> None:
    registry = LiveBlockerRegistry.from_config("config/live_blockers.yaml")
    with pytest.raises(LiveTradingBlocked, match="FEMA_CA_IDLE_FX_OPINION"):
        registry.assert_live_allowed(open_blocker_evidence)
```

```python
# tests/integration/test_paper_bootstrap.py
import pytest

from trading_os.bootstrap import build_application


@pytest.mark.integration
@pytest.mark.asyncio
async def test_paper_application_starts_reconciled_and_halted_until_ready(paper_settings) -> None:
    app = await build_application(paper_settings)
    assert app.mode.value == "paper"
    assert app.startup_reconciliation.completed is True
    assert app.live_submission_enabled is False
```

- [ ] **Step 2: Run and observe missing composition root**

Run: `uv run pytest tests/unit/test_live_blockers.py tests/integration/test_paper_bootstrap.py -v`

Expected: FAIL with missing bootstrap/CLI modules.

- [ ] **Step 3: Implement explicit dependency composition and live blockers**

`bootstrap.py` is the only composition root. Select adapters by config and inject all protocols;
do not use module-level service locators. Startup order is database migration check, event replay,
broker reconciliation, cache rebuild, kill-state load, protection audit, readiness checks, then
scheduler/watchdog start. Paper mode uses simulated or Alpaca paper adapters and separate strategy
books.

`config/live_blockers.yaml` requires: approved promotion manifest/evidence; written Alpaca cash/
India onboarding confirmation; Finance Act/TCS/LTCG verification; FEMA-CA idle-FX/sweep/repatriation
opinion; cross-border investment-income opinion; Zerodha below-TOPS/tag SOP; DDPI active; static IP;
audit retention; verified backup restore; successful reconciliation/protection drill; and explicit
`live_trading_enabled=true`. `live-run` prints only blocker IDs and safe descriptions, never secrets,
and exits nonzero if any are absent, expired, mismatched to account, or tied to a different manifest.

```python
def assert_live_allowed(self, evidence: LiveEvidence) -> None:
    open_ids = tuple(
        blocker.blocker_id for blocker in self._blockers if not blocker.is_satisfied(evidence)
    )
    if open_ids:
        raise LiveTradingBlocked(",".join(open_ids))


async def build_application(settings: Settings) -> Application:
    services = await CompositionRoot(settings).build()
    await services.reconciler.reconcile()
    await services.protection_supervisor.check_once()
    return Application(settings.run_mode, services)
```

- [ ] **Step 4: Verify paper composition and guarded live mode**

Run: `uv run pytest tests/unit/test_live_blockers.py tests/integration/test_paper_bootstrap.py -v`

Run: `uv run trading-os doctor`

Expected: tests PASS; doctor reports dependency health and lists open live blocker IDs without enabling live submission.

- [ ] **Step 5: Commit**

```bash
git add src/trading_os/bootstrap.py src/trading_os/cli.py src/trading_os/live_blockers.py config/live_blockers.yaml tests/unit/test_live_blockers.py tests/integration/test_paper_bootstrap.py
git commit -m "feat: compose paper runtime and guard live trading"
```

### Task 37: Prove the complete paper workflow and publish operator runbooks

**Files:**
- Create: `tests/integration/test_e2e_paper_cycle.py`
- Create: `tests/integration/test_crash_recovery_matrix.py`
- Create: `tests/integration/test_fail_direction_matrix.py`
- Create: `docs/runbooks/paper-operations.md`
- Create: `docs/runbooks/reconciliation.md`
- Create: `docs/runbooks/protection-incidents.md`
- Create: `docs/runbooks/kite-reauthentication.md`
- Create: `docs/runbooks/idle-fx-disposition.md`
- Create: `docs/runbooks/live-promotion.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: the complete application from Tasks 1–36.
- Produces: one end-to-end paper cycle, exhaustive event-boundary recovery proof, §6 fail-direction proof, and non-ambiguous operator procedures.

- [ ] **Step 1: Write the end-to-end acceptance scenario**

```python
# tests/integration/test_e2e_paper_cycle.py
import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_validated_signal_to_protected_fill_to_reconciled_close(paper_app, deterministic_market_day) -> None:
    result = await paper_app.run_cycle(deterministic_market_day)
    assert result.snapshot_validated is True
    assert result.seam_fields == {"hot_path_candidate", "exposure_vector"}
    assert result.order_approved is True
    assert result.fill_recorded is True
    assert result.coverage_confirmed is True
    assert result.reconciliation_clean is True
    assert result.accounting_balanced is True
```

```python
# tests/integration/test_crash_recovery_matrix.py
import pytest


@pytest.mark.integration
@pytest.mark.parametrize("boundary", range(1, 19))
@pytest.mark.asyncio
async def test_crash_at_every_cycle_boundary_recovers_without_duplicate_effect(
    boundary, paper_app_factory, deterministic_market_day
) -> None:
    crashed = await paper_app_factory(crash_after_event=boundary).run_cycle(deterministic_market_day)
    resumed = await paper_app_factory(existing_store=crashed.event_store).resume()
    baseline = await paper_app_factory().run_cycle(deterministic_market_day)
    assert resumed.economic_state == baseline.economic_state
    assert resumed.duplicate_economic_effects == ()
```

- [ ] **Step 2: Run the full integration matrix and capture failures**

Run: `docker compose up -d && uv run alembic upgrade head && uv run pytest tests/integration/test_e2e_paper_cycle.py tests/integration/test_crash_recovery_matrix.py tests/integration/test_fail_direction_matrix.py -v`

Expected: initial failures identify only wiring/runbook gaps; no live broker endpoint is contacted.

- [ ] **Step 3: Complete composition fixtures and write exact runbooks**

Wire the deterministic integration fixture with fake LLM, recorded market data, simulated broker,
Postgres, Valkey, and Neo4j. The fail-direction matrix must assert every finalized §6 row. Runbooks
must state commands, expected evidence, abort conditions, escalation channel, and recovery proof for
paper startup/shutdown, reconciliation mismatch, protection deficit, Kite 403 re-authentication,
idle-FX disposition, backup restore, and promotion. Update README to describe only the final system,
link the spec/plan/runbooks, and show paper-safe commands; do not document a copy-paste live command.

```markdown
## Trigger

State the exact alert, event type, and rule ID that opens this runbook.

## Safe actions

List commands that are read-only or exposure-reducing and the evidence each command must return.

## Abort conditions

State the broker, data, credential, or reconciliation result that requires HALT and escalation.

## Recovery proof

Require broker custody, event projection, protective coverage, and accounting to reconcile before resume.
```

- [ ] **Step 4: Run complete verification**

Run: `uv run ruff check .`

Expected: exit 0.

Run: `uv run mypy src`

Expected: exit 0 with strict typing.

Run: `uv run pytest tests/unit tests/contract -v`

Expected: all tests PASS with no network credentials.

Run: `docker compose up -d && uv run alembic upgrade head && uv run pytest tests/integration -v -m integration`

Expected: all non-live integration tests PASS; Alpaca paper test is skipped unless its explicit paper credential flag is set; no Kite live order is placed.

- [ ] **Step 5: Commit**

```bash
git add tests/integration docs/runbooks README.md
git commit -m "test: prove complete recoverable paper workflow"
```

---

## Final Acceptance Checklist

- [ ] The D30 import/seam tests prove that changing or injecting any disallowed LLM field cannot alter sizing, risk, price, exits, compliance, or kill state.
- [ ] The rule-null compiles and runs with the LLM/KG/calibration services unavailable.
- [ ] Every hot-path decision references a sealed `ValidatedDataSnapshotId` and frozen rule/config versions.
- [ ] Event replay after a Valkey flush produces the same projection hash.
- [ ] Crash injection at every EOD event boundary produces no duplicate economic broker effect.
- [ ] Every open simulated/paper position has broker-confirmed protective quantity covering reconciled quantity, or its symbol is `REDUCING/HALTED_UNVERIFIED`.
- [ ] India and US jobs cannot reserve the same cash/risk capacity from one global snapshot version.
- [ ] India and US compliance tests cover every D19 pre-remittance, pre-order, post-event, periodic, and pre-live rule.
- [ ] Accounting balances in native currency and INR without summing live risk marks into realized equity/FX ledgers.
- [ ] Mandatory COVID-2020 and Russia/Ukraine-2022 KG replays pass against as-of graph/data versions.
- [ ] The promotion manifest is written before the paper campaign and cannot be edited in place.
- [ ] All unit and fixture contract tests run without network credentials; CI has no live Kite submission path.
- [ ] `ruff`, strict `mypy`, unit, contract, and non-live integration suites all pass.
- [ ] Live mode remains blocked until every legal, broker, promotion, operational, and backup-restoration attestation is current and bound to the intended accounts/configuration.

## Recommended Execution Boundaries

1. Complete Tasks 1–11 and review the deterministic/event-sourced foundation before adding market data.
2. Complete Tasks 12–17 and review D4 containment, snapshot correctness, rule-null independence, and KG admission.
3. Complete Tasks 18–28 and run the complete broker/protection/fail-direction contract suite.
4. Complete Tasks 29–37 and run the full paper acceptance matrix.

Do not start a later milestone while the preceding milestone's tests or review findings remain open.
