from datetime import datetime

from trading_os.policy.models import EffectiveRelease


class ComplianceProfileRelease(EffectiveRelease, frozen=True):
    """Externally owned broker/exchange constraints, effective-dated and
    review-expiring. An expired or missing profile blocks new exposure."""

    jurisdiction: str
    broker: str
    reviewed_at: datetime
    review_expires_at: datetime
    static_ip_required: bool
    allowed_order_types: tuple[str, ...]
    max_orders_per_second: int
    required_tags: tuple[str, ...]


def is_profile_effective(profile: ComplianceProfileRelease, at: datetime) -> bool:
    return (
        profile.effective_from <= at
        and (profile.effective_until is None or at < profile.effective_until)
        and profile.reviewed_at <= at < profile.review_expires_at
    )
