from datetime import UTC, datetime, timedelta

from trading_os.policy.live_authority import LiveAuthorityReceipt, verify_live_authority


def _receipt(now: datetime) -> LiveAuthorityReceipt:
    return LiveAuthorityReceipt(
        receipt_id="live-kite-1",
        account_id="kite-1",
        broker="kite",
        product_scope="cash_equity",
        readiness_report_hash="sha256:readiness",
        policy_release_ids=("capital-1", "exposure-t0", "promotion-t0"),
        kill_generation=4,
        code_commit="27658af",
        schema_version="0001",
        effective_from=now - timedelta(seconds=1),
        effective_until=now + timedelta(hours=8),
        signer="owner-1",
    )


def test_receipt_is_broker_scoped_and_expires() -> None:
    now = datetime.now(UTC)
    receipt = _receipt(now)
    common = dict(
        policy_release_ids=receipt.policy_release_ids,
        kill_generation=4,
        code_commit="27658af",
        schema_version="0001",
    )
    assert verify_live_authority(receipt, account_id="kite-1", broker="kite", at=now, **common).allowed
    # Wrong broker/account is denied.
    assert not verify_live_authority(
        receipt, account_id="alpaca-1", broker="alpaca", at=now, **common
    ).allowed
    # Expired is denied.
    assert not verify_live_authority(
        receipt, account_id="kite-1", broker="kite", at=now + timedelta(days=1), **common
    ).allowed


def test_policy_or_runtime_mismatch_denies() -> None:
    now = datetime.now(UTC)
    receipt = _receipt(now)
    assert not verify_live_authority(
        receipt,
        account_id="kite-1",
        broker="kite",
        at=now,
        policy_release_ids=("different",),
        kill_generation=4,
        code_commit="27658af",
        schema_version="0001",
    ).allowed
    assert not verify_live_authority(
        receipt,
        account_id="kite-1",
        broker="kite",
        at=now,
        policy_release_ids=receipt.policy_release_ids,
        kill_generation=99,
        code_commit="27658af",
        schema_version="0001",
    ).allowed
