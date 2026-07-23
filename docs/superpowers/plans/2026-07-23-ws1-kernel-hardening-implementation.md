# WS-1 Kernel Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the partial kernel types, scattered external protocols, and
free-form events with one strict typed foundation while preserving the shipped
account-partitioned safety architecture.

**Architecture:** Harden existing modules in dependency order. External values
are parsed once by adapters; internal code uses frozen typed identifiers,
finite-Decimal values, canonical order/fill models, small capability ports, and
closed versioned events. Event envelopes own fact identity and time, while the
event store alone owns stream location and optimistic versioning.

**Tech Stack:** Python 3.11+, Pydantic v2 frozen models, `Decimal`,
`typing.Protocol`, SQLAlchemy async, PostgreSQL JSONB, pytest/pytest-asyncio,
Hypothesis, mypy strict, and Ruff.

## Global Constraints

- Work only in the isolated `codex/ws1-kernel-hardening-planning` worktree.
- Preserve `AccountPortfolioSnapshot` and `OwnerPortfolioCut`; never introduce
  `GlobalPortfolioSnapshot`.
- Preserve account-generation-scoped kill state and `(account_id, cas_version)`
  reservation ownership.
- No executable number crosses the categorical evidence seam. Money, price,
  quantity, and executable ratios use finite `Decimal`; binary float is confined
  to statistical evaluation code.
- The kernel imports no broker, persistence, framework, portfolio, policy,
  accounting, or deployment module.
- Use Pydantic v2 frozen models with `extra="forbid"` at domain boundaries.
- Use string-wire identifier value objects with `.new()` and `.parse()`.
- Use canonical snake-case event names and immutable semantic schemas such as
  `order_intent_created.v1`.
- Do not add legacy aliases, re-export old port paths, dual numeric fields, a
  historical decoder, a data migration, or a second event model.
- Preserve the existing PostgreSQL table shape: empty stream version `0`, first
  committed event version `1`.
- The default gate is offline and deterministic. PostgreSQL, live service, and
  network tests are explicitly excluded and marked integration.
- TDD red → green. Before each task's single final commit, run specification
  review and code-quality review on the uncommitted diff, fix findings, and
  rerun the task gate.
- Keep `CONTEXT.md` glossary-only. ADR-0011 is the accepted durable event
  versioning decision.

---

## File map

### Kernel

- `src/trading_os/kernel/ids.py`: all type-distinct string-wire identifiers.
- `src/trading_os/kernel/values.py`: strict Decimal value objects and shared
  closed enums.
- `src/trading_os/kernel/event_payloads.py`: one frozen payload model per event
  schema.
- `src/trading_os/kernel/events.py`: `EventType`, `EventSchema`,
  `EventEnvelope`, `StoredEvent`, and schema derivation.

### Subject models and services

- `src/trading_os/brokers/models.py`: normalized observations, requests,
  acknowledgements, and fills.
- `src/trading_os/brokers/{alpaca,kite}.py`: raw-wire parsing and outbound broker
  conversion.
- `src/trading_os/execution/{kill_state,protection,reservations,coordinator}.py`:
  account-scoped execution state and intent ordering.
- `src/trading_os/decision/{sizing,risk,compliance}.py`,
  `src/trading_os/policy/models.py`, and
  `src/trading_os/portfolio/{models,analysis,projector,normalizer}.py`:
  executable numeric callers converted to the kernel authority.

### External ports

- `src/trading_os/ports/clock.py`
- `src/trading_os/ports/calendar.py`
- `src/trading_os/ports/market_data.py`
- `src/trading_os/ports/fx.py`
- `src/trading_os/ports/security_master.py`
- `src/trading_os/ports/graph.py`
- `src/trading_os/ports/event_store.py`
- `src/trading_os/ports/state_cache.py`
- `src/trading_os/ports/broker.py`
- `src/trading_os/ports/llm.py`
- `src/trading_os/ports/secrets.py`
- `src/trading_os/ports/hitl.py`
- `src/trading_os/ports/notifier.py`
- `src/trading_os/ports/__init__.py`

### Persistence and tests

- `src/trading_os/ledger/memory.py`: deterministic `InMemoryEventStore`.
- `src/trading_os/ledger/store.py`: PostgreSQL `PostgresEventStore`.
- `src/trading_os/ledger/tables.py`: typed row serialization/deserialization.
- `tests/fakes/ports.py`: reusable deterministic fakes for all thirteen ports.
- `tests/contract/ledger/contract.py`: shared event-store behavioral assertions.
- `tests/unit/kernel/`: value and event model tests.
- `tests/unit/ports/`: protocol/fake tests.
- `tests/contract/brokers/`: normalized broker contract.
- `tests/integration/ledger/`: PostgreSQL store contract and append-only guard.

---

## Execution preflight

- [ ] Confirm the implementation starts from the approved planning commit in the
  isolated worktree:

```bash
git branch --show-current
git status --short
git log -1 --oneline
```

Expected: branch `codex/ws1-kernel-hardening-planning`, clean status, and the
approved plan commit at `HEAD`.

- [ ] Install the locked project and development dependencies:

```bash
uv sync --extra dev
```

Expected: exit code `0`; no dependency or project file changes.

- [ ] Establish the offline baseline before the first red test:

```bash
uv run ruff check src tests
uv run mypy src/trading_os
uv run pytest tests/unit tests/contract tests/live_readiness -q
```

Expected: all commands PASS. If they do not, diagnose and record the pre-existing
failure before changing WS-1 code.

---

### Task 1: Replace bare string aliases with identifier value objects

**Covers:** V1 Task 2, identifier half.

**Files:**

- Modify: `src/trading_os/kernel/ids.py`
- Create: `tests/unit/kernel/test_ids.py`
- Modify identifier construction in:
  `src/trading_os/brokers/alpaca.py`,
  `src/trading_os/brokers/fake.py`,
  `src/trading_os/brokers/kite.py`,
  `src/trading_os/brokers/mapping.py`,
  `src/trading_os/brokers/models.py`,
  `src/trading_os/decision/models.py`,
  `src/trading_os/discovery/models.py`,
  `src/trading_os/discovery/momentum.py`,
  `src/trading_os/discovery/registry.py`,
  `src/trading_os/identity/models.py`,
  `src/trading_os/kernel/events.py`,
  `src/trading_os/market_data/models.py`,
  `src/trading_os/market_data/snapshot.py`,
  `src/trading_os/market_data/testing.py`,
  `src/trading_os/policy/models.py`,
  `src/trading_os/portfolio/analysis.py`,
  `src/trading_os/portfolio/models.py`,
  `src/trading_os/portfolio/projector.py`,
  `src/trading_os/portfolio/snapshot.py`,
  `src/trading_os/tradability/builder.py`,
  `src/trading_os/tradability/models.py`
- Modify:
  `tests/contract/brokers/contract.py`,
  `tests/contract/brokers/test_alpaca_read_contract.py`,
  `tests/contract/brokers/test_alpaca_write_contract.py`,
  `tests/contract/brokers/test_fake_contract.py`,
  `tests/contract/brokers/test_kite_read_contract.py`,
  `tests/contract/brokers/test_kite_write_contract.py`,
  `tests/integration/execution/test_coordinator.py`,
  `tests/integration/ontology/test_relational_fallback.py`,
  `tests/unit/discovery/test_coverage.py`,
  `tests/unit/discovery/test_momentum.py`,
  `tests/unit/identity/test_authority.py`,
  `tests/unit/kernel/test_events.py`,
  `tests/unit/market_data/test_adjustments.py`,
  `tests/unit/market_data/test_snapshot.py`,
  `tests/unit/policy/test_compliance_release.py`,
  `tests/unit/policy/test_releases.py`,
  `tests/unit/portfolio/test_analysis_gate.py`,
  `tests/unit/portfolio/test_projector.py`,
  `tests/unit/research/test_evidence_boundary.py`,
  `tests/unit/tradability/test_builder.py`

**Interfaces:**

- Consumes: Pydantic v2 and UUID generation.
- Produces:
  `AccountId`, `InstrumentId`, `SnapshotId`,
  `ValidatedDataSnapshotId`, `SemanticSnapshotId`, `ReleaseId`, `EventId`,
  `TenantId`, `IntentId`, `StrategyBookId`, and `PositionEpisodeId`, each with
  `new() -> Self`, `parse(value: str) -> Self`, and `str(value) -> str`.

- [ ] **Step 1: Write failing identifier contract tests**

```python
# tests/unit/kernel/test_ids.py
import pytest
from pydantic import ValidationError

from trading_os.kernel.ids import (
    AccountId,
    EventId,
    InstrumentId,
    IntentId,
    PositionEpisodeId,
    ReleaseId,
    SemanticSnapshotId,
    SnapshotId,
    StrategyBookId,
    TenantId,
    ValidatedDataSnapshotId,
)

ID_TYPES = (
    AccountId,
    InstrumentId,
    SnapshotId,
    ValidatedDataSnapshotId,
    SemanticSnapshotId,
    ReleaseId,
    EventId,
    TenantId,
    IntentId,
    StrategyBookId,
    PositionEpisodeId,
)


@pytest.mark.parametrize("id_type", ID_TYPES)
def test_identifier_round_trips_as_a_json_string(id_type: type[AccountId]) -> None:
    value = id_type.parse("stable-external-id")
    assert str(value) == "stable-external-id"
    assert id_type.model_validate_json(value.model_dump_json()) == value


def test_new_identifier_uses_stable_uuid_text() -> None:
    value = IntentId.new()
    assert IntentId.parse(str(value)) == value


def test_identifier_types_are_not_interchangeable_or_raw_strings() -> None:
    account = AccountId.parse("same")
    assert account != InstrumentId.parse("same")
    assert account != "same"
    assert len({account, AccountId.parse("same")}) == 1


@pytest.mark.parametrize("bad", ["", " ", " padded", "padded "])
def test_identifier_rejects_non_canonical_text(bad: str) -> None:
    with pytest.raises(ValidationError):
        AccountId.parse(bad)
```

- [ ] **Step 2: Run the test and confirm the old aliases fail**

Run:

```bash
uv run pytest tests/unit/kernel/test_ids.py -v
```

Expected: FAIL because `IntentId`, `StrategyBookId`, and
`PositionEpisodeId` do not exist and current aliases have no `.parse()`.

- [ ] **Step 3: Implement the complete identifier roster**

```python
# src/trading_os/kernel/ids.py
from typing import Self
from uuid import uuid4

from pydantic import ConfigDict, RootModel, field_validator


class _Id(RootModel[str]):
    model_config = ConfigDict(frozen=True)

    @field_validator("root")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value or value != value.strip():
            raise ValueError("identifier must be non-empty canonical text")
        return value

    @classmethod
    def new(cls) -> Self:
        return cls.parse(str(uuid4()))

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls.model_validate(value, strict=True)

    def __str__(self) -> str:
        return self.root


class AccountId(_Id): ...
class InstrumentId(_Id): ...
class SnapshotId(_Id): ...
class ValidatedDataSnapshotId(_Id): ...
class SemanticSnapshotId(_Id): ...
class ReleaseId(_Id): ...
class EventId(_Id): ...
class TenantId(_Id): ...
class IntentId(_Id): ...
class StrategyBookId(_Id): ...
class PositionEpisodeId(_Id): ...
```

- [ ] **Step 4: Convert every repository caller atomically**

Use these exact construction rules throughout the files listed above:

```python
# Existing external or fixture identity
account_id = AccountId.parse("acct-1")
instrument_id = InstrumentId.parse("NSE:INE009A01021")
release_id = ReleaseId.parse("capital-v1")

# OS-created identity
event_id = EventId.new()
intent_id = IntentId.new()

# Wire/database boundary
wire_value = str(account_id)
loaded = AccountId.parse(database_value)
```

Do not retain `NewType`, `cast()`, equality to raw strings, or
`AccountId(raw_value)` call sites.

- [ ] **Step 5: Run the identifier and affected-domain gate**

Run:

```bash
uv run pytest tests/unit/kernel/test_ids.py tests/unit/identity tests/unit/market_data tests/unit/portfolio tests/unit/policy tests/unit/tradability tests/unit/discovery -q
uv run mypy src/trading_os
uv run ruff check src tests
```

Expected: all commands PASS; mypy reports no raw-string assignment to an ID.

- [ ] **Step 6: Run the two review gates**

Specification review checks the complete roster, wire-string serialization,
cross-type inequality, and absence of compatibility aliases. Code-quality review
checks Pydantic v2 idioms, hashing, validation messages, and caller consistency.
Fix all findings and rerun Step 5.

- [ ] **Step 7: Commit**

```bash
git add src/trading_os/kernel/ids.py src/trading_os tests
git commit -m "refactor: harden kernel identifiers"
```

---

### Task 2: Establish strict Decimal values and canonical execution states

**Covers:** V1 Task 2, numeric/enumeration half, and the required in-process
caller cutover.

**Files:**

- Modify: `src/trading_os/kernel/values.py`
- Modify: `src/trading_os/decision/sizing.py`
- Modify: `src/trading_os/decision/risk.py`
- Modify: `src/trading_os/decision/compliance.py`
- Modify: `src/trading_os/identity/models.py`
- Modify: `src/trading_os/market_data/models.py`
- Modify: `src/trading_os/policy/models.py`
- Modify: `src/trading_os/portfolio/models.py`
- Modify: `src/trading_os/portfolio/analysis.py`
- Modify: `src/trading_os/portfolio/projector.py`
- Modify: `src/trading_os/portfolio/normalizer.py`
- Modify: `src/trading_os/research/models.py`
- Modify: `src/trading_os/retrospective/models.py`
- Modify: `src/trading_os/retrospective/linker.py`
- Modify: `src/trading_os/execution/kill_state.py`
- Modify: `src/trading_os/execution/protection.py`
- Modify: `src/trading_os/execution/reconciliation.py`
- Modify: `src/trading_os/execution/reservations.py`
- Modify: `tests/unit/kernel/test_values.py`
- Modify: `tests/unit/decision/test_risk.py`
- Modify: `tests/unit/decision/test_sizing.py`
- Modify: `tests/unit/decision/test_us_compliance.py`
- Modify: `tests/unit/identity/test_authority.py`
- Modify: `tests/unit/market_data/test_adjustments.py`
- Modify: `tests/unit/market_data/test_snapshot.py`
- Modify: `tests/unit/policy/test_releases.py`
- Modify: `tests/unit/portfolio/test_analysis_gate.py`
- Modify: `tests/unit/portfolio/test_completeness.py`
- Modify: `tests/unit/portfolio/test_normalizer.py`
- Modify: `tests/unit/portfolio/test_projector.py`
- Modify: `tests/unit/research/test_evidence_boundary.py`
- Modify: `tests/unit/retrospective/test_linker.py`
- Modify: `tests/unit/execution/test_kill_state.py`
- Modify: `tests/integration/execution/test_protection.py`
- Modify: `tests/integration/execution/test_reconciliation.py`
- Modify: `tests/integration/execution/test_reservations.py`
- Create: `tests/unit/kernel/test_numeric_boundaries.py`

**Interfaces:**

- Consumes: identifier objects from Task 1.
- Produces:
  `Currency`, `Market`, `Direction`, `OrderSide`, `OrderType`, `OrderStatus`,
  `KillState`, `CoverageState`, `QuantityUnit`, `Money`, `Price`, and
  `Quantity`; `UtcDateTime`; `validate_order_terms()`; plus
  `AccountKillState`.

- [ ] **Step 1: Write failing strict-value tests**

```python
# tests/unit/kernel/test_values.py
from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading_os.kernel.values import Currency, Money, Price, Quantity, QuantityUnit


def test_money_addition_requires_matching_currency() -> None:
    with pytest.raises(ValueError, match="currency mismatch"):
        _ = Money(amount=Decimal("10.00"), currency=Currency.INR) + Money(
            amount=Decimal("1.00"), currency=Currency.USD
        )


@pytest.mark.parametrize("model", [Money, Price, Quantity])
def test_executable_values_reject_binary_float(model: type[Money]) -> None:
    kwargs = {"amount": 1.5, "currency": Currency.INR}
    if model is Price:
        kwargs = {"value": 1.5, "currency": Currency.INR}
    if model is Quantity:
        kwargs = {"value": 1.5, "unit": QuantityUnit.SHARES}
    with pytest.raises(ValidationError):
        model.model_validate(kwargs)


@pytest.mark.parametrize("bad", [Decimal("NaN"), Decimal("Infinity")])
def test_executable_values_reject_non_finite_decimal(bad: Decimal) -> None:
    with pytest.raises(ValidationError):
        Money(amount=bad, currency=Currency.INR)


def test_price_is_positive_and_quantity_may_be_zero() -> None:
    with pytest.raises(ValidationError):
        Price(value=Decimal("0"), currency=Currency.USD)
    assert Quantity(value=Decimal("0"), unit=QuantityUnit.SHARES).value == 0
```

- [ ] **Step 2: Write failing state-vocabulary tests**

```python
# tests/unit/execution/test_kill_state.py
from trading_os.execution.kill_state import AccountKillState, transition
from trading_os.kernel.ids import AccountId
from trading_os.kernel.values import KillState


def test_safety_fault_advances_account_generation_and_fences_entries() -> None:
    state = AccountKillState.active(AccountId.parse("acct-1"), generation=1)
    stopped = transition(state, "critical_portfolio_stale")
    assert stopped.state is KillState.ENTRY_DISABLED
    assert stopped.generation == 2
    assert stopped.account_id == state.account_id


def test_halted_unverified_remains_account_scoped() -> None:
    state = AccountKillState(
        account_id=AccountId.parse("acct-1"),
        generation=3,
        state=KillState.HALTED_UNVERIFIED,
    )
    assert state.may_increase_exposure is False
    assert state.may_reconcile is True
```

- [ ] **Step 3: Run the tests and observe the old integer/string models fail**

Run:

```bash
uv run pytest tests/unit/kernel/test_values.py tests/unit/execution/test_kill_state.py -v
```

Expected: FAIL because `Price`, `Currency`, and kernel `KillState` are absent and
`Money` still exposes `minor_units`.

- [ ] **Step 4: Implement strict values and the closed vocabulary**

Implement in `kernel/values.py`:

```python
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, Strict


def _require_finite(value: Decimal) -> Decimal:
    if not value.is_finite():
        raise ValueError("value must be finite")
    return value


StrictFiniteDecimal = Annotated[
    Decimal,
    Strict(),
    AfterValidator(_require_finite),
]


def _require_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("datetime must be timezone-aware UTC")
    return value


UtcDateTime = Annotated[datetime, AfterValidator(_require_utc)]


class Currency(StrEnum):
    INR = "INR"
    USD = "USD"


class Market(StrEnum):
    INDIA = "india"
    US = "us"


class Direction(StrEnum):
    LONG = "long"
    FLAT = "flat"


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    OUTCOME_UNKNOWN = "outcome_unknown"


class KillState(StrEnum):
    ACTIVE = "active"
    ENTRY_DISABLED = "entry_disabled"
    REDUCE_ONLY = "reduce_only"
    MANAGEMENT_ONLY = "management_only"
    HALTED = "halted"
    HALTED_UNVERIFIED = "halted_unverified"


class CoverageState(StrEnum):
    UNREQUIRED = "unrequired"
    PENDING_FILL = "pending_fill"
    SUBMITTED_UNCONFIRMED = "submitted_unconfirmed"
    PARTIALLY_FILLED_UNPROTECTED = "partially_filled_unprotected"
    PROTECTION_PENDING = "protection_pending"
    PROTECTED = "protected"
    DEGRADED = "degraded"
    FAILED = "failed"
    CLOSED = "closed"


class QuantityUnit(StrEnum):
    SHARES = "shares"
    CONTRACTS = "contracts"
    BASE_CURRENCY = "base_currency"
    QUOTE_CURRENCY = "quote_currency"


class Money(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    amount: StrictFiniteDecimal
    currency: Currency

    def _matching(self, other: Self) -> None:
        if self.currency is not other.currency:
            raise ValueError("currency mismatch")

    def __add__(self, other: Self) -> Self:
        self._matching(other)
        return type(self)(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: Self) -> Self:
        self._matching(other)
        return type(self)(amount=self.amount - other.amount, currency=self.currency)

    def to_minor_units(self) -> int:
        scaled = self.amount * Decimal(100)
        if scaled != scaled.to_integral_value():
            raise ValueError("amount is not representable in V1 minor units")
        return int(scaled)


class Price(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    value: StrictFiniteDecimal = Field(gt=Decimal("0"))
    currency: Currency


class Quantity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    value: StrictFiniteDecimal = Field(ge=Decimal("0"))
    unit: QuantityUnit


def validate_order_terms(
    *,
    market: Market,
    side: OrderSide,
    quantity: Quantity,
    order_type: OrderType,
    limit_price: Price | None,
    stop_price: Price | None,
    reduce_only: bool,
) -> None:
    if side is OrderSide.BUY and reduce_only:
        raise ValueError("buy orders cannot be reduce_only in long-only V1")
    if side is OrderSide.SELL and not reduce_only:
        raise ValueError("sell orders must be reduce_only in long-only V1")
    expected = {
        OrderType.LIMIT: (True, False),
        OrderType.STOP: (False, True),
        OrderType.STOP_LIMIT: (True, True),
    }[order_type]
    prices = tuple(price for price in (limit_price, stop_price) if price is not None)
    if (limit_price is not None, stop_price is not None) != expected:
        raise ValueError("order prices do not match order type")
    expected_currency = {Market.INDIA: Currency.INR, Market.US: Currency.USD}[market]
    if any(price.currency is not expected_currency for price in prices):
        raise ValueError("price currency does not match market")
    if quantity.unit is not QuantityUnit.SHARES or quantity.value <= 0:
        raise ValueError("order quantity must be positive shares")
```

- [ ] **Step 5: Migrate executable numeric callers without changing policy**

Use typed inputs/outputs, not parallel fields. The sizing core becomes:

```python
class SizingInput(BaseModel, frozen=True):
    available_cash: Money
    capital: Money
    risk_fraction_ppm: int = Field(gt=0, le=1_000_000)
    entry_price: Price
    stop_price: Price
    max_symbol: Money
    lot_size: Quantity


class ProvisionalSize(BaseModel, frozen=True):
    quantity: Quantity
    notional: Money
    risk: Money


def _lot_floor(value: Decimal, lot: Decimal) -> Decimal:
    return (value // lot) * lot


def size_cash_equity(value: SizingInput) -> ProvisionalSize:
    currencies = {
        value.available_cash.currency,
        value.capital.currency,
        value.entry_price.currency,
        value.stop_price.currency,
        value.max_symbol.currency,
    }
    if len(currencies) != 1:
        raise ValueError("currency mismatch")
    if value.lot_size.unit is not QuantityUnit.SHARES or value.lot_size.value <= 0:
        raise ValueError("lot size must be positive shares")
    risk_per_share = value.entry_price.value - value.stop_price.value
    zero = Quantity(value=Decimal("0"), unit=QuantityUnit.SHARES)
    currency = value.entry_price.currency
    if risk_per_share <= 0:
        return ProvisionalSize(
            quantity=zero,
            notional=Money(amount=Decimal("0"), currency=currency),
            risk=Money(amount=Decimal("0"), currency=currency),
        )
    risk_budget = (
        value.capital.amount * Decimal(value.risk_fraction_ppm) / Decimal(1_000_000)
    )
    raw = min(
        risk_budget / risk_per_share,
        value.available_cash.amount / value.entry_price.value,
        value.max_symbol.amount / value.entry_price.value,
    )
    quantity_value = _lot_floor(raw, value.lot_size.value)
    return ProvisionalSize(
        quantity=Quantity(value=quantity_value, unit=QuantityUnit.SHARES),
        notional=Money(
            amount=quantity_value * value.entry_price.value,
            currency=currency,
        ),
        risk=Money(amount=quantity_value * risk_per_share, currency=currency),
    )
```

Apply this exact field conversion matrix:

| Model/function | Canonical fields |
|---|---|
| `RiskInput` | `provisional_quantity: Quantity`, `entry_price: Price`, `deployed/max_deployed/symbol_exposure/max_symbol: Money`, existing categorical overlay |
| `RiskDecision` | `final_quantity: Quantity`, unchanged reason codes |
| `UsComplianceInput` | `buying_power: Money`, `required: Money`; validator rejects currency mismatch before comparison |
| `CapitalEnvelopeRelease` | `capital: Money`, `max_cumulative_loss: Money`; remove duplicate `currency` and require matching currencies |
| `ExposurePolicyRelease` | `max_deployed_fraction` and `max_symbol_fraction` use `StrictFiniteDecimal` in `(0, 1]` |
| `RiskOverlaySet` and `PortfolioRiskOverlaySet` | `multiplier: StrictFiniteDecimal` in `(0, 1]`; no binary float |
| account/FX metadata | identity and portfolio base currencies plus `FxMark` base/quote fields use `Currency`, never raw ISO strings |
| `PositionBuckets` | every custody/reservation/order bucket is `Quantity` in shares; derived totals return `Quantity` |
| `CashBuckets` | settled, unsettled, broker-available, OS-reserved, pending-debit, and pending-credit are `Money`; remove duplicate currency |
| `PortfolioAnalysis` | sector exposure/cap are `Money`; price map values are `Price`; derived overlay uses Decimal division |
| `ProtectionSupervisor` | covered, filled, observed-stop, and optional guessed-close values are `Quantity` |
| `reconcile_quantity()` | accepts two share `Quantity` values and returns a typed share difference |
| `OrderReservation` | `account_id: AccountId`, `policy_release_ids: tuple[ReleaseId, ...]`, `cash: Money`, `quantity: Quantity`, `risk: Money` |
| retrospective trade models/linker | provisional/final quantities are `Quantity`; broker/OS/unknown P&L values are `Money` |

`ReservationRow.cash_minor`, `ReservationRow.risk_minor`, and its integer SQL
columns remain storage-only; `ReservationStore` calls `Money.to_minor_units()`
explicitly. Portfolio arithmetic constructs new frozen values explicitly and
rejects unit/currency mismatch before addition, subtraction, or comparison.

Rename the execution model to:

```python
class AccountKillState(BaseModel, frozen=True):
    account_id: AccountId
    generation: int = Field(ge=0)
    state: KillState
```

Replace `ProtectionState` with kernel `CoverageState`; replace supervisor
quantity integers with `Quantity`. Do not add enum aliases.

- [ ] **Step 6: Add an explicit no-parallel-authority test**

```python
# tests/unit/kernel/test_numeric_boundaries.py
from trading_os.decision.risk import RiskInput
from trading_os.decision.sizing import SizingInput
from trading_os.execution.reservations import OrderReservation
from trading_os.policy.models import CapitalEnvelopeRelease
from trading_os.portfolio.models import CashBuckets, PositionBuckets
from trading_os.research.models import RiskOverlaySet


def test_domain_models_have_no_minor_unit_or_binary_float_authority() -> None:
    models = (
        SizingInput,
        RiskInput,
        OrderReservation,
        CapitalEnvelopeRelease,
        CashBuckets,
        PositionBuckets,
        RiskOverlaySet,
    )
    for model in models:
        assert not any(name.endswith("_minor") for name in model.model_fields)
    assert RiskOverlaySet.model_fields["multiplier"].annotation is not float
```

- [ ] **Step 7: Run the numeric/state gate**

Run:

```bash
uv run pytest tests/unit/kernel tests/unit/decision tests/unit/identity tests/unit/market_data tests/unit/policy tests/unit/portfolio tests/unit/research tests/unit/retrospective tests/unit/execution -q
uv run mypy src/trading_os
uv run ruff check src tests
make services-up
uv run pytest tests/integration/execution/test_reservations.py tests/integration/execution/test_protection.py -q
make services-down
```

Expected: all commands PASS. Database-backed reservation tests preserve the
same CAS winner and idempotent-release behavior.

- [ ] **Step 8: Run both review gates and commit**

Specification review checks Decimal authority, currency mismatch, state
vocabulary, account scope, and CAS preservation. Code-quality review checks that
arithmetic remains deterministic and no float conversion or duplicate minor-unit
domain field remains. Fix findings, rerun Step 7, then:

```bash
git add src/trading_os tests
git commit -m "refactor: establish strict execution values"
```

---

### Task 3: Harden normalized orders, acknowledgements, fills, and broker edges

**Covers:** V1 Task 4 types.

**Files:**

- Modify: `src/trading_os/brokers/models.py`
- Modify: `src/trading_os/brokers/alpaca.py`
- Modify: `src/trading_os/brokers/kite.py`
- Modify: `src/trading_os/brokers/fake.py`
- Modify: `src/trading_os/brokers/mapping.py`
- Delete: `src/trading_os/execution/models.py`
- Modify: `src/trading_os/execution/coordinator.py`
- Modify: `tests/contract/brokers/contract.py`
- Modify: `tests/contract/brokers/test_alpaca_read_contract.py`
- Modify: `tests/contract/brokers/test_alpaca_write_contract.py`
- Modify: `tests/contract/brokers/test_fake_contract.py`
- Modify: `tests/contract/brokers/test_kite_read_contract.py`
- Modify: `tests/contract/brokers/test_kite_write_contract.py`
- Modify: `tests/integration/execution/test_coordinator.py`
- Modify: `tests/unit/decision/test_india_compliance.py`
- Create: `tests/unit/brokers/__init__.py`
- Create: `tests/unit/brokers/test_models.py`
- Create: `tests/unit/brokers/test_mapping_boundaries.py`

**Interfaces:**

- Consumes: IDs and values from Tasks 1–2.
- Produces:
  `OrderRequest`, `OrderAck`, `Fill`, `PositionObservation`,
  `CashObservation`, `OpenOrderObservation`, and
  `BrokerSnapshotObservation`.

- [ ] **Step 1: Write the failing order truth-table tests**

```python
# tests/unit/brokers/test_models.py
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading_os.brokers.models import Fill, OrderAck, OrderRequest
from trading_os.kernel.ids import (
    AccountId,
    InstrumentId,
    IntentId,
    SnapshotId,
    StrategyBookId,
)
from trading_os.kernel.values import (
    Currency,
    Market,
    Money,
    OrderSide,
    OrderStatus,
    OrderType,
    Price,
    Quantity,
    QuantityUnit,
)


def request(**updates: object) -> OrderRequest:
    values: dict[str, object] = {
        "account_id": AccountId.parse("acct-1"),
        "intent_id": IntentId.parse("intent-1"),
        "instrument_id": InstrumentId.parse("NSE:INE009A01021"),
        "snapshot_id": SnapshotId.parse("snapshot-1"),
        "strategy_book_id": StrategyBookId.parse("book-1"),
        "market": Market.INDIA,
        "side": OrderSide.BUY,
        "quantity": Quantity(value=Decimal("1"), unit=QuantityUnit.SHARES),
        "order_type": OrderType.LIMIT,
        "limit_price": Price(value=Decimal("1500"), currency=Currency.INR),
        "stop_price": None,
        "reduce_only": False,
        "kill_generation": 4,
        "submitted_after": datetime(2026, 7, 23, 10, tzinfo=UTC),
    }
    values.update(updates)
    return OrderRequest.model_validate(values)


def test_sell_must_be_reduce_only_and_buy_cannot_be_reduce_only() -> None:
    with pytest.raises(ValidationError):
        request(side=OrderSide.SELL, reduce_only=False)
    with pytest.raises(ValidationError):
        request(side=OrderSide.BUY, reduce_only=True)
    assert request(side=OrderSide.SELL, reduce_only=True).reduce_only is True


@pytest.mark.parametrize(
    ("order_type", "limit", "stop"),
    [
        (OrderType.LIMIT, True, False),
        (OrderType.STOP, False, True),
        (OrderType.STOP_LIMIT, True, True),
    ],
)
def test_order_type_requires_exact_price_shape(
    order_type: OrderType, limit: bool, stop: bool
) -> None:
    inr = Currency.INR
    value = request(
        order_type=order_type,
        limit_price=Price(value=Decimal("1500"), currency=inr) if limit else None,
        stop_price=Price(value=Decimal("1450"), currency=inr) if stop else None,
    )
    assert (value.limit_price is not None, value.stop_price is not None) == (limit, stop)
```

- [ ] **Step 2: Write failing fill and ambiguity tests**

```python
def test_outcome_unknown_does_not_require_a_broker_order_id() -> None:
    ack = OrderAck(
        intent_id=IntentId.parse("intent-1"),
        broker_order_id=None,
        observed_at=datetime(2026, 7, 23, 10, tzinfo=UTC),
        status=OrderStatus.OUTCOME_UNKNOWN,
    )
    assert ack.broker_order_id is None


def test_fill_is_custody_observation_without_strategy_attribution() -> None:
    fill = Fill(
        account_id=AccountId.parse("acct-1"),
        intent_id=IntentId.parse("intent-1"),
        instrument_id=InstrumentId.parse("NSE:INE009A01021"),
        broker_order_id="broker-order-1",
        broker_fill_id="broker-fill-1",
        side=OrderSide.BUY,
        quantity=Quantity(value=Decimal("1"), unit=QuantityUnit.SHARES),
        price=Price(value=Decimal("1500"), currency=Currency.INR),
        fee=Money(amount=Decimal("2.50"), currency=Currency.INR),
        executed_at=datetime(2026, 7, 23, 10, tzinfo=UTC),
        received_at=datetime(2026, 7, 23, 10, 0, 1, tzinfo=UTC),
        source_record_hash="sha256:fixture",
    )
    assert "strategy_book_id" not in fill.model_fields
    assert "position_episode_id" not in fill.model_fields
```

- [ ] **Step 3: Run tests and confirm the current broker models fail**

Run:

```bash
uv run pytest tests/unit/brokers/test_models.py -v
```

Expected: FAIL because `Fill`, `reduce_only`, `STOP`, typed prices, and
`OUTCOME_UNKNOWN` are absent.

- [ ] **Step 4: Implement canonical broker models**

The required request and result shapes are:

```python
class BrokerModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class OrderRequest(BrokerModel):
    account_id: AccountId
    intent_id: IntentId
    instrument_id: InstrumentId
    snapshot_id: SnapshotId
    strategy_book_id: StrategyBookId
    market: Market
    side: OrderSide
    quantity: Quantity
    order_type: OrderType
    limit_price: Price | None = None
    stop_price: Price | None = None
    reduce_only: bool
    kill_generation: int = Field(ge=0)
    submitted_after: UtcDateTime

    @model_validator(mode="after")
    def enforce_long_only_and_price_shape(self) -> "OrderRequest":
        validate_order_terms(
            market=self.market,
            side=self.side,
            quantity=self.quantity,
            order_type=self.order_type,
            limit_price=self.limit_price,
            stop_price=self.stop_price,
            reduce_only=self.reduce_only,
        )
        return self


class OrderAck(BrokerModel):
    intent_id: IntentId
    broker_order_id: str | None
    observed_at: UtcDateTime
    status: OrderStatus


class Fill(BrokerModel):
    account_id: AccountId
    intent_id: IntentId
    instrument_id: InstrumentId
    broker_order_id: str
    broker_fill_id: str
    side: OrderSide
    quantity: Quantity
    price: Price
    fee: Money | None = None
    executed_at: UtcDateTime
    received_at: UtcDateTime
    source_record_hash: str

    @model_validator(mode="after")
    def validate_fill(self) -> "Fill":
        if self.quantity.unit is not QuantityUnit.SHARES or self.quantity.value <= 0:
            raise ValueError("fill quantity must be positive shares")
        if self.fee is not None and self.fee.currency is not self.price.currency:
            raise ValueError("currency mismatch")
        if self.received_at < self.executed_at:
            raise ValueError("fill cannot be received before execution")
        return self
```

Use typed `Quantity`, `Price`, `Money`, `Currency`, and `OrderStatus` in all
broker observation models:

| Model | Canonical fields |
|---|---|
| `PositionObservation` | instrument ID; five share `Quantity` buckets; optional average-cost and last `Price`; source hash |
| `CashObservation` | settled, broker-available, and unsettled `Money`; source hash |
| `OpenOrderObservation` | broker order ID, optional `IntentId`, instrument ID, side, remaining share `Quantity`, optional limit `Price`, and `OrderStatus` |
| `BrokerSnapshotObservation` | snapshot/account IDs, broker name, optional observed UTC time, received UTC time, immutable observation tuples, and missing-segment set |

Remove duplicate currency fields where the value object carries currency. Remove
the duplicate order enums from `brokers/models.py` and delete the unused
`execution.models.OrderIntent`.

- [ ] **Step 5: Convert broker adapters at their edges**

Replace float/minor-unit parsing with:

```python
def _decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _shares(value: object) -> Quantity:
    parsed = _decimal(value)
    assert parsed is not None
    return Quantity(value=parsed, unit=QuantityUnit.SHARES)
```

Pure snapshot mappers receive `received_at` explicitly in tests. Outbound
adapters send `str(request.quantity.value)`, `str(request.limit_price.value)`,
and `str(request.stop_price.value)` as required by their SDKs. They map
`IntentId` to `client_order_id`/Kite tag. No `float()`, `/ 100`, or
`*_minor` conversion remains in broker code.

- [ ] **Step 6: Update and run the broker contract**

Update `BrokerContract._request()` to construct the canonical request. Add
contract assertions that repeat submission of the same `IntentId` is
idempotent, reuse with different content fails, and cancellation is idempotent.

Run:

```bash
uv run pytest tests/unit/brokers tests/contract/brokers -q
uv run mypy src/trading_os
uv run ruff check src tests
make services-up
uv run pytest tests/integration/execution/test_coordinator.py -q
make services-down
```

Expected: all commands PASS; recorded Kite/Alpaca fixtures map without binary
float and coordinator crash/restart behavior remains intact.

- [ ] **Step 7: Run both review gates and commit**

Specification review checks every order truth-table row, fill/attribution
separation, `IntentId` mapping, and `OUTCOME_UNKNOWN`. Quality review checks
adapter parsing, timezone validation, no duplicate fields, and contract
coverage. Fix findings, rerun Step 6, then:

```bash
git add src/trading_os/brokers src/trading_os/execution tests
git commit -m "refactor: harden broker order and fill models"
```

---

### Task 4: Replace free-form operational events with a closed versioned catalogue

**Covers:** V1 Task 6, event model and catalogue.

**Files:**

- Create: `src/trading_os/kernel/event_payloads.py`
- Modify: `src/trading_os/kernel/events.py`
- Modify: `src/trading_os/ledger/tables.py`
- Modify: `src/trading_os/app/container.py`
- Modify: `src/trading_os/execution/coordinator.py`
- Modify: `tests/unit/kernel/test_events.py`
- Create: `tests/unit/kernel/test_event_catalogue.py`
- Modify: `tests/integration/app/test_cycle.py`
- Modify: `tests/integration/execution/test_coordinator.py`
- Modify: `tests/integration/ledger/test_event_store.py`
- Modify: `tests/replay/test_two_broker_cycle.py`

**Interfaces:**

- Consumes: Tasks 1–3 kernel and order vocabulary.
- Produces:
  `EventType`, `EventSchema`, `OperationalPayload`, `EventEnvelope`,
  `StoredEvent`, and 22 `v1` payload models.

- [ ] **Step 1: Write failing catalogue-completeness tests**

```python
# tests/unit/kernel/test_event_catalogue.py
from trading_os.kernel.events import (
    EVENT_TYPE_BY_SCHEMA,
    PAYLOAD_TYPE_BY_SCHEMA,
    EventSchema,
    EventType,
)


RECOVERY_TYPES = {
    "position_episode_opened",
    "position_episode_closed",
    "fill_allocated",
    "stop_intent_placed",
    "stop_ack_received",
    "protection_coverage_changed",
    "trail_ratcheted",
    "time_stop_deadline_set",
    "entry_regime_recorded",
    "approval_decision",
    "order_reservation_committed",
    "order_reservation_released",
    "strategy_attribution",
    "fx_lot_opened",
    "fx_lot_consumed",
    "idle_fx_lot_opened",
    "idle_fx_lot_disposed",
    "calibration_recorded",
    "kill_switch_generation_bumped",
}


def test_catalogue_is_closed_complete_and_one_to_one() -> None:
    assert RECOVERY_TYPES <= {item.value for item in EventType}
    assert len(EventType) == 22
    assert len(EventSchema) == 22
    assert set(EVENT_TYPE_BY_SCHEMA) == set(EventSchema)
    assert set(PAYLOAD_TYPE_BY_SCHEMA) == set(EventSchema)
    assert len(set(PAYLOAD_TYPE_BY_SCHEMA.values())) == 22
```

- [ ] **Step 2: Write failing derivation and rejection tests**

```python
def test_envelope_derives_type_and_version_from_payload() -> None:
    payload = KillSwitchGenerationBumpedV1(
        account_id=AccountId.parse("acct-1"),
        previous_generation=3,
        new_generation=4,
        previous_state=KillState.ACTIVE,
        new_state=KillState.HALTED,
        reason="owner_emergency_stop",
        bumped_at=datetime(2026, 7, 23, 10, tzinfo=UTC),
    )
    envelope = EventEnvelope.new(
        payload=payload,
        recorded_at=datetime(2026, 7, 23, 10, tzinfo=UTC),
    )
    assert envelope.event_type is EventType.KILL_SWITCH_GENERATION_BUMPED
    assert envelope.schema_version == 1


def test_arbitrary_event_name_and_dictionary_payload_are_not_constructible() -> None:
    assert "Other" not in {item.value for item in EventType}
    with pytest.raises(ValidationError):
        EventEnvelope.model_validate(
            {
                "event_id": str(EventId.new()),
                "event_type": "Other",
                "schema_version": 1,
                "payload": {},
                "recorded_at": "2026-07-23T10:00:00Z",
            }
        )
```

- [ ] **Step 3: Run tests and confirm free-form events fail**

Run:

```bash
uv run pytest tests/unit/kernel/test_events.py tests/unit/kernel/test_event_catalogue.py -v
```

Expected: FAIL because the catalogue, schemas, and typed payload union do not
exist.

- [ ] **Step 4: Implement all payload schemas**

Use a frozen base with a literal `schema` discriminator and define these exact
payload identities:

```python
from datetime import date
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from trading_os.kernel.ids import (
    AccountId,
    InstrumentId,
    IntentId,
    PositionEpisodeId,
    ReleaseId,
    SnapshotId,
    StrategyBookId,
)
from trading_os.kernel.values import (
    CoverageState,
    KillState,
    Market,
    Money,
    OrderSide,
    OrderStatus,
    OrderType,
    Price,
    Quantity,
    QuantityUnit,
    UtcDateTime,
    validate_order_terms,
)


class EventPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


def _non_empty_text(value: str) -> str:
    if not value or value != value.strip():
        raise ValueError("reference must be non-empty canonical text")
    return value


def _positive_shares(value: Quantity) -> Quantity:
    if value.unit is not QuantityUnit.SHARES or value.value <= 0:
        raise ValueError("quantity must be positive shares")
    return value


NonEmptyText = Annotated[str, AfterValidator(_non_empty_text)]
PositiveShares = Annotated[Quantity, AfterValidator(_positive_shares)]


class CycleCompletedV1(EventPayload):
    schema: Literal["cycle_completed.v1"] = "cycle_completed.v1"
    account_id: AccountId
    cycle_id: NonEmptyText
    cycle_key: NonEmptyText
    order_intent_ids: tuple[IntentId, ...]
    live_writes_enabled: bool


class OrderIntentCreatedV1(EventPayload):
    schema: Literal["order_intent_created.v1"] = "order_intent_created.v1"
    account_id: AccountId
    intent_id: IntentId
    instrument_id: InstrumentId
    snapshot_id: SnapshotId
    strategy_book_id: StrategyBookId
    market: Market
    side: OrderSide
    quantity: PositiveShares
    order_type: OrderType
    limit_price: Price | None
    stop_price: Price | None
    reduce_only: bool
    kill_generation: int = Field(ge=0)
    submitted_after: UtcDateTime

    @model_validator(mode="after")
    def validate_order(self) -> "OrderIntentCreatedV1":
        validate_order_terms(
            market=self.market,
            side=self.side,
            quantity=self.quantity,
            order_type=self.order_type,
            limit_price=self.limit_price,
            stop_price=self.stop_price,
            reduce_only=self.reduce_only,
        )
        return self


class OrderAcknowledgedV1(EventPayload):
    schema: Literal["order_acknowledged.v1"] = "order_acknowledged.v1"
    account_id: AccountId
    intent_id: IntentId
    broker_order_id: NonEmptyText | None
    status: OrderStatus
    observed_at: UtcDateTime


class PositionEpisodeOpenedV1(EventPayload):
    schema: Literal["position_episode_opened.v1"] = "position_episode_opened.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    instrument_id: InstrumentId
    opening_fill_id: NonEmptyText
    opened_at: UtcDateTime


class PositionEpisodeClosedV1(EventPayload):
    schema: Literal["position_episode_closed.v1"] = "position_episode_closed.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    instrument_id: InstrumentId
    closing_fill_id: NonEmptyText | None
    reason: NonEmptyText
    closed_at: UtcDateTime


class FillAllocatedV1(EventPayload):
    schema: Literal["fill_allocated.v1"] = "fill_allocated.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    intent_id: IntentId
    broker_fill_id: NonEmptyText
    strategy_book_id: StrategyBookId
    quantity: PositiveShares
    allocated_at: UtcDateTime


class StopIntentPlacedV1(EventPayload):
    schema: Literal["stop_intent_placed.v1"] = "stop_intent_placed.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    intent_id: IntentId
    quantity: PositiveShares
    stop_price: Price
    limit_price: Price | None
    policy_release_id: ReleaseId
    placed_at: UtcDateTime


class StopAckReceivedV1(EventPayload):
    schema: Literal["stop_ack_received.v1"] = "stop_ack_received.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    intent_id: IntentId
    broker_order_id: NonEmptyText | None
    status: OrderStatus
    observed_at: UtcDateTime


class ProtectionCoverageChangedV1(EventPayload):
    schema: Literal["protection_coverage_changed.v1"] = "protection_coverage_changed.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    previous_state: CoverageState
    new_state: CoverageState
    filled_quantity: Quantity
    covered_quantity: Quantity
    reason: NonEmptyText
    observed_at: UtcDateTime


class TrailRatchetedV1(EventPayload):
    schema: Literal["trail_ratcheted.v1"] = "trail_ratcheted.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    previous_stop: Price
    new_stop: Price
    policy_release_id: ReleaseId
    ratcheted_at: UtcDateTime


class TimeStopDeadlineSetV1(EventPayload):
    schema: Literal["time_stop_deadline_set.v1"] = "time_stop_deadline_set.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    deadline: UtcDateTime
    policy_release_id: ReleaseId
    set_at: UtcDateTime


class EntryRegimeRecordedV1(EventPayload):
    schema: Literal["entry_regime_recorded.v1"] = "entry_regime_recorded.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    regime: NonEmptyText
    snapshot_id: SnapshotId
    release_id: ReleaseId
    recorded_at: UtcDateTime


class ApprovalDecisionV1(EventPayload):
    schema: Literal["approval_decision.v1"] = "approval_decision.v1"
    account_id: AccountId
    intent_id: IntentId
    decision: Literal["approved", "rejected", "expired"]
    decided_by: NonEmptyText
    reason: NonEmptyText
    decided_at: UtcDateTime


class OrderReservationCommittedV1(EventPayload):
    schema: Literal["order_reservation_committed.v1"] = "order_reservation_committed.v1"
    reservation_id: NonEmptyText
    account_id: AccountId
    intent_id: IntentId
    cas_version: int = Field(ge=0)
    cash: Money
    quantity: PositiveShares
    risk: Money
    policy_release_ids: tuple[ReleaseId, ...]
    committed_at: UtcDateTime


class OrderReservationReleasedV1(EventPayload):
    schema: Literal["order_reservation_released.v1"] = "order_reservation_released.v1"
    reservation_id: NonEmptyText
    account_id: AccountId
    intent_id: IntentId
    reason: NonEmptyText
    released_at: UtcDateTime


class StrategyAttributionV1(EventPayload):
    schema: Literal["strategy_attribution.v1"] = "strategy_attribution.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    strategy_book_id: StrategyBookId
    quantity: PositiveShares
    attributed_at: UtcDateTime


class FxLotOpenedV1(EventPayload):
    schema: Literal["fx_lot_opened.v1"] = "fx_lot_opened.v1"
    account_id: AccountId
    lot_id: NonEmptyText
    acquired: Money
    cost_basis: Money
    rate_record_id: NonEmptyText
    opened_at: UtcDateTime


class FxLotConsumedV1(EventPayload):
    schema: Literal["fx_lot_consumed.v1"] = "fx_lot_consumed.v1"
    account_id: AccountId
    lot_id: NonEmptyText
    consumed: Money
    allocated_cost_basis: Money
    reason: NonEmptyText
    consumed_at: UtcDateTime


class IdleFxLotOpenedV1(EventPayload):
    schema: Literal["idle_fx_lot_opened.v1"] = "idle_fx_lot_opened.v1"
    account_id: AccountId
    lot_id: NonEmptyText
    amount: Money
    disposition_deadline: date
    opened_at: UtcDateTime


class IdleFxLotDisposedV1(EventPayload):
    schema: Literal["idle_fx_lot_disposed.v1"] = "idle_fx_lot_disposed.v1"
    account_id: AccountId
    lot_id: NonEmptyText
    amount: Money
    proceeds: Money
    reason: NonEmptyText
    value_date: date
    disposed_at: UtcDateTime


class CalibrationRecordedV1(EventPayload):
    schema: Literal["calibration_recorded.v1"] = "calibration_recorded.v1"
    account_id: AccountId
    episode_id: PositionEpisodeId
    strategy_book_id: StrategyBookId
    outcome: Literal["success", "failure"]
    recorded_at: UtcDateTime


class KillSwitchGenerationBumpedV1(EventPayload):
    schema: Literal["kill_switch_generation_bumped.v1"] = "kill_switch_generation_bumped.v1"
    account_id: AccountId
    previous_generation: int = Field(ge=0)
    new_generation: int = Field(ge=1)
    previous_state: KillState
    new_state: KillState
    reason: NonEmptyText
    bumped_at: UtcDateTime
```

Use `NonEmptyText` for every opaque broker, reservation, lot, reason, actor,
cycle, regime, rate-record, and correlation string. Use `PositiveShares` for
fill allocation, stop intent, and strategy-attribution quantities. Add exact
after-validators:

- `OrderReservationCommittedV1.cash.currency ==
  OrderReservationCommittedV1.risk.currency`;
- `TrailRatchetedV1.previous_stop.currency ==
  TrailRatchetedV1.new_stop.currency` and the prices differ;
- `KillSwitchGenerationBumpedV1.new_generation ==
  previous_generation + 1`;
- `ProtectionCoverageChangedV1` quantities both use shares.

Whether a trail moved in the correct direction depends on episode direction and
belongs to the later recovery handler, not the kernel payload constructor. The
event model establishes facts only; it does not implement recovery handlers.

- [ ] **Step 5: Implement schema-derived envelopes**

Define all 22 snake-case `EventType` members and all 22
`<event_type>.v1` `EventSchema` members. Build total maps:

```python
EVENT_TYPE_BY_SCHEMA: dict[EventSchema, EventType]
PAYLOAD_TYPE_BY_SCHEMA: dict[EventSchema, type[EventPayload]]
```

Define the discriminated union with `Field(discriminator="schema")`. The
envelope factory is:

```python
class EventEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: EventId
    event_type: EventType
    schema_version: int = Field(ge=1)
    payload: OperationalPayload
    recorded_at: UtcDateTime
    valid_at: UtcDateTime | None = None
    correlation_id: str | None = None
    causation_id: EventId | None = None

    @model_validator(mode="after")
    def verify_schema_columns(self) -> "EventEnvelope":
        schema = EventSchema(self.payload.schema)
        expected_version = int(schema.value.rsplit(".v", 1)[1])
        if self.event_type is not EVENT_TYPE_BY_SCHEMA[schema]:
            raise ValueError("event_type does not match payload schema")
        if self.schema_version != expected_version:
            raise ValueError("schema_version does not match payload schema")
        return self

    @classmethod
    def new(
        cls,
        *,
        payload: OperationalPayload,
        recorded_at: datetime,
        valid_at: datetime | None = None,
        correlation_id: str | None = None,
        causation_id: EventId | None = None,
    ) -> "EventEnvelope":
        schema = EventSchema(payload.schema)
        return cls(
            event_id=EventId.new(),
            event_type=EVENT_TYPE_BY_SCHEMA[schema],
            schema_version=int(schema.value.rsplit(".v", 1)[1]),
            payload=payload,
            recorded_at=recorded_at,
            valid_at=valid_at,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )


class StoredEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    stream_id: NonEmptyText
    stream_version: int = Field(ge=1)
    envelope: EventEnvelope
```

- [ ] **Step 6: Convert current producers and row serialization**

Replace `new_event("CycleCompleted", {...})`,
`new_event("OrderIntentCreated", {...})`, and
`new_event("OrderAcknowledged", {...})` with their typed `V1` payloads and
explicit clock time. `EventRow.from_envelope()` serializes:

```python
payload=event.payload.model_dump(mode="json"),
event_type=event.event_type.value,
schema_version=event.schema_version,
```

Tests no longer create `A`, `B`, `X`, `Other`, `AccountObserved`, or
`CapitalEnvelopeReleased`; use distinct valid typed payload instances instead.
Delete the free-form `new_event()` function.

- [ ] **Step 7: Run event and producer tests**

Run:

```bash
uv run pytest tests/unit/kernel/test_events.py tests/unit/kernel/test_event_catalogue.py -q
uv run mypy src/trading_os
uv run ruff check src tests
make services-up
uv run pytest tests/integration/app/test_cycle.py tests/integration/execution/test_coordinator.py tests/integration/ledger/test_event_store.py tests/replay/test_two_broker_cycle.py -q
make services-down
```

Expected: all commands PASS; catalogue count is 22 and no producer supplies a
free-form event name or dictionary payload.

- [ ] **Step 8: Run both review gates and commit**

Specification review checks all 3 existing + 19 recovery facts, schema
derivation, UTC time, no handler scope creep, and no global events. Quality
review checks union discrimination, serializer symmetry, enum totality, and
payload locality. Fix findings, rerun Step 7, then:

```bash
git add src/trading_os/kernel src/trading_os/app src/trading_os/execution src/trading_os/ledger tests
git commit -m "feat: close the operational event catalogue"
```

---

### Task 5: Consolidate thirteen external ports and reusable offline fakes

**Covers:** V1 Task 5 and the in-memory half of V1 Task 6.

**Files:**

- Create all files under `src/trading_os/ports/` listed in the file map.
- Create: `src/trading_os/ledger/memory.py`
- Delete after moving the test fake: `src/trading_os/brokers/fake.py`
- Delete: `src/trading_os/brokers/ports.py`
- Delete: `src/trading_os/market_data/ports.py`
- Modify: `src/trading_os/agents/llm.py`
- Modify: `src/trading_os/agents/composition.py`
- Modify: `src/trading_os/agents/corporate_events.py`
- Modify: `src/trading_os/agents/harness.py`
- Modify: `src/trading_os/agents/providers.py`
- Modify: `src/trading_os/execution/coordinator.py`
- Modify: `src/trading_os/market_data/models.py`
- Modify: `src/trading_os/ontology/projections.py`
- Modify: `tests/contract/agents/llm_role_contract.py`
- Modify: `tests/contract/agents/test_anthropic_llm_role.py`
- Modify: `tests/contract/agents/test_fixture_llm_role.py`
- Modify: `tests/contract/agents/test_openai_llm_role.py`
- Modify: `tests/contract/brokers/contract.py`
- Modify: `tests/contract/brokers/test_fake_contract.py`
- Modify: `tests/integration/agents/test_p0_acceptance.py`
- Modify: `tests/unit/agents/test_corporate_event_nodes.py`
- Create: `tests/fakes/__init__.py`
- Create: `tests/fakes/ports.py`
- Create: `tests/unit/ports/__init__.py`
- Create: `tests/unit/ports/test_fakes.py`
- Create: `tests/unit/ports/test_architecture.py`
- Create: `tests/integration/conftest.py`
- Modify: `Makefile`

**Interfaces:**

- Consumes: typed broker, agent, graph, market-data, and event models.
- Produces exactly thirteen canonical external protocols and deterministic fakes.

- [ ] **Step 1: Write failing protocol conformance tests**

```python
# tests/unit/ports/test_fakes.py
from datetime import UTC, datetime

from trading_os.kernel.ids import AccountId
from trading_os.kernel.values import Currency
from trading_os.ports.broker import BrokerPort
from trading_os.ports.calendar import CalendarPort
from trading_os.ports.clock import ClockPort
from trading_os.ports.event_store import EventStorePort
from trading_os.ports.fx import FxRatePort
from trading_os.ports.graph import GraphStorePort
from trading_os.ports.hitl import HITLTransportPort
from trading_os.ports.llm import LLMRolePort
from trading_os.ports.market_data import MarketDataPort
from trading_os.ports.notifier import NotifierPort
from trading_os.ports.secrets import SecretsPort
from trading_os.ports.security_master import SecurityMasterPort
from trading_os.ports.state_cache import StateCachePort
from tests.fakes.ports import (
    CollectingNotifier,
    FakeCalendar,
    FakeBroker,
    FakeFxRates,
    FakeGraphStore,
    FakeHITLTransport,
    FakeLLMRole,
    FakeMarketData,
    FakeSecrets,
    FakeSecurityMaster,
    FrozenClock,
    InMemoryEventStore,
    InMemoryStateCache,
)


def test_core_fakes_satisfy_canonical_protocols() -> None:
    now = datetime(2026, 7, 23, 10, tzinfo=UTC)
    clock: ClockPort = FrozenClock(now)
    calendar: CalendarPort = FakeCalendar()
    market_data: MarketDataPort = FakeMarketData()
    fx: FxRatePort = FakeFxRates()
    security_master: SecurityMasterPort = FakeSecurityMaster()
    graph: GraphStorePort = FakeGraphStore()
    cache: StateCachePort = InMemoryStateCache(clock=clock)
    broker: BrokerPort = FakeBroker.empty(
        account_id=AccountId.parse("acct-1"),
        currency=Currency.INR,
        now=now,
    )
    llm: LLMRolePort = FakeLLMRole({})
    secrets: SecretsPort = FakeSecrets({})
    hitl: HITLTransportPort = FakeHITLTransport()
    notifier: NotifierPort = CollectingNotifier()
    events: EventStorePort = InMemoryEventStore()
    assert clock.now() == now
    assert (
        calendar,
        market_data,
        fx,
        security_master,
        graph,
        cache,
        broker,
        llm,
        secrets,
        hitl,
        notifier,
        events,
    )
```

- [ ] **Step 2: Run the test and observe missing canonical ports**

Run:

```bash
uv run pytest tests/unit/ports/test_fakes.py -v
```

Expected: FAIL with missing `trading_os.ports`.

- [ ] **Step 3: Define the exact protocol signatures**

Use these canonical capabilities:

```python
T = TypeVar("T", bound=BaseModel)


class ClockPort(Protocol):
    def now(self) -> datetime: ...


# Defined in `market_data.models`; imported by `ports.calendar`.
class MarketSession(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    market: Market
    trade_date: date
    opens_at: UtcDateTime
    closes_at: UtcDateTime
    calendar_release_id: ReleaseId

    @model_validator(mode="after")
    def validate_window(self) -> "MarketSession":
        if self.opens_at >= self.closes_at:
            raise ValueError("market session must open before it closes")
        return self


class CalendarPort(Protocol):
    def session(
        self, market: Market, trade_date: date
    ) -> MarketSession | None: ...


class MarketDataPort(Protocol):
    async def historical_bars(
        self,
        instrument_id: InstrumentId,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> tuple[Bar, ...]: ...
    async def latest_quote(self, instrument_id: InstrumentId) -> Quote: ...


class FxRatePort(Protocol):
    async def live_rate(
        self, base: Currency, quote: Currency, at: datetime
    ) -> FxMark: ...
    async def rule115_rate(self, transaction_date: date) -> FxMark: ...


class SecurityMasterPort(Protocol):
    async def resolve(
        self, market: Market, symbol: str, as_of: date
    ) -> InstrumentId | None: ...


class GraphStorePort(Protocol):
    def rebuild(
        self, manifest: SemanticContentManifest
    ) -> SemanticProjectionReceipt: ...


class EventStorePort(Protocol):
    async def append(
        self,
        stream_id: str,
        expected_version: int,
        events: Sequence[EventEnvelope],
    ) -> int: ...
    async def read_stream(
        self, stream_id: str, after_version: int = 0
    ) -> tuple[StoredEvent, ...]: ...


class StateCachePort(Protocol):
    async def get(self, key: str) -> bytes | None: ...
    async def set(
        self, key: str, value: bytes, expires_at: datetime | None = None
    ) -> None: ...
    async def delete(self, key: str) -> None: ...


class BrokerPort(Protocol):
    async def observe_account(self) -> BrokerSnapshotObservation: ...
    async def submit_order(self, request: OrderRequest) -> OrderAck: ...
    async def cancel_order(self, broker_order_id: str) -> None: ...


class LLMRolePort(Protocol):
    async def invoke(
        self, invocation: StructuredInvocation[T]
    ) -> StructuredResult[T] | ExpectedLLMFailure: ...


class SecretsPort(Protocol):
    async def get_secret(self, name: str) -> SecretStr: ...


class HITLTransportPort(Protocol):
    async def send(self, request: HITLRequest) -> None: ...
    async def receive(
        self, correlation_id: str, timeout_seconds: int
    ) -> HITLResponse | None: ...


class NotifierPort(Protocol):
    async def notify(self, notification: Notification) -> None: ...
```

The exact transport DTOs are:

```python
class HITLRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    correlation_id: str
    account_id: AccountId
    kind: Literal["approval", "emergency"]
    message: str
    created_at: UtcDateTime


class HITLResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    correlation_id: str
    outcome: Literal["approved", "rejected", "expired"]
    responder: str
    responded_at: UtcDateTime


class Notification(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    account_id: AccountId | None
    severity: Literal["info", "warning", "critical"]
    topic: str
    message: str
    created_at: UtcDateTime
```

Non-empty canonical-text validators apply to correlation, message, responder,
and topic fields. These DTOs carry no order authority or executable number.

Expected failure behavior is capability-specific:

| Port | Expected failure contract |
|---|---|
| `CalendarPort` | `CalendarUnavailable`; a closed day is ordinary `None` |
| `MarketDataPort` | `MarketDataUnavailable` or `MarketDataNotFound` |
| `FxRatePort` | `FxRateUnavailable`; absence never fabricates `1.0` |
| `SecurityMasterPort` | infrastructure failure raises `SecurityMasterUnavailable`; unknown symbol returns `None` |
| `GraphStorePort` | unavailability returns a degraded `SemanticProjectionReceipt`, preserving the relational champion |
| `EventStorePort` | the four typed store errors defined below |
| `StateCachePort` | `StateCacheUnavailable`; missing key returns `None` |
| `BrokerPort` | subject-owned broker failure types; ambiguity returns `OrderStatus.OUTCOME_UNKNOWN` |
| `LLMRolePort` | existing `ExpectedLLMFailure` union |
| `SecretsPort` | `SecretNotFound` or `SecretsUnavailable` |
| `HITLTransportPort` | `HITLUnavailable`; response timeout returns `None` |
| `NotifierPort` | `NotifierUnavailable` |

`ClockPort` has no expected runtime-failure abstraction. No port defines or
raises a universal `InfrastructureError`.

- [ ] **Step 4: Move only external protocols**

Update all imports to `trading_os.ports.*`. Remove `BrokerPort`,
`MarketDataPort`, `GraphProjectionPort`, and `LLMRole` definitions from their old
modules after their callers move. Keep `ResearchAgentPort`, `TrajectoryEngine`,
`SourceWatcher`, `SourceFetchPort`, `SeenRecordStore`,
`OpportunityDetector`, and `AgentRunLedger` beside their subsystems.

`LLMRolePort` uses the existing `StructuredInvocation`, `StructuredResult`, and
`ExpectedLLMFailure`; it is not a second harness/provider seam.

- [ ] **Step 5: Implement deterministic fakes and memory event store**

`tests/fakes/ports.py` provides:

```text
FrozenClock, FakeCalendar, FakeMarketData, FakeFxRates,
FakeSecurityMaster, FakeGraphStore, InMemoryEventStore,
InMemoryStateCache, FakeBroker, FakeLLMRole, FakeSecrets,
FakeHITLTransport, CollectingNotifier
```

Each fake stores typed calls in insertion order and performs no clock, network,
filesystem, environment, or credential access. `FakeLLMRole` delegates to the
existing deterministic fixture-role behavior. `InMemoryEventStore` is imported
from `trading_os.ledger.memory`, not reimplemented.

Use these exact fake states and outcomes:

| Fake | Constructor state | Recorded calls / result |
|---|---|---|
| `FrozenClock` | one UTC datetime | `now()` always returns it |
| `FakeCalendar` | `(Market, date) -> MarketSession` map | records lookups and returns a session or `None` |
| `FakeMarketData` | bar map and quote map | records typed requests; returns immutable tuples/models |
| `FakeFxRates` | `(Currency, Currency)` and Rule-115 date maps | records lookups; missing keys raise `FxRateUnavailable` |
| `FakeSecurityMaster` | `(Market, symbol, date) -> InstrumentId` map | records resolution requests; unknown returns `None` |
| `FakeGraphStore` | queued projection receipts | records manifests; pops one receipt per rebuild |
| `InMemoryEventStore` | empty or preloaded typed streams | implements the full event-store contract below |
| `InMemoryStateCache` | `ClockPort` plus `dict[str, bytes]` | records get/set/delete and enforces explicit expiries against the clock |
| `FakeBroker` | account snapshot and intent map | records submit/cancel; idempotent by `IntentId` |
| `FakeLLMRole` | replay-key result map | records invocation; returns typed fixture result/failure |
| `FakeSecrets` | `dict[str, SecretStr]` | records names; missing secret raises `SecretNotFound` |
| `FakeHITLTransport` | queued typed responses | records sent requests; returns matching queued response or `None` |
| `CollectingNotifier` | empty notification list | appends notifications in call order |

The memory store implements expected-version append, immutable ordered replay,
exact whole-batch retry, partial-duplicate rejection, and same-ID/different-fact
rejection. Define shared errors in `ports/event_store.py`:

```python
class EventStoreError(RuntimeError): ...
class ConcurrencyError(EventStoreError): ...
class DuplicateBatchError(EventStoreError): ...
class EventIdentityConflict(EventStoreError): ...
```

- [ ] **Step 6: Add architecture and offline-gate tests**

```python
# tests/unit/ports/test_architecture.py
from pathlib import Path


def test_removed_external_port_paths_do_not_exist() -> None:
    root = Path("src/trading_os")
    assert not (root / "brokers/ports.py").exists()
    assert not (root / "market_data/ports.py").exists()


def test_kernel_does_not_import_infrastructure_or_subject_packages() -> None:
    forbidden = (
        "trading_os.brokers",
        "trading_os.ledger",
        "trading_os.ports",
        "sqlalchemy",
        "langgraph",
    )
    for path in Path("src/trading_os/kernel").glob("*.py"):
        text = path.read_text()
        assert not any(name in text for name in forbidden), path
```

Add `tests/integration/conftest.py` collection logic that applies
`pytest.mark.integration` only to tests collected below that directory:

```python
# tests/integration/conftest.py
from pathlib import Path

import pytest

INTEGRATION_ROOT = Path(__file__).parent.resolve()


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if Path(str(item.path)).resolve().is_relative_to(INTEGRATION_ROOT):
            item.add_marker(pytest.mark.integration)
```

Change the default Makefile test command to:

```make
test:
	uv run pytest tests/unit tests/contract tests/live_readiness
```

- [ ] **Step 7: Run the ports/fakes gate**

Run:

```bash
uv run pytest tests/unit/ports tests/contract/agents tests/contract/brokers -q
uv run mypy src/trading_os
uv run ruff check src tests
```

Expected: all commands PASS, all thirteen protocols have a structurally
conforming fake, and no old external port path remains.

- [ ] **Step 8: Run both review gates and commit**

Specification review checks the exact thirteen-port roster, internal-contract
locality, agent-harness continuity, relational champion, and deployment
neutrality. Quality review checks protocol size, cycles, fake determinism, and
typed failure behavior. Fix findings, rerun Step 7, then:

```bash
git add Makefile src/trading_os tests
git commit -m "refactor: unify external capability ports"
```

---

### Task 6: Make memory and PostgreSQL stores satisfy one event contract

**Covers:** V1 Task 6, event-store completion.

**Files:**

- Modify: `src/trading_os/ledger/store.py`
- Modify: `src/trading_os/ledger/tables.py`
- Modify: `src/trading_os/ledger/replay.py`
- Modify: `src/trading_os/ledger/memory.py`
- Modify: `src/trading_os/app/container.py`
- Modify: `src/trading_os/execution/coordinator.py`
- Create: `tests/contract/ledger/__init__.py`
- Create: `tests/contract/ledger/contract.py`
- Create: `tests/contract/ledger/test_memory_event_store.py`
- Modify: `tests/integration/ledger/conftest.py`
- Modify: `tests/integration/ledger/test_event_store.py`
- Modify: `tests/integration/execution/conftest.py`
- Modify: `tests/integration/app/conftest.py`
- Modify: `tests/replay/conftest.py`
- Modify: `tests/replay/test_two_broker_cycle.py`
- Modify: `Makefile`

**Interfaces:**

- Consumes: `EventStorePort`, typed envelopes, and Task 5 errors.
- Produces:
  `InMemoryEventStore` and `PostgresEventStore` with identical observable
  behavior; `read_stream() -> tuple[StoredEvent, ...]`.

- [ ] **Step 1: Write shared contract assertions before changing PostgreSQL**

```python
# tests/contract/ledger/contract.py
from datetime import UTC, datetime, timedelta

import pytest

from trading_os.kernel.event_payloads import CycleCompletedV1
from trading_os.kernel.events import EventEnvelope, EventType
from trading_os.kernel.ids import AccountId, EventId
from trading_os.ports.event_store import (
    ConcurrencyError,
    DuplicateBatchError,
    EventIdentityConflict,
    EventStorePort,
)

NOW = datetime(2026, 7, 23, 10, tzinfo=UTC)


def valid_events() -> tuple[EventEnvelope, EventEnvelope]:
    def event(event_id: str, cycle_id: str) -> EventEnvelope:
        payload = CycleCompletedV1(
            account_id=AccountId.parse("acct-contract"),
            cycle_id=cycle_id,
            cycle_key=f"key-{cycle_id}",
            order_intent_ids=(),
            live_writes_enabled=False,
        )
        return EventEnvelope(
            event_id=EventId.parse(event_id),
            event_type=EventType.CYCLE_COMPLETED,
            schema_version=1,
            payload=payload,
            recorded_at=NOW,
        )

    return event("event-1", "cycle-1"), event("event-2", "cycle-2")


async def assert_ordered_batch_append(store: EventStorePort) -> None:
    first, second = valid_events()
    assert await store.append("account:acct-1", 0, (first, second)) == 2
    loaded = await store.read_stream("account:acct-1")
    assert [item.stream_version for item in loaded] == [1, 2]
    assert [item.envelope.event_id for item in loaded] == [
        first.event_id,
        second.event_id,
    ]


async def assert_exact_batch_retry_is_idempotent(store: EventStorePort) -> None:
    batch = valid_events()
    assert await store.append("account:acct-2", 0, batch) == 2
    assert await store.append("account:acct-2", 0, batch) == 2
    assert len(await store.read_stream("account:acct-2")) == 2


async def assert_partial_duplicate_fails(store: EventStorePort) -> None:
    first, second = valid_events()
    await store.append("account:acct-3", 0, (first,))
    with pytest.raises(DuplicateBatchError):
        await store.append("account:acct-3", 1, (first, second))


async def assert_same_id_different_fact_fails(store: EventStorePort) -> None:
    first, _ = valid_events()
    await store.append("account:acct-4", 0, (first,))
    conflicting = first.model_copy(
        update={"recorded_at": first.recorded_at + timedelta(seconds=1)}
    )
    with pytest.raises(EventIdentityConflict):
        await store.append("account:acct-4", 0, (conflicting,))


async def assert_stale_expected_version_fails(store: EventStorePort) -> None:
    first, second = valid_events()
    await store.append("account:acct-5", 0, (first,))
    with pytest.raises(ConcurrencyError):
        await store.append("account:acct-5", 0, (second,))


async def assert_after_version_filters_without_reordering(store: EventStorePort) -> None:
    first, second = valid_events()
    await store.append("account:acct-6", 0, (first, second))
    loaded = await store.read_stream("account:acct-6", after_version=1)
    assert tuple(item.envelope.event_id for item in loaded) == (second.event_id,)


async def assert_event_identity_cannot_move_streams(store: EventStorePort) -> None:
    first, _ = valid_events()
    await store.append("account:acct-7", 0, (first,))
    with pytest.raises(EventIdentityConflict):
        await store.append("account:other", 0, (first,))
```

`valid_events()` returns two distinct valid typed envelopes created with fixed
UTC times—never arbitrary event names.

- [ ] **Step 2: Run contract against memory and observe PostgreSQL mismatch**

Run:

```bash
uv run pytest tests/contract/ledger/test_memory_event_store.py -v
uv run pytest -m integration tests/integration/ledger/test_event_store.py -v
```

Expected: memory tests PASS after Task 5; PostgreSQL tests FAIL because it returns
rows, accepts weak whole-ID idempotency, and does not implement exact batch
identity.

- [ ] **Step 3: Harden row deserialization**

`EventRow.to_stored_event()`:

1. serializes the JSONB dictionary back to canonical JSON;
2. validates it with `TypeAdapter(OperationalPayload).validate_json(...)`, so
   strict Decimal strings are parsed under JSON rules;
3. reconstructs `EventEnvelope`;
4. verifies column `event_type` and `schema_version` against the payload schema;
5. returns `StoredEvent(stream_id, stream_version, envelope)`.

Unknown schema, malformed payload, or mismatched columns raises a typed
deserialization error and never returns a dictionary.

- [ ] **Step 4: Implement transactional PostgreSQL append**

Rename the concrete class to `PostgresEventStore`; do not leave an `EventStore`
alias. Its append transaction:

```text
BEGIN
pg_advisory_xact_lock(hashtextextended(stream_id, 0))
load current maximum stream_version, default 0
load rows for requested event IDs
if every ID exists:
    require same stream, expected contiguous positions, and canonical envelope
    return the existing batch's final version
if some IDs exist:
    raise DuplicateBatchError or EventIdentityConflict
if current != expected_version:
    raise ConcurrencyError
insert the whole batch at current+1..current+n
COMMIT
```

Check duplicate IDs within the requested batch before opening the transaction.
Map uniqueness races to the same typed errors. Do not alter the `event_log`
schema or migrations.

- [ ] **Step 5: Return `StoredEvent` everywhere**

Change PostgreSQL and memory `read_stream()` to:

```python
async def read_stream(
    self, stream_id: str, after_version: int = 0
) -> tuple[StoredEvent, ...]:
    ...
```

Update `ledger.replay()` to fold `StoredEvent`, and update coordinator/container
to depend on `EventStorePort`. Coordinator reads typed payloads and never
indexes a dictionary. Rename fixtures and type annotations from `EventStore` to
`PostgresEventStore`.

Convert `tests/replay/conftest.py` to `InMemoryEventStore` so replay joins the
offline deterministic gate. Update Makefile:

```make
test:
	uv run pytest tests/unit tests/contract tests/replay tests/live_readiness
```

- [ ] **Step 6: Run shared, replay, and PostgreSQL gates**

Run offline:

```bash
uv run pytest tests/contract/ledger tests/replay -q
make verify
```

Expected: PASS without Docker, network, or credentials.

Run local PostgreSQL integration:

```bash
make services-up
uv run pytest -m integration tests/integration/ledger tests/integration/execution tests/integration/app -q
make services-down
```

Expected: PASS; update/delete trigger tests still reject mutation. No
live-readiness or credentialed broker test is run.

- [ ] **Step 7: Run both review gates and commit**

Specification review checks stream convention `0 -> 1`, store-owned positions,
exact retry semantics, unknown-schema failure, and no migration. Quality review
checks transaction boundaries, canonical comparison, race mapping, memory/store
parity, and no SQLAlchemy leakage through the port. Fix findings, rerun Step 6,
then:

```bash
git add Makefile src/trading_os tests
git commit -m "feat: enforce the typed event store contract"
```

---

## Whole-branch review and handoff

- [ ] **Step 1: Audit the final tree against the design**

Confirm:

```bash
rg -n 'NewType' src/trading_os
rg -n 'new_event\\(|event_type: str|payload: dict' src/trading_os/kernel src/trading_os/ledger src/trading_os/execution src/trading_os/app
rg -n 'GlobalPortfolioSnapshot|control:global' src tests
rg -n 'from trading_os\\.(brokers\\.ports|market_data\\.ports)' src tests
rg -n 'limit_price_minor|stop_price_minor' src/trading_os
rg -n '_minor\\b' src/trading_os --glob '*.py'
rg -n 'client_order_id' src/trading_os
```

Expected: the first five commands have no matches. The `_minor` audit reports
only storage conversion and `ReservationRow` fields. `client_order_id` reports
only the Alpaca SDK boundary where `IntentId` is mapped explicitly.

- [ ] **Step 2: Run the complete offline gate**

```bash
make verify
git diff --check origin/main...HEAD
git status --short
```

Expected: Ruff, strict mypy, unit, contract, and replay tests PASS; diff check is
clean; worktree has no uncommitted files.

- [ ] **Step 3: Run whole-branch specification and quality review**

Review the complete branch, not just the last task. Reject:

- a second ID/value/event/port authority;
- global account aggregation;
- global kill state;
- changed reservation CAS ownership;
- arbitrary event decoding;
- floats or minor-unit domain fields at executable boundaries;
- infrastructure details inside protocols;
- live/network tests in the default gate.

If a finding touches an earlier task, reopen that task, apply the smallest
correction, rerun its gate, and record a clearly scoped review-fix commit. Do not
rewrite shared history.

- [ ] **Step 4: Prepare the PR but do not push or open it without instruction**

Summarize the six focused implementation commits, offline and integration test
results, accepted ADR-0011, and any evidence that changed the design. The user
reviews and merges; never push, open a PR, or merge on assumption.
