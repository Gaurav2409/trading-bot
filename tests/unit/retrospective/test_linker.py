from trading_os.retrospective.linker import DecisionOutcomeRecord, link_outcome


def test_outcome_record_binds_all_provenance_without_rewriting_sources() -> None:
    record = link_outcome(
        candidate_id="cand-1",
        coverage_receipt_id="cov-1",
        tradability_packet_id="trad-1",
        evidence_packet_ids=("ev-1", "ev-2"),
        decision_feature_set_id="feat-1",
        portfolio_snapshot_id="psnap-1",
        data_snapshot_id="dsnap-1",
        semantic_snapshot_id=None,
        policy_release_ids=("cap-1", "exp-1"),
        provisional_quantity=10,
        final_quantity=5,
        order_intent_id="intent-1",
        broker_pnl_minor=1500,
        os_pnl_minor=1400,
        unknown_pnl_minor=0,
    )
    assert isinstance(record, DecisionOutcomeRecord)
    assert record.coverage_receipt_id == "cov-1"
    assert record.evidence_packet_ids == ("ev-1", "ev-2")
    # Separately labelled P&L, never blended.
    assert record.broker_pnl_minor == 1500
    assert record.os_pnl_minor == 1400
    assert record.unknown_pnl_minor == 0
