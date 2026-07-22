from datetime import datetime

from trading_os.market_data.models import Bar


def validate_bar(bar: Bar, cutoff: datetime, require_entitlement: str | None) -> str | None:
    """Return a rejection reason, or None if the bar is admissible.

    Enforces decision-cutoff freshness, OHLC consistency, non-negative volume,
    and (optionally) a required data entitlement so an IEX-only feed cannot
    silently claim whole-market SIP coverage.
    """
    if bar.received_at > cutoff:
        return "received_after_cutoff"
    if not (bar.low <= bar.open <= bar.high and bar.low <= bar.close <= bar.high):
        return "ohlc_inconsistent"
    if bar.low > bar.high:
        return "ohlc_inconsistent"
    if bar.volume < 0:
        return "negative_volume"
    if require_entitlement is not None and bar.entitlement != require_entitlement:
        return f"entitlement_mismatch:{bar.entitlement}!={require_entitlement}"
    return None
