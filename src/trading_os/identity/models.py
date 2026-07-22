from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from trading_os.kernel.ids import AccountId


class AccessScope(StrEnum):
    READ = "read"
    RECONCILE = "reconcile"
    PROPOSE = "propose"
    APPROVE = "approve"
    EXECUTE = "execute"


class LegalParty(BaseModel, frozen=True):
    party_id: str
    party_kind: str


class UserProfile(BaseModel, frozen=True):
    profile_id: str
    party_id: str
    tenant_id: str


class BrokerageAccount(BaseModel, frozen=True):
    account_id: AccountId
    broker: str
    environment: str
    external_account_hash: str
    base_currency: str


class BrokerConnectionRef(BaseModel, frozen=True):
    connection_id: str
    broker: str
    credential_secret_ref: str


class AccountAccessGrant(BaseModel, frozen=True):
    grant_id: str
    account_id: AccountId
    grantee_party_id: str
    scopes: frozenset[AccessScope]
    effective_from: datetime
    effective_until: datetime | None = None
    revoked_at: datetime | None = None

    def allows(self, scope: AccessScope, at: datetime) -> bool:
        return (
            scope in self.scopes
            and self.effective_from <= at
            and (self.effective_until is None or at < self.effective_until)
            and (self.revoked_at is None or at < self.revoked_at)
        )


class TradingMandate(AccountAccessGrant, frozen=True):
    strategy_ids: frozenset[str]


class Household(BaseModel, frozen=True):
    household_id: str
    display_name: str
