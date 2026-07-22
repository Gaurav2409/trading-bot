from datetime import UTC, datetime, timedelta

from trading_os.identity.models import AccessScope, AccountAccessGrant
from trading_os.kernel.ids import AccountId


def test_household_read_grant_does_not_authorize_execution() -> None:
    now = datetime.now(UTC)
    grant = AccountAccessGrant(
        grant_id="grant-1",
        account_id=AccountId("acct-1"),
        grantee_party_id="party-2",
        scopes=frozenset({AccessScope.READ}),
        effective_from=now - timedelta(minutes=1),
    )
    assert grant.allows(AccessScope.EXECUTE, now) is False


def test_read_grant_allows_read_within_effective_window() -> None:
    now = datetime.now(UTC)
    grant = AccountAccessGrant(
        grant_id="grant-1",
        account_id=AccountId("acct-1"),
        grantee_party_id="party-2",
        scopes=frozenset({AccessScope.READ}),
        effective_from=now - timedelta(minutes=1),
    )
    assert grant.allows(AccessScope.READ, now) is True


def test_revoked_grant_denies_after_revocation() -> None:
    now = datetime.now(UTC)
    grant = AccountAccessGrant(
        grant_id="grant-1",
        account_id=AccountId("acct-1"),
        grantee_party_id="party-2",
        scopes=frozenset({AccessScope.READ}),
        effective_from=now - timedelta(minutes=5),
        revoked_at=now - timedelta(minutes=1),
    )
    assert grant.allows(AccessScope.READ, now) is False
