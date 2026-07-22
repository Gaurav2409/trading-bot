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
