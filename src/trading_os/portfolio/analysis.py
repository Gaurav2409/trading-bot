from pydantic import BaseModel, Field

from trading_os.kernel.ids import AccountId, InstrumentId
from trading_os.portfolio.completeness import PortfolioCompletenessVector
from trading_os.portfolio.projector import AccountPortfolioProjection


class PortfolioRiskOverlaySet(BaseModel, frozen=True):
    """Tighten-only overlay. The multiplier is in (0, 1]; it may shrink or veto,
    never increase, a provisional size."""

    multiplier: float = Field(gt=0, le=1)
    veto: bool = False
    reason_codes: tuple[str, ...] = ()


class CurrentPortfolioAnalysis(BaseModel, frozen=True):
    account_id: AccountId
    gate_ready: bool
    candidate_instrument: InstrumentId
    candidate_sector: str
    sector_exposure_minor: int
    sector_cap_minor: int
    overlay: PortfolioRiskOverlaySet

    @classmethod
    def build(
        cls,
        projection: AccountPortfolioProjection,
        completeness: PortfolioCompletenessVector,
        *,
        candidate_instrument: InstrumentId,
        candidate_sector: str,
        sector_of: dict[InstrumentId, str],
        sector_cap_minor: int,
        price_minor: dict[InstrumentId, int],
    ) -> "CurrentPortfolioAnalysis":
        # Existing exposure in the candidate's sector, including external/manual
        # holdings already present in the projection.
        sector_exposure = 0
        for instrument, buckets in projection.positions.items():
            if sector_of.get(instrument) == candidate_sector:
                sector_exposure += buckets.total_owned * price_minor.get(instrument, 0)

        overlay = _overlay_for(sector_exposure, sector_cap_minor)
        return cls(
            account_id=projection.account_id,
            gate_ready=True,
            candidate_instrument=candidate_instrument,
            candidate_sector=candidate_sector,
            sector_exposure_minor=sector_exposure,
            sector_cap_minor=sector_cap_minor,
            overlay=overlay,
        )


def _overlay_for(sector_exposure_minor: int, sector_cap_minor: int) -> PortfolioRiskOverlaySet:
    if sector_cap_minor <= 0 or sector_exposure_minor <= 0:
        return PortfolioRiskOverlaySet(multiplier=1.0)
    if sector_exposure_minor >= sector_cap_minor:
        return PortfolioRiskOverlaySet(
            multiplier=1.0, veto=True, reason_codes=("sector_cap_exceeded",)
        )
    # Remaining headroom fraction becomes the tighten-only multiplier.
    headroom = (sector_cap_minor - sector_exposure_minor) / sector_cap_minor
    return PortfolioRiskOverlaySet(
        multiplier=min(1.0, headroom),
        reason_codes=("sector_concentration_tightened",),
    )
