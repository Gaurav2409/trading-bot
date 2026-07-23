from trading_os.research.seen_store import InMemorySeenRecordStore


def test_first_sighting_is_new_then_duplicate_is_not() -> None:
    store = InMemorySeenRecordStore()
    assert store.is_new("nse", "nse:A1", "sha256:x") is True
    assert store.is_new("nse", "nse:A1", "sha256:x") is False


def test_same_id_different_hash_is_new_again() -> None:
    # A corrected/replaced payload for the same announcement id is a new sighting.
    store = InMemorySeenRecordStore()
    assert store.is_new("nse", "nse:A1", "sha256:x") is True
    assert store.is_new("nse", "nse:A1", "sha256:y") is True


def test_channels_are_independent() -> None:
    store = InMemorySeenRecordStore()
    assert store.is_new("nse", "id", "sha256:x") is True
    assert store.is_new("bse", "id", "sha256:x") is True
