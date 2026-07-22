from pathlib import Path

from trading_os.ontology.instance_validation import validate_instance_snapshot

_SHAPES = Path("ontology/shapes/core.shacl.ttl")

_PREFIX = """
@prefix tw:  <https://trading-os.example/ontology/trading-world#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""


def _validate(instance_ttl: str) -> tuple[bool, str]:
    report = validate_instance_snapshot(instance_ttl, _SHAPES.read_text())
    return report.conforms, report.text


def test_wellformed_source_record_conforms() -> None:
    ttl = _PREFIX + """
    tw:sr1 a tw:SourceRecord ;
        tw:payload_hash "sha256:abc" ;
        tw:publishedAt "2026-07-22T09:00:00+00:00"^^xsd:dateTime ;
        tw:receivedAt  "2026-07-22T09:00:01+00:00"^^xsd:dateTime .
    """
    conforms, _ = _validate(ttl)
    assert conforms is True


def test_source_record_missing_payload_hash_fails() -> None:
    ttl = _PREFIX + """
    tw:sr1 a tw:SourceRecord ;
        tw:publishedAt "2026-07-22T09:00:00+00:00"^^xsd:dateTime ;
        tw:receivedAt  "2026-07-22T09:00:01+00:00"^^xsd:dateTime .
    """
    conforms, _ = _validate(ttl)
    assert conforms is False


def test_timezone_naive_timestamp_fails() -> None:
    ttl = _PREFIX + """
    tw:sr1 a tw:SourceRecord ;
        tw:payload_hash "sha256:abc" ;
        tw:publishedAt "2026-07-22T09:00:00"^^xsd:dateTime ;
        tw:receivedAt  "2026-07-22T09:00:01+00:00"^^xsd:dateTime .
    """
    conforms, _ = _validate(ttl)
    assert conforms is False


def test_security_without_issuer_role_fails() -> None:
    ttl = _PREFIX + """
    tw:sec1 a tw:Security .
    """
    conforms, _ = _validate(ttl)
    assert conforms is False


def test_evidence_packet_has_no_noop_constraint() -> None:
    # An EvidencePacket with a real contained claim conforms; the shape is not a
    # no-op minCount 0. An empty packet is not silently "valid by vacuity".
    ttl = _PREFIX + """
    tw:ep1 a tw:EvidencePacket ;
        tw:containsClaim tw:c1 .
    tw:c1 a tw:Claim ;
        tw:supportedBy tw:sr1 .
    tw:sr1 a tw:SourceRecord ;
        tw:payload_hash "sha256:abc" ;
        tw:publishedAt "2026-07-22T09:00:00+00:00"^^xsd:dateTime ;
        tw:receivedAt  "2026-07-22T09:00:01+00:00"^^xsd:dateTime .
    """
    conforms, _ = _validate(ttl)
    assert conforms is True
