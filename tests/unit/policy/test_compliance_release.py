from datetime import UTC, datetime, timedelta

from trading_os.kernel.ids import ReleaseId
from trading_os.policy.compliance import ComplianceProfileRelease, is_profile_effective


def _release(**overrides: object) -> ComplianceProfileRelease:
    now = datetime(2026, 7, 22, tzinfo=UTC)
    base = dict(
        release_id=ReleaseId("india-v1"),
        effective_from=now - timedelta(days=1),
        jurisdiction="IN",
        broker="kite",
        reviewed_at=now - timedelta(days=1),
        review_expires_at=now + timedelta(days=30),
        static_ip_required=True,
        allowed_order_types=("limit", "stop_limit"),
        max_orders_per_second=10,
        required_tags=("algo",),
    )
    base.update(overrides)
    return ComplianceProfileRelease(**base)  # type: ignore[arg-type]


def test_effective_profile_is_usable() -> None:
    now = datetime(2026, 7, 22, tzinfo=UTC)
    assert is_profile_effective(_release(), now) is True


def test_expired_review_blocks_new_exposure() -> None:
    now = datetime(2026, 7, 22, tzinfo=UTC)
    expired = _release(review_expires_at=now - timedelta(seconds=1))
    assert is_profile_effective(expired, now) is False


def test_day_10_supersession_keeps_prior_release_id() -> None:
    now = datetime(2026, 7, 22, tzinfo=UTC)
    v1 = _release()
    v2 = v1.model_copy(
        update={
            "release_id": ReleaseId("india-v2"),
            "supersedes": v1.release_id,
            "effective_from": now + timedelta(days=10),
        }
    )
    assert v2.supersedes == v1.release_id
    assert v2.release_id != v1.release_id
