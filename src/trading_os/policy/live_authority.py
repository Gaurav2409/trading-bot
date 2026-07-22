from datetime import datetime

from pydantic import BaseModel


class LiveAuthorityReceipt(BaseModel, frozen=True):
    receipt_id: str
    account_id: str
    broker: str
    product_scope: str
    readiness_report_hash: str
    policy_release_ids: tuple[str, ...]
    kill_generation: int
    code_commit: str
    schema_version: str
    effective_from: datetime
    effective_until: datetime
    signer: str


class LiveAuthorityDecision(BaseModel, frozen=True):
    allowed: bool
    reason: str


def verify_live_authority(
    receipt: LiveAuthorityReceipt,
    *,
    account_id: str,
    broker: str,
    at: datetime,
    policy_release_ids: tuple[str, ...],
    kill_generation: int,
    code_commit: str,
    schema_version: str,
) -> LiveAuthorityDecision:
    """Verified immediately before every submit/amend/cancel/replace. A receipt
    only authorizes its exact broker/account, within its interval, for the exact
    policy releases, kill generation, code commit and schema version."""
    if receipt.account_id != account_id or receipt.broker != broker:
        return LiveAuthorityDecision(allowed=False, reason="scope_mismatch")
    if not receipt.effective_from <= at < receipt.effective_until:
        return LiveAuthorityDecision(allowed=False, reason="receipt_inactive")
    if receipt.policy_release_ids != policy_release_ids:
        return LiveAuthorityDecision(allowed=False, reason="policy_release_mismatch")
    if receipt.kill_generation != kill_generation:
        return LiveAuthorityDecision(allowed=False, reason="kill_generation_mismatch")
    if receipt.code_commit != code_commit or receipt.schema_version != schema_version:
        return LiveAuthorityDecision(allowed=False, reason="runtime_version_mismatch")
    return LiveAuthorityDecision(allowed=True, reason="receipt_effective")
