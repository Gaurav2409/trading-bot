from trading_os.execution.kill_state import KillMode, KillState, transition


def test_safety_fault_fences_entries_before_human_acknowledgement() -> None:
    state = KillState.active(account_id="acct-1", generation=1)
    stopped = transition(state, "critical_portfolio_stale")
    assert stopped.mode is KillMode.ENTRY_DISABLED
    assert stopped.generation == 2


def test_entry_disabled_keeps_reconciliation_enabled() -> None:
    state = KillState(account_id="acct-1", generation=2, mode=KillMode.ENTRY_DISABLED)
    assert state.may_increase_exposure is False
    assert state.may_reconcile is True


def test_non_safety_reason_halts() -> None:
    state = KillState.active(account_id="acct-1", generation=1)
    halted = transition(state, "owner_emergency_stop")
    assert halted.mode is KillMode.HALTED
    assert halted.generation == 2


def test_active_may_increase_exposure() -> None:
    state = KillState.active(account_id="acct-1", generation=1)
    assert state.may_increase_exposure is True
    assert state.may_reconcile is True
