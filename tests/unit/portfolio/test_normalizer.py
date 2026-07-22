from trading_os.portfolio.normalizer import merge_kite_holding_and_position


def test_zero_net_day_position_does_not_duplicate_delivery_holding() -> None:
    merged = merge_kite_holding_and_position(
        settled_available=7,
        unsettled=2,
        pledged=1,
        day_net=0,
        broker_saleable=7,
    )
    assert merged.total_owned == 10
    assert merged.saleable_before_local_reservations == 7


def test_manual_record_adds_provenance_not_quantity() -> None:
    merged = merge_kite_holding_and_position(
        settled_available=7,
        unsettled=2,
        pledged=1,
        day_net=0,
        broker_saleable=7,
        manual_quantity=10,
    )
    assert merged.total_owned == 10
    assert merged.provenance == "manual_matched_broker"


def test_ambiguous_manual_quantity_creates_conflict_not_quantity() -> None:
    merged = merge_kite_holding_and_position(
        settled_available=7,
        unsettled=2,
        pledged=1,
        day_net=0,
        broker_saleable=7,
        manual_quantity=99,
    )
    # A manual quantity that does not match broker custody must not add quantity.
    assert merged.total_owned == 10
    assert merged.provenance == "manual_unmatched"
