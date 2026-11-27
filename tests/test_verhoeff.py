import unittest
from truthlens.fields import aadhaar_checksum_ok

D = [
    [0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],
    [3,4,0,1,2,8,9,5,6,7],[4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],
    [6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],[8,7,6,5,9,3,2,1,0,4],
    [9,8,7,6,5,4,3,2,1,0],
]
P = [
    [0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],
    [8,9,1,6,0,4,3,5,2,7],[9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],
    [2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8],
]
INV = [0,4,3,2,1,5,6,7,8,9]


def make_valid(first11: str) -> str:
    c = 0
    for i, ch in enumerate(reversed(first11)):
        c = D[c][P[(i + 1) % 8][int(ch)]]
    return first11 + str(INV[c])


class VerhoeffTests(unittest.TestCase):
    def test_valid_number_passes(self):
        self.assertTrue(aadhaar_checksum_ok(make_valid("23456789012")))

    def test_wrong_last_digit_fails(self):
        valid = make_valid("23456789012")
        bad = valid[:-1] + str((int(valid[-1]) + 1) % 10)
        self.assertFalse(aadhaar_checksum_ok(bad))