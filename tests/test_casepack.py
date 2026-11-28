import unittest
from types import SimpleNamespace as NS

from truthlens.casepack import _outcome, build_case_pack

ROWS = [
    {"file": "a.jpg", "type": "PAN", "slot": "pan", "verdict": "FAKE", "qr": "no"},
    {"file": "b.jpg", "type": "Marksheet", "slot": "marksheet", "verdict": "REAL", "qr": "no"},
]


def _item(name, status):
    return NS(filename=name, verdict="FAKE", confidence=90.0, status=status,
              reviewer="R" if status != "pending" else "", decided_at="2026-11-28T10:00:00+00:00", note="")


class CasePackTests(unittest.TestCase):
    def test_pdf_is_built(self):
        pdf = build_case_pack(case_id="abc", workflow_label="Job joining", operator="op & co",
                              rows=ROWS, complete=True, missing=[], items=[_item("a.jpg", "rejected")])
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1500)

    def test_incomplete_kit_outcome(self):
        self.assertEqual(_outcome(False, ROWS, [])[0], "INCOMPLETE")

    def test_flagged_file_is_never_reported_clear(self):
        self.assertEqual(_outcome(True, ROWS, [])[0], "PENDING REVIEW")
        self.assertEqual(_outcome(True, ROWS, [_item("a.jpg", "pending")])[0], "PENDING REVIEW")

    def test_decided_outcomes(self):
        self.assertEqual(_outcome(True, ROWS, [_item("a.jpg", "rejected")])[0], "ACTION NEEDED")
        self.assertEqual(_outcome(True, ROWS, [_item("a.jpg", "accepted")])[0], "SCREENING CLEAR")


if __name__ == "__main__":
    unittest.main()
