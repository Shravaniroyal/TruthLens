import tempfile
import unittest
from pathlib import Path

from truthlens.review import ReviewStore, should_review


class ReviewStoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.store = ReviewStore(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def _add(self, verdict="UNCERTAIN"):
        return self.store.add_if_needed(
            verdict,
            filename="scan1.jpg",
            content_hash="a" * 64,
            doc_type="pan",
            confidence=62.5,
            fields_masked={"pan": "ABCXXXX34F"},
            case_id="case1",
            operator="op1",
        )

    def test_real_is_not_queued(self):
        self.assertFalse(should_review("REAL"))
        self.assertIsNone(self._add("REAL"))
        self.assertEqual(self.store.list(), [])

    def test_fake_and_uncertain_are_queued(self):
        self.assertIsNotNone(self._add("FAKE"))
        self.assertIsNotNone(self._add("UNCERTAIN"))
        self.assertEqual(len(self.store.list(status="pending")), 2)

    def test_decision_recorded(self):
        item = self._add()
        done = self.store.decide(item.id, "need_original", "Reviewer A", "photo too dark")
        self.assertEqual(done.status, "need_original")
        self.assertEqual(done.reviewer, "Reviewer A")
        self.assertTrue(done.decided_at)
        self.assertEqual(len(self.store.list(status="pending")), 0)

    def test_bad_decision_and_missing_reviewer_rejected(self):
        item = self._add()
        with self.assertRaises(ValueError):
            self.store.decide(item.id, "maybe", "Reviewer A")
        with self.assertRaises(ValueError):
            self.store.decide(item.id, "accepted", "  ")

    def test_path_traversal_id_rejected(self):
        with self.assertRaises(KeyError):
            self.store.get("../../etc/passwd")


if __name__ == "__main__":
    unittest.main()
