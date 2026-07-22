from datetime import datetime
from hashlib import sha256
from typing import Protocol

from trading_os.discovery.models import (
    CoverageReceipt,
    DiscoveryResult,
    OpportunityCandidate,
)
from trading_os.kernel.ids import InstrumentId, SnapshotId
from trading_os.market_data.models import Bar


class OpportunityDetector(Protocol):
    @property
    def release_id(self) -> str: ...

    def detect(self, bars: list[Bar], snapshot_id: SnapshotId) -> list[OpportunityCandidate]: ...


class OpportunityDetectorRegistry:
    """Runs registered deterministic detectors across a broad instrument universe
    and always emits one CoverageReceipt, even when some instruments are omitted.
    The scanner — not an LLM — owns exhaustive universe coverage.
    """

    def __init__(self, detectors: list[OpportunityDetector]) -> None:
        self._detectors = detectors

    def run(
        self,
        bars_by_instrument: dict[InstrumentId, list[Bar]],
        data_snapshot_id: SnapshotId,
        *,
        started_at: datetime,
        completed_at: datetime,
    ) -> DiscoveryResult:
        intended = tuple(bars_by_instrument.keys())
        scanned: list[InstrumentId] = []
        omitted: dict[InstrumentId, str] = {}
        candidates: list[OpportunityCandidate] = []

        for instrument, bars in bars_by_instrument.items():
            if not bars:
                omitted[instrument] = "no_bars"
                continue
            produced_any = False
            for detector in self._detectors:
                try:
                    found = detector.detect(bars, data_snapshot_id)
                except Exception:  # noqa: BLE001 - a detector failure omits, not aborts
                    omitted[instrument] = "detector_error"
                    continue
                candidates.extend(found)
                produced_any = True
            if produced_any:
                scanned.append(instrument)

        receipt_key = ":".join(
            [str(data_snapshot_id), started_at.isoformat(), completed_at.isoformat()]
            + [str(i) for i in intended]
        )
        receipt = CoverageReceipt(
            receipt_id=sha256(receipt_key.encode()).hexdigest(),
            intended_instruments=intended,
            scanned_instruments=tuple(scanned),
            omitted=omitted,
            started_at=started_at,
            completed_at=completed_at,
            data_snapshot_id=data_snapshot_id,
            detector_release_ids=tuple(d.release_id for d in self._detectors),
        )
        return DiscoveryResult(candidates=tuple(candidates), receipt=receipt)
