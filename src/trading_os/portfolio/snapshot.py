import json
from datetime import datetime
from hashlib import sha256

from pydantic import BaseModel

from trading_os.kernel.ids import (
    AccountId,
    ReleaseId,
    SnapshotId,
    ValidatedDataSnapshotId,
)
from trading_os.portfolio.completeness import PortfolioCompletenessVector


class AccountPortfolioSnapshot(BaseModel, frozen=True):
    """A sealed, content-addressed cut of one account's state at a decision time."""

    account_id: AccountId
    broker_observation_ids: tuple[SnapshotId, ...]
    ledger_version: int
    reservation_ids: tuple[str, ...]
    validated_data_snapshot_id: ValidatedDataSnapshotId | None
    policy_release_ids: tuple[ReleaseId, ...]
    cas_version: int
    completeness: PortfolioCompletenessVector
    built_at: datetime
    content_hash: str = ""

    def sealed(self) -> "AccountPortfolioSnapshot":
        manifest = {
            "account_id": str(self.account_id),
            "broker_observation_ids": [str(i) for i in self.broker_observation_ids],
            "ledger_version": self.ledger_version,
            "reservation_ids": list(self.reservation_ids),
            "validated_data_snapshot_id": (
                None
                if self.validated_data_snapshot_id is None
                else str(self.validated_data_snapshot_id)
            ),
            "policy_release_ids": [str(i) for i in self.policy_release_ids],
            "cas_version": self.cas_version,
            "completeness": self.completeness.model_dump(mode="json"),
        }
        digest = sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        return self.model_copy(update={"content_hash": f"sha256:{digest}"})
