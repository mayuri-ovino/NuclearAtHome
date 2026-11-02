import tempfile
import unittest
from pathlib import Path

from server.db import boinc_login


class TestBoincLogin(unittest.TestCase):
    def test_reads_login_from_boinc_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.xml"
            path.write_text("<boinc><config><db_host>mysql</db_host><db_user>root</db_user>"
                            "<db_passwd>example</db_passwd><db_name>nuclear</db_name></config></boinc>")
            self.assertEqual(boinc_login(path), {"host": "mysql", "user": "root", "password": "example", "database": "nuclear"})


if __name__ == "__main__":
    unittest.main()
