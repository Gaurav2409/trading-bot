from trading_os.execution.reconciliation import DifferenceClass, reconcile_quantity


def test_unexplained_broker_quantity_blocks_new_exposure() -> None:
    difference = reconcile_quantity(broker_quantity=12, os_expected_quantity=10)
    assert difference.kind is DifferenceClass.UNEXPLAINED_CUSTODY
    assert difference.fail_direction == "entry_disabled"


def test_matching_quantity_is_no_difference() -> None:
    difference = reconcile_quantity(broker_quantity=10, os_expected_quantity=10)
    assert difference.kind is DifferenceClass.NONE
    assert difference.fail_direction == "none"


def test_broker_lower_than_os_is_unexplained_custody() -> None:
    difference = reconcile_quantity(broker_quantity=8, os_expected_quantity=10)
    assert difference.kind is DifferenceClass.UNEXPLAINED_CUSTODY
    assert difference.fail_direction == "entry_disabled"
