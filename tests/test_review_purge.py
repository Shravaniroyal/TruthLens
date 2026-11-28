from datetime import datetime, timedelta, timezone

import truthlens.review as review


def test_purge_removes_only_old_items(tmp_path):
    store = review.ReviewStore(tmp_path)
    old = store.add(filename="a", content_hash="h", doc_type="pan", verdict="FAKE", confidence=90)
    new = store.add(filename="b", content_hash="h", doc_type="pan", verdict="FAKE", confidence=90)
    item = store.get(old.id)
    item.created_at = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(timespec="seconds")
    store._write(item)

    assert store.purge_older_than(7) == 1
    ids = [i.id for i in store.list()]
    assert ids == [new.id]
