from datetime import UTC, datetime

from trading_os.kernel.ids import AccountId, InstrumentId, SnapshotId
from trading_os.tradability.builder import TradabilityInput, build_tradability_packet


def _base_input(**overrides: object) -> TradabilityInput:
    base = dict(
        account_id=AccountId("kite-1"),
        instrument_id=InstrumentId("BSE:INE000000001"),
        broker="kite",
        listing_active=True,
        broker_orderable=True,
        surveillance_flags=(),
        circuit_or_band_state="normal",
        liquidity_state="adequate",
        stop_feasible=True,
        raw_adjusted_lineage_valid=True,
        account_restrictions=(),
        data_snapshot_id=SnapshotId("data-1"),
        data_fresh_at=datetime(2026, 7, 22, tzinfo=UTC),
        compliance_release_id="india-v1",
    )
    base.update(overrides)
    return TradabilityInput(**base)  # type: ignore[arg-type]


def test_healthy_candidate_is_eligible() -> None:
    packet = build_tradability_packet(_base_input())
    assert packet.eligible is True
    assert packet.reason_codes == ()


def test_upper_circuit_lock_is_not_eligible() -> None:
    packet = build_tradability_packet(_base_input(circuit_or_band_state="upper_circuit"))
    assert packet.eligible is False
    assert "circuit_locked" in packet.reason_codes


def test_infeasible_stop_blocks_eligibility() -> None:
    packet = build_tradability_packet(_base_input(stop_feasible=False))
    assert packet.eligible is False
    assert "stop_infeasible" in packet.reason_codes


def test_surveillance_flag_blocks_eligibility() -> None:
    packet = build_tradability_packet(_base_input(surveillance_flags=("ASM",)))
    assert packet.eligible is False
    assert "under_surveillance" in packet.reason_codes


def test_not_orderable_blocks_eligibility() -> None:
    packet = build_tradability_packet(_base_input(broker_orderable=False))
    assert packet.eligible is False
    assert "not_broker_orderable" in packet.reason_codes
