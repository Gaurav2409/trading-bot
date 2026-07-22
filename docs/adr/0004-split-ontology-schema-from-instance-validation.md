---
status: accepted
---

# Split ontology-schema validation from instance-snapshot validation

The Task-11 release builder parsed `core.ttl` as its SHACL `data_graph` and applied instance-targeted
node shapes to the vocabulary itself. Because a vocabulary contains no instance focus nodes, the
shapes did no work: an empty or field-less ontology could report `conforms=True` without ever testing
a real SourceRecord, Security or EvidencePacket. `OntologyRelease.conforms=True` therefore meant only
"the Turtle parsed", not "the semantic contract is sound".

We separate two validation stages that were conflated:

1. **Ontology-schema validation** (build time): parse every meaning-bearing module, enforce
   ontology-document conventions (an ontology IRI and `owl:versionIRI` must be present), run bounded
   lint/consistency checks, and run positive/negative entailment fixtures. This never claims that
   instance data is valid.
2. **Instance-snapshot validation** (before sealing a semantic snapshot): apply SHACL to actual
   canonical semantic facts, retain validation reports and rejected facts.

The release manifest hashes each meaning-bearing artifact (ontology modules, shapes, mappings,
inference/query policies) rather than the raw bytes of two files, so whitespace or comment churn no
longer changes release identity and future mappings/rules fall inside the hash. This costs an extra
validation path and a manifest type, but prevents an empty vocabulary from masquerading as a
validated semantic contract and keeps the relational baseline the authoritative decision champion.
