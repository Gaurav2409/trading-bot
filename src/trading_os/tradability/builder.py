from datetime import datetime
from hashlib import sha256

from pydantic import BaseModel

from trading_os.kernel.ids import AccountId, InstrumentId, SnapshotId
from trading_os.tradability.models import TradabilityRiskPacket

_CIRCUIT_LOCKED = frozenset({"upper_circuit", "lower_circuit", "halted"})


class TradabilityInput(BaseModel, frozen=True):
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


def build_tradability_packet(value: TradabilityInput) -> TradabilityRiskPacket:
    """Deterministically decide account-specific tradability. Any blocking
    reason makes the candidate ineligible; a candidate is never added to the
    tradable allowlist without a complete, eligible packet.
    """
    reasons: list[str] = []
    if not value.listing_active:
        reasons.append("listing_inactive")
    if not value.broker_orderable:
        reasons.append("not_broker_orderable")
    if value.surveillance_flags:
        reasons.append("under_surveillance")
    if value.circuit_or_band_state in _CIRCUIT_LOCKED:
        reasons.append("circuit_locked")
    if value.liquidity_state not in {"adequate", "high"}:
        reasons.append("insufficient_liquidity")
    if not value.stop_feasible:
        reasons.append("stop_infeasible")
    if not value.raw_adjusted_lineage_valid:
        reasons.append("adjustment_lineage_invalid")
    if value.account_restrictions:
        reasons.append("account_restricted")

    packet_key = ":".join(
        [str(value.account_id), str(value.instrument_id), str(value.data_snapshot_id)]
    )
    return TradabilityRiskPacket(
        packet_id=sha256(packet_key.encode()).hexdigest(),
        account_id=value.account_id,
        instrument_id=value.instrument_id,
        broker=value.broker,
        listing_active=value.listing_active,
        broker_orderable=value.broker_orderable,
        surveillance_flags=value.surveillance_flags,
        circuit_or_band_state=value.circuit_or_band_state,
        liquidity_state=value.liquidity_state,
        stop_feasible=value.stop_feasible,
        raw_adjusted_lineage_valid=value.raw_adjusted_lineage_valid,
        account_restrictions=value.account_restrictions,
        data_snapshot_id=value.data_snapshot_id,
        data_fresh_at=value.data_fresh_at,
        compliance_release_id=value.compliance_release_id,
        eligible=not reasons,
        reason_codes=tuple(reasons),
    )
