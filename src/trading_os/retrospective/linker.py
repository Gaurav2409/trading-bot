from trading_os.retrospective.models import DecisionOutcomeRecord


def link_outcome(
    *,
    candidate_id: str,
    coverage_receipt_id: str,
    tradability_packet_id: str,
    evidence_packet_ids: tuple[str, ...],
    decision_feature_set_id: str,
    portfolio_snapshot_id: str,
    data_snapshot_id: str,
    semantic_snapshot_id: str | None,
    policy_release_ids: tuple[str, ...],
    provisional_quantity: int,
    final_quantity: int,
    order_intent_id: str,
    broker_pnl_minor: int,
    os_pnl_minor: int,
    unknown_pnl_minor: int,
) -> DecisionOutcomeRecord:
    return DecisionOutcomeRecord(
        candidate_id=candidate_id,
        coverage_receipt_id=coverage_receipt_id,
        tradability_packet_id=tradability_packet_id,
        evidence_packet_ids=evidence_packet_ids,
        decision_feature_set_id=decision_feature_set_id,
        portfolio_snapshot_id=portfolio_snapshot_id,
        data_snapshot_id=data_snapshot_id,
        semantic_snapshot_id=semantic_snapshot_id,
        policy_release_ids=policy_release_ids,
        provisional_quantity=provisional_quantity,
        final_quantity=final_quantity,
        order_intent_id=order_intent_id,
        broker_pnl_minor=broker_pnl_minor,
        os_pnl_minor=os_pnl_minor,
        unknown_pnl_minor=unknown_pnl_minor,
    )
