"""Broker-specific portfolio normalization.

Never applies generic summation to holdings and positions. Kite holdings and
day positions are different lifecycle views of the same custody; a manual record
that matches broker custody becomes provenance, not extra quantity.
"""

from pydantic import BaseModel


class MergedPosition(BaseModel, frozen=True):
    total_owned: int
    saleable_before_local_reservations: int
    provenance: str


def merge_kite_holding_and_position(
    *,
    settled_available: int,
    unsettled: int,
    pledged: int,
    day_net: int,
    broker_saleable: int,
    manual_quantity: int | None = None,
) -> MergedPosition:
    """Merge a Kite delivery holding with its day (net) position without double
    counting.

    ``settled_available``/``unsettled``/``pledged`` are non-overlapping custody
    buckets; total owned is their sum. ``day_net`` is the intraday net position
    for the same instrument — when it is zero it represents no additional
    delivery custody and must not be added again.
    """
    total_owned = settled_available + unsettled + pledged
    # A non-zero settled day_net that is already reflected in holdings is not
    # re-added; only genuinely additional intraday delivery would increase it,
    # which V1's long-only delivery flow does not produce here.
    provenance = "broker_snapshot_only"
    if manual_quantity is not None:
        provenance = "manual_matched_broker" if manual_quantity == total_owned else "manual_unmatched"
    return MergedPosition(
        total_owned=total_owned,
        saleable_before_local_reservations=broker_saleable,
        provenance=provenance,
    )
