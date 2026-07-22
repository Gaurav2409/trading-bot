"""Multi-clock scheduling.

APScheduler jobs trigger broad scans (daily/hourly/15m), shortlist refresh
(1m/5m), configured decision windows, and second-level protection/reconciliation
checks. Decision-window policy is re-checked inside the cycle, so a scheduler
misfire cannot trade. This adds intraday discovery, not a day-trading mandate.
"""

from collections.abc import Awaitable, Callable

from pydantic import BaseModel


class ScheduledJob(BaseModel, frozen=True):
    name: str
    trigger: str  # e.g. "cron", "interval"
    spec: str  # human-readable schedule spec
    clock: str  # discovery | shortlist | decision | protection | watcher


DEFAULT_JOBS: tuple[ScheduledJob, ...] = (
    ScheduledJob(name="broad_scan_daily", trigger="cron", spec="0 18 * * *", clock="discovery"),
    ScheduledJob(name="broad_scan_hourly", trigger="cron", spec="0 * * * *", clock="discovery"),
    ScheduledJob(name="broad_scan_15m", trigger="interval", spec="15m", clock="discovery"),
    ScheduledJob(name="shortlist_5m", trigger="interval", spec="5m", clock="shortlist"),
    ScheduledJob(name="decision_window", trigger="cron", spec="*/30 3-10 * * *", clock="decision"),
    ScheduledJob(name="protection_check", trigger="interval", spec="1s", clock="protection"),
    ScheduledJob(name="reconcile", trigger="interval", spec="30s", clock="protection"),
    ScheduledJob(name="filing_watcher", trigger="interval", spec="5m", clock="watcher"),
)


class SchedulerPlan:
    """Describes the jobs; binding to an APScheduler instance happens in the
    running app. Kept as data so it is testable without a live scheduler."""

    def __init__(self, jobs: tuple[ScheduledJob, ...] = DEFAULT_JOBS) -> None:
        self.jobs = jobs

    def clocks(self) -> set[str]:
        return {job.clock for job in self.jobs}

    def register(
        self, add_job: Callable[[str, str, str, Callable[[], Awaitable[None]]], None]
    ) -> None:  # pragma: no cover - thin adapter over APScheduler
        raise NotImplementedError("bound at runtime by the running application")
