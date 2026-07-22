from pydantic import BaseModel, Field

from trading_os.research.models import RiskOverlaySet


class RiskInput(BaseModel, frozen=True):
    provisional_quantity: int = Field(ge=0)
    entry_price_minor: int = Field(gt=0)
    deployed_minor: int = Field(ge=0)
    max_deployed_minor: int = Field(gt=0)
    symbol_exposure_minor: int = Field(ge=0)
    max_symbol_minor: int = Field(gt=0)
    overlay: RiskOverlaySet


class RiskDecision(BaseModel, frozen=True):
    final_quantity: int = Field(ge=0)
    reason_codes: tuple[str, ...]


class RiskEngine:
    """Applies deterministic caps to a provisional size, then the tighten-only
    overlay. Every step may shrink or veto; none may increase the quantity."""

    def evaluate(self, value: RiskInput) -> RiskDecision:
        reasons: list[str] = []
        quantity = value.provisional_quantity

        symbol_headroom_minor = max(0, value.max_symbol_minor - value.symbol_exposure_minor)
        by_symbol = symbol_headroom_minor // value.entry_price_minor
        if by_symbol < quantity:
            quantity = by_symbol
            reasons.append("symbol_cap")

        deploy_headroom_minor = max(0, value.max_deployed_minor - value.deployed_minor)
        by_deploy = deploy_headroom_minor // value.entry_price_minor
        if by_deploy < quantity:
            quantity = by_deploy
            reasons.append("deployment_cap")

        if value.overlay.veto:
            reasons.extend(value.overlay.reason_codes or ("overlay_veto",))
            return RiskDecision(final_quantity=0, reason_codes=tuple(reasons))

        shrunk = int(quantity * value.overlay.multiplier)
        if shrunk < quantity:
            quantity = shrunk
            reasons.extend(value.overlay.reason_codes or ("overlay_tightened",))

        return RiskDecision(final_quantity=quantity, reason_codes=tuple(reasons))
