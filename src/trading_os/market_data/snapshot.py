import json
from datetime import datetime
from hashlib import sha256

from pydantic import BaseModel

from trading_os.kernel.ids import ValidatedDataSnapshotId
from trading_os.market_data.models import Bar
from trading_os.market_data.validator import validate_bar


class BarRejection(BaseModel, frozen=True):
    instrument_id: str
    timeframe: str
    reason: str


class ValidatedDataSnapshot(BaseModel, frozen=True):
    snapshot_id: ValidatedDataSnapshotId
    cutoff: datetime
    bars: tuple[Bar, ...]
    rejections: tuple[BarRejection, ...]
    require_entitlement: str | None = None

    @property
    def rejected_count(self) -> int:
        return len(self.rejections)


def build_validated_snapshot(
    bars: list[Bar],
    cutoff: datetime,
    require_entitlement: str | None = None,
) -> ValidatedDataSnapshot:
    accepted: list[Bar] = []
    rejections: list[BarRejection] = []
    for bar in bars:
        reason = validate_bar(bar, cutoff, require_entitlement)
        if reason is None:
            accepted.append(bar)
        else:
            rejections.append(
                BarRejection(
                    instrument_id=str(bar.instrument_id),
                    timeframe=bar.timeframe,
                    reason=reason,
                )
            )

    # Sort accepted bars by canonical identity for deterministic hashing.
    accepted.sort(key=lambda b: (str(b.instrument_id), b.timeframe, b.start.isoformat()))
    manifest = {
        "cutoff": cutoff.isoformat(),
        "require_entitlement": require_entitlement,
        "bars": [
            {
                "instrument_id": str(b.instrument_id),
                "timeframe": b.timeframe,
                "start": b.start.isoformat(),
                "end": b.end.isoformat(),
                "open": str(b.open),
                "high": str(b.high),
                "low": str(b.low),
                "close": str(b.close),
                "volume": str(b.volume),
                "source_id": b.source_id,
                "entitlement": b.entitlement,
                "adjustment_set_id": b.adjustment_set_id,
            }
            for b in accepted
        ],
    }
    digest = sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    return ValidatedDataSnapshot(
        snapshot_id=ValidatedDataSnapshotId(f"sha256:{digest}"),
        cutoff=cutoff,
        bars=tuple(accepted),
        rejections=tuple(rejections),
        require_entitlement=require_entitlement,
    )
