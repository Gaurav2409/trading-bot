from pydantic import BaseModel

from trading_os.kernel.ids import AccountId, InstrumentId, SnapshotId


class EligibilityInput(BaseModel, frozen=True):
    account_id: AccountId
    instrument_id: InstrumentId
    on_tradable_allowlist: bool
    portfolio_gate_allows: bool
    snapshot_id: SnapshotId


class EligibilityDecision(BaseModel, frozen=True):
    eligible: bool
    reason_codes: tuple[str, ...]
