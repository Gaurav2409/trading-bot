from trading_os.execution.protection import ProtectionState, ProtectionSupervisor


def test_fill_is_not_managed_until_broker_confirmed_protection() -> None:
    sup = ProtectionSupervisor.required(covered_quantity=10)
    assert sup.state is ProtectionState.PENDING_FILL
    sup = sup.on_fill(filled_quantity=10)
    assert sup.state is ProtectionState.PENDING_PROTECTION
    # Not PROTECTED until a broker-confirmed stop covers the reconciled quantity.
    sup = sup.on_protection_observed(stop_quantity=10)
    assert sup.state is ProtectionState.PROTECTED


def test_partial_protection_is_degraded() -> None:
    sup = ProtectionSupervisor.required(covered_quantity=10).on_fill(10)
    sup = sup.on_protection_observed(stop_quantity=6)
    assert sup.state is ProtectionState.DEGRADED


def test_protection_failure_enters_management_only_without_guessing_quantity() -> None:
    sup = ProtectionSupervisor.required(covered_quantity=10).on_fill(10)
    sup = sup.on_protection_failed()
    assert sup.state is ProtectionState.FAILED
    assert sup.fences_new_entries is True
    # It never fabricates a close quantity when custody is stale.
    assert sup.guessed_close_quantity is None


def test_unrequired_when_no_position() -> None:
    sup = ProtectionSupervisor.unrequired()
    assert sup.state is ProtectionState.UNREQUIRED
    assert sup.fences_new_entries is False
