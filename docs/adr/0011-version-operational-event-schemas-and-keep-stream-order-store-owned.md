---
status: accepted
---

# Version operational-event schemas and keep stream order store-owned

Operational events must remain replayable as their payloads evolve, while
optimistic stream ordering must remain authoritative under concurrent writers.
Event occurrence time, schema compatibility, and stream position answer
different questions and cannot safely share one version field.

Every operational fact has a closed semantic `EventType` and an immutable
composite schema tag such as `order_intent_created.v1`. The caller creates an
envelope from a typed payload; the event type and numeric schema version are
derived and verified during deserialization. A change to a published payload's
persisted wire shape or meaning adds a new readable schema such as `v2` rather
than mutating `v1` or using a datetime as a compatibility marker.

The caller-created envelope does not contain authoritative stream location. The
event store atomically assigns `stream_id` and monotonically increasing
`stream_version`, returning a `StoredEvent` on replay. The existing convention is
retained: an empty stream is version `0` and its first committed event is version
`1`.

This creates explicit reader-evolution work when a schema changes and retains old
payload models for replay. We accept that cost because it prevents timestamps
from masquerading as compatibility, prevents callers from claiming committed
order, and makes history deterministic across in-memory and PostgreSQL stores.
