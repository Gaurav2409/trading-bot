from collections.abc import Callable, Iterable
from typing import TypeVar

from trading_os.ledger.tables import EventRow

S = TypeVar("S")


def replay(
    rows: Iterable[EventRow],
    initial: S,
    reducer: Callable[[S, EventRow], S],
) -> S:
    """Fold an ordered event stream into a projected state.

    Deterministic: the same ordered rows and reducer always yield the same
    state. Rows must already be ordered by ``stream_version`` (as returned by
    ``EventStore.read_stream``).
    """
    state = initial
    for row in rows:
        state = reducer(state, row)
    return state
