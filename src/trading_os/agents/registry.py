from datetime import datetime
from hashlib import sha256

from trading_os.agents.models import (
    AgentProfileRelease,
    ReleaseClosure,
    ReleaseStatus,
    TrajectoryRelease,
)
from trading_os.research.models import EvidenceDomain


class ReleaseResolutionError(RuntimeError):
    """Raised when a domain does not resolve to exactly one effective closure."""


_EFFECTIVE_STATUSES = frozenset({ReleaseStatus.SHADOW, ReleaseStatus.ACTIVE})


class ReleaseRegistry:
    def __init__(
        self,
        profiles: tuple[AgentProfileRelease, ...],
        trajectories: tuple[TrajectoryRelease, ...],
    ) -> None:
        self._profiles = profiles
        self._trajectories = {item.release_id: item for item in trajectories}

    def resolve(self, domain: EvidenceDomain, cutoff: datetime) -> ReleaseClosure:
        matches = tuple(
            item
            for item in self._profiles
            if item.domain is domain
            and item.effective_from <= cutoff
            and (item.effective_until is None or cutoff < item.effective_until)
            and item.status in _EFFECTIVE_STATUSES
        )
        if len(matches) != 1:
            raise ReleaseResolutionError(
                "exactly one effective profile is required"
            )
        profile = matches[0]
        trajectory = self._trajectories.get(profile.trajectory_release_id)
        if trajectory is None:
            raise ReleaseResolutionError("trajectory release is unavailable")
        digest = sha256(
            f"{profile.content_hash}\x00{trajectory.content_hash}".encode()
        ).hexdigest()
        return ReleaseClosure(
            profile=profile,
            trajectory=trajectory,
            content_hash=f"sha256:{digest}",
        )
