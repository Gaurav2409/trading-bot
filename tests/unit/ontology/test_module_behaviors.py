"""Instance-validation behaviors for the P1 reasoning modules.

Each test loads the relevant module's SHACL shapes and validates a small instance
graph, asserting the MoA-mandated safety behaviors (false-merge, cutoff, correction
lineage, relationship typing, contradiction target, projection closure).
"""

from pathlib import Path

from trading_os.ontology.instance_validation import validate_instance_snapshot

_SHAPES_DIR = Path("ontology/modules/shapes")

_PREFIX = """
@prefix tw:  <https://trading-os.example/ontology/trading-world#> .
@prefix id:  <https://trading-os.example/ontology/identity#> .
@prefix tm:  <https://trading-os.example/ontology/time#> .
@prefix pv:  <https://trading-os.example/ontology/provenance#> .
@prefix ev:  <https://trading-os.example/ontology/events#> .
@prefix pf:  <https://trading-os.example/ontology/portfolio#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""


def _validate(shapes_file: str, instance_ttl: str) -> bool:
    shapes = (_SHAPES_DIR / shapes_file).read_text()
    return validate_instance_snapshot(_PREFIX + instance_ttl, shapes).conforms


# --- H6a identity: false merge requires a governed IdentityAssertion ---

def test_two_securities_equated_without_governed_assertion_fails() -> None:
    ttl = """
    id:secA a id:Security ; id:mapsToInstrument id:secB .
    id:secB a id:Security .
    """
    assert _validate("identity.shacl.ttl", ttl) is False


def test_mapping_with_governed_assertion_and_interval_conforms() -> None:
    ttl = """
    id:secA a id:Security .
    id:brokerInstr a id:BrokerInstrument ;
        id:mapsToInstrument id:secA ;
        id:mappingAssertion id:ia1 ;
        id:validFrom "2026-01-01T00:00:00+00:00"^^xsd:dateTime .
    id:ia1 a id:IdentityAssertion ; id:assertionStatus "confirmed" .
    """
    assert _validate("identity.shacl.ttl", ttl) is True


# --- H7a time: a fact received after the decision cutoff must fail ---

def test_fact_received_after_cutoff_fails() -> None:
    ttl = """
    tm:snap1 a tm:SemanticSnapshot ; tm:decisionCutoffAt "2026-07-22T10:00:00+00:00"^^xsd:dateTime .
    tm:fact1 a tm:TimedFact ;
        tm:inSnapshot tm:snap1 ;
        tm:receivedAt "2026-07-22T10:00:01+00:00"^^xsd:dateTime .
    """
    assert _validate("time.shacl.ttl", ttl) is False


def test_fact_received_at_or_before_cutoff_conforms() -> None:
    ttl = """
    tm:snap1 a tm:SemanticSnapshot ; tm:decisionCutoffAt "2026-07-22T10:00:00+00:00"^^xsd:dateTime .
    tm:fact1 a tm:TimedFact ;
        tm:inSnapshot tm:snap1 ;
        tm:receivedAt "2026-07-22T09:59:59+00:00"^^xsd:dateTime .
    """
    assert _validate("time.shacl.ttl", ttl) is True


# --- H7b provenance: correction must name a superseded target; forward guidance allowed ---

def test_correction_without_superseded_target_fails() -> None:
    ttl = """
    pv:corr1 a pv:CorrectionActivity .
    """
    assert _validate("provenance.shacl.ttl", ttl) is False


def test_correction_with_superseded_target_conforms() -> None:
    ttl = """
    pv:rec2 a pv:SourceRecord .
    pv:rec1 a pv:SourceRecord .
    pv:corr1 a pv:CorrectionActivity ;
        pv:supersedes pv:rec1 ;
        pv:generatedRecord pv:rec2 .
    """
    assert _validate("provenance.shacl.ttl", ttl) is True


def test_forward_guidance_effective_after_received_is_allowed() -> None:
    ttl = """
    pv:g1 a pv:ForwardGuidanceRecord ;
        tm:receivedAt "2026-07-22T09:00:00+00:00"^^xsd:dateTime ;
        tm:effectiveAt "2026-09-01T00:00:00+00:00"^^xsd:dateTime .
    """
    assert _validate("provenance.shacl.ttl", ttl) is True


# --- H9 events: a RelationshipAssertion must carry a relationshipType ---

def test_relationship_assertion_without_type_fails() -> None:
    ttl = """
    ev:r1 a ev:RelationshipAssertion ; ev:subject id:secA ; ev:object id:secB .
    """
    assert _validate("events.shacl.ttl", ttl) is False


def test_relationship_assertion_with_type_conforms() -> None:
    ttl = """
    ev:r1 a ev:RelationshipAssertion ;
        ev:subject id:secA ; ev:object id:secB ;
        ev:relationshipType "CONTRACTUAL" .
    """
    assert _validate("events.shacl.ttl", ttl) is True


# --- H11 portfolio: projection node may not carry a raw quantity/cash literal ---

def test_projection_with_raw_quantity_literal_fails() -> None:
    ttl = """
    pf:p1 a pf:PortfolioProjection ;
        pf:concentrationBand "high" ;
        pf:rawQuantity 100 .
    """
    assert _validate("portfolio.shacl.ttl", ttl) is False


def test_projection_with_only_governed_categories_conforms() -> None:
    ttl = """
    pf:p1 a pf:PortfolioProjection ;
        pf:concentrationBand "high" ;
        pf:exposureCategory "metals" .
    """
    assert _validate("portfolio.shacl.ttl", ttl) is True
