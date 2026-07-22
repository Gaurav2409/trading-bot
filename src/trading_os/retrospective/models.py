from pydantic import BaseModel


class DecisionOutcomeRecord(BaseModel, frozen=True):
    """Immutable linkage from a decision to its realized outcome. Binds every
    provenance id without rewriting any source event; broker-reported, OS-ledger
    and unknown/partial P&L stay separately labelled."""

    candidate_id: str
    coverage_receipt_id: str
    tradability_packet_id: str
    evidence_packet_ids: tuple[str, ...]
    decision_feature_set_id: str
    portfolio_snapshot_id: str
    data_snapshot_id: str
    semantic_snapshot_id: str | None
    policy_release_ids: tuple[str, ...]
    provisional_quantity: int
    final_quantity: int
    order_intent_id: str
    broker_pnl_minor: int
    os_pnl_minor: int
    unknown_pnl_minor: int
