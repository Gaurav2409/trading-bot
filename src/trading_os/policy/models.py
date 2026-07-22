from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from trading_os.kernel.ids import AccountId, ReleaseId


class EffectiveRelease(BaseModel, frozen=True):
    release_id: ReleaseId
    effective_from: datetime
    effective_until: datetime | None = None
    supersedes: ReleaseId | None = None


class CapitalEnvelopeRelease(EffectiveRelease, frozen=True):
    account_id: AccountId
    currency: str
    capital_minor: int = Field(gt=0)
    max_cumulative_loss_minor: int = Field(gt=0)
    automatic_reload: bool = False

    @model_validator(mode="after")
    def validate_loss_ceiling(self) -> "CapitalEnvelopeRelease":
        if self.max_cumulative_loss_minor > self.capital_minor:
            raise ValueError("maximum cumulative loss cannot exceed the capital envelope")
        return self


class ExposurePolicyRelease(EffectiveRelease, frozen=True):
    account_id: AccountId
    max_deployed_fraction: float = Field(gt=0, le=1)
    max_symbol_fraction: float = Field(gt=0, le=1)


class PromotionPolicyRelease(EffectiveRelease, frozen=True):
    account_id: AccountId
    tier: str
    required_protected_entries: int = Field(ge=0)
    required_reconciled_exits: int = Field(ge=0)
    daily_loss_cooldown_ppm: int = Field(ge=0, le=1_000_000)
    retrospective_drawdown_ppm: int = Field(ge=0, le=1_000_000)
    promotion_block_drawdown_ppm: int = Field(ge=0, le=1_000_000)
    demote_drawdown_ppm: int = Field(ge=0, le=1_000_000)
    restart_drawdown_ppm: int = Field(ge=0, le=1_000_000)
    stop_drawdown_ppm: int = Field(ge=0, le=1_000_000)


class PolicySet(BaseModel, frozen=True):
    capital: CapitalEnvelopeRelease
    exposure: ExposurePolicyRelease
    promotion: PromotionPolicyRelease
