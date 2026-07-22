"""Explicit field authority for current portfolio analysis (ADR-0002).

There is no single fused source of truth. Each field family has a primary
authority; disagreements become reconciliation facts rather than silent
overwrites.
"""

from enum import StrEnum


class FieldAuthority(StrEnum):
    BROKER_OBSERVATION = "broker_observation"
    OS_LEDGER = "os_ledger"
    VALIDATED_MARKET_DATA = "validated_market_data"
    SEMANTIC_PROJECTION = "semantic_projection"


# Which source is authoritative for each field family. Matches research doc 14 §1.1.
FIELD_AUTHORITY: dict[str, FieldAuthority] = {
    "custody_quantity": FieldAuthority.BROKER_OBSERVATION,
    "broker_saleable_quantity": FieldAuthority.BROKER_OBSERVATION,
    "settlement_restriction": FieldAuthority.BROKER_OBSERVATION,
    "pledge_lien": FieldAuthority.BROKER_OBSERVATION,
    "broker_order_state": FieldAuthority.BROKER_OBSERVATION,
    "cash_available": FieldAuthority.BROKER_OBSERVATION,
    "os_order_intent": FieldAuthority.OS_LEDGER,
    "os_reservation": FieldAuthority.OS_LEDGER,
    "strategy_sleeve_provenance": FieldAuthority.OS_LEDGER,
    "os_approval": FieldAuthority.OS_LEDGER,
    "decision_price": FieldAuthority.VALIDATED_MARKET_DATA,
    "fx_mark": FieldAuthority.VALIDATED_MARKET_DATA,
    "classification": FieldAuthority.SEMANTIC_PROJECTION,
    "relationships": FieldAuthority.SEMANTIC_PROJECTION,
}


def authority_for(field_name: str) -> FieldAuthority:
    return FIELD_AUTHORITY[field_name]
