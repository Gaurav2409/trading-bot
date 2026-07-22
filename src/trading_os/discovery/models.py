from datetime import datetime

from pydantic import BaseModel

from trading_os.kernel.ids import InstrumentId, SnapshotId


class OpportunityCandidate(BaseModel, frozen=True):
    """A discovered setup. Carries no executable fields (no quantity, price,
    target weight/position, order or broker) — it requires tradability, evidence,
    portfolio and deterministic risk evaluation before it can influence an order.
    """

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


class DiscoveryResult(BaseModel, frozen=True):
    candidates: tuple[OpportunityCandidate, ...]
    receipt: CoverageReceipt
