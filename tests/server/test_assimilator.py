import gzip
import lzma
import tempfile
import unittest
from pathlib import Path

from server.assimilator import SNAPSHOT_INDEX, archive_xz


class TestArchive(unittest.TestCase):
    def test_gzip_and_plain_uploads_archive_losslessly(self):
        data = b"ITEM: TIMESTEP\n43300\n" + b"1 1 0.0294 0.0238 0.0757 0 0 0\n" * 1000
        with tempfile.TemporaryDirectory() as tmp:
            for name, content in (("up.gz", gzip.compress(data)), ("up.txt", data)):
                source, target = Path(tmp) / name, Path(tmp) / (name + ".xz")
                source.write_bytes(content)
                archive_xz(source, target)
                self.assertEqual(lzma.decompress(target.read_bytes()), data)
                self.assertFalse(target.with_name(target.name + ".part").exists())

    def test_snapshots_stay_gzip_for_the_viewer(self):
        self.assertEqual(SNAPSHOT_INDEX, 3)


if __name__ == "__main__":
    unittest.main()
