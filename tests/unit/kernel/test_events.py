from datetime import UTC, datetime

from trading_os.kernel.events import new_event
from trading_os.kernel.ids import AccountId


def test_event_has_utc_recorded_time() -> None:
    event = new_event("AccountObserved", {"account_id": "acct-1"})
    assert event.recorded_at.tzinfo is UTC
    assert event.recorded_at <= datetime.now(UTC)
    assert AccountId("acct-1") == "acct-1"
