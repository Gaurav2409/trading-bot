from datetime import datetime, timedelta

from trading_os.kernel.ids import AccountId, ReleaseId
from trading_os.policy.evaluator import PolicyEvaluator
from trading_os.policy.models import CapitalEnvelopeRelease


def test_capital_release_is_effective_dated(now: datetime) -> None:
    release = CapitalEnvelopeRelease(
        release_id=ReleaseId("capital-1"),
        account_id=AccountId("acct-1"),
        currency="INR",
        capital_minor=5_000_000,
        max_cumulative_loss_minor=5_000_000,
        effective_from=now - timedelta(seconds=1),
    )
    assert PolicyEvaluator().is_effective(release, now) is True


def test_release_not_yet_effective(now: datetime) -> None:
    release = CapitalEnvelopeRelease(
        release_id=ReleaseId("capital-1"),
        account_id=AccountId("acct-1"),
        currency="INR",
        capital_minor=5_000_000,
        max_cumulative_loss_minor=5_000_000,
        effective_from=now + timedelta(days=1),
    )
    assert PolicyEvaluator().is_effective(release, now) is False


def test_loss_ceiling_cannot_exceed_capital(now: datetime) -> None:
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CapitalEnvelopeRelease(
            release_id=ReleaseId("capital-bad"),
            account_id=AccountId("acct-1"),
            currency="INR",
            capital_minor=5_000_000,
            max_cumulative_loss_minor=6_000_000,
            effective_from=now,
        )


def test_initial_capital_values_and_day_10_supersession(now: datetime) -> None:
    inr = CapitalEnvelopeRelease(
        release_id=ReleaseId("kite-capital-v1"),
        account_id=AccountId("kite-1"),
        currency="INR",
        capital_minor=5_000_000,
        max_cumulative_loss_minor=5_000_000,
        effective_from=now,
    )
    usd = CapitalEnvelopeRelease(
        release_id=ReleaseId("alpaca-capital-v1"),
        account_id=AccountId("alpaca-1"),
        currency="USD",
        capital_minor=20_000,
        max_cumulative_loss_minor=20_000,
        effective_from=now,
    )
    day_10 = inr.model_copy(
        update={
            "release_id": ReleaseId("kite-capital-v2"),
            "supersedes": inr.release_id,
            "effective_from": now + timedelta(days=10),
        }
    )
    assert inr.automatic_reload is False
    assert usd.automatic_reload is False
    assert day_10.release_id != inr.release_id
    assert day_10.supersedes == inr.release_id
