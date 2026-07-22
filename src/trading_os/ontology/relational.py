"""The permanent relational retrieval baseline.

Answers competency questions from snapshot-scoped structured records with no
dependency on Fuseki or Neo4j. This is the production decision champion; the
graph projections are rebuildable research/audit paths only.
"""

from trading_os.research.models import EvidencePacket


class RelationalRetrievalBaseline:
    def __init__(self, evidence: list[EvidencePacket]) -> None:
        self._evidence = tuple(evidence)

    def evidence_for(
        self, instrument_id: str, data_snapshot_id: str
    ) -> tuple[EvidencePacket, ...]:
        return tuple(
            packet
            for packet in self._evidence
            if packet.instrument_id == instrument_id
            and packet.data_snapshot_id == data_snapshot_id
        )
