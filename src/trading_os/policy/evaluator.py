from datetime import datetime

from trading_os.policy.models import EffectiveRelease


class PolicyEvaluator:
    def is_effective(self, release: EffectiveRelease, at: datetime) -> bool:
        return release.effective_from <= at and (
            release.effective_until is None or at < release.effective_until
        )
