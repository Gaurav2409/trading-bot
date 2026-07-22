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

    @property
    def release_id(self) -> str:
        return self._policy.release_id

    def detect(self, bars: list[Bar], snapshot_id: SnapshotId) -> list[OpportunityCandidate]:
        required = max(self._policy.return_lookback, self._policy.volume_lookback) + 2
        if len(bars) < required:
            return []
        recent_return = bars[-1].close / bars[-self._policy.return_lookback].close - Decimal("1")
        volume_window = bars[-(self._policy.volume_lookback + 2) : -2]
        baseline_volume = sum((bar.volume for bar in volume_window), Decimal("0")) / Decimal(
            len(volume_window)
        )
        volume_ratio = (
            bars[-1].volume / baseline_volume if baseline_volume > 0 else Decimal("0")
        )
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
