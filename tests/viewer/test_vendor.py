"""Vendored Three.js must match the hashes recorded when it was verified against npm."""
import hashlib
import unittest
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[2] / "viewer" / "vendor"


class TestVendor(unittest.TestCase):
    def test_vendored_files_match_recorded_hashes(self):
        for line in (VENDOR / "SHA256SUMS").read_text().splitlines():
            if line.startswith("#"):
                continue
            digest, name = line.split()
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((VENDOR / name).read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
