import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unittest
from main import check

def row(path, size, sha=""):
    return {"path": path, "size_bytes": str(size), "sha256": sha}

class TestCloudSyncChecker(unittest.TestCase):
    def test_in_sync(self):
        r, in_sync, _ = check([row("a.txt", 100, "aaa")],
                              [row("a.txt", 100, "aaa")])
        self.assertEqual((r, in_sync), ([], 1))

    def test_missing_in_cloud(self):
        r, _, _ = check([row("a.txt", 100, "aaa")], [])
        self.assertEqual(r[0][1], "MISSING IN CLOUD")

    def test_extra_in_cloud(self):
        r, _, _ = check([], [row("old.zip", 50, "eee")])
        self.assertEqual(r[0][1], "EXTRA IN CLOUD")

    def test_size_mismatch(self):
        r, _, _ = check([row("a.txt", 100, "aaa")],
                        [row("a.txt", 90, "aaa")])
        self.assertEqual(r[0][1], "SIZE MISMATCH")
        self.assertIn("local 100 byte(s), cloud 90 byte(s)", r[0][2])

    def test_hash_mismatch(self):
        r, _, _ = check([row("a.txt", 100, "aaa")],
                        [row("a.txt", 100, "bbb")])
        self.assertEqual(r[0][1], "HASH MISMATCH")

    def test_no_hash_on_either_side_is_in_sync(self):
        r, in_sync, _ = check([row("a.txt", 100)],
                              [row("a.txt", 100)])
        self.assertEqual((r, in_sync), ([], 1))

    def test_missing_comes_first(self):
        r, _, _ = check([row("a.txt", 100), row("b.txt", 50)],
                        [row("b.txt", 60), row("c.txt", 10)])
        self.assertEqual(r[0][0], "a.txt")
        self.assertEqual(r[0][1], "MISSING IN CLOUD")

    def test_invalid_row_is_skipped(self):
        # The local row is invalid and skipped, so the cloud copy of
        # the same path is reported as EXTRA IN CLOUD.
        r, in_sync, skipped = check([row("a.txt", "big")],
                                    [row("a.txt", 100)])
        self.assertEqual((r, in_sync, skipped),
                         ([("a.txt", "EXTRA IN CLOUD", "not in local manifest")], 0, 1))

    def test_empty_input(self):
        self.assertEqual(check([], []), ([], 0, 0))
