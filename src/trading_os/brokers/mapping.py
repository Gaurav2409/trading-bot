from trading_os.kernel.ids import InstrumentId


def canonical_equity_id(venue: str, isin_or_symbol: str) -> InstrumentId:
    normalized_venue = venue.upper()
    normalized_key = isin_or_symbol.upper()
    return InstrumentId(f"{normalized_venue}:{normalized_key}")


class LiveWriteDisabled(RuntimeError):
    """Raised when a read-only adapter is asked to submit or cancel an order.

    Live writes are enabled only in Task 15, behind an ExecutionAuthority and a
    broker-scoped LiveAuthorityReceipt.
    """
