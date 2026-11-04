import unittest
from pathlib import Path
from unittest import mock

from server import work_generator
from tests.fixtures.cascade import settings, wu


class TestCreateWork(unittest.TestCase):
    def command(self, tier):
        record = dict(wu(), size_tier=tier)
        with mock.patch.object(work_generator.subprocess, "run") as run:
            work_generator.create_work(settings(), Path("/project"), record, "params", ["template", "pot"])
        return run.call_args.args[0]

    def test_size_class_follows_the_tier(self):
        for tier, size_class in (("small", "0"), ("large", "1")):
            cmd = self.command(tier)
            self.assertEqual(cmd[cmd.index("--size_class") + 1], size_class)

    def test_credit_and_bounds_come_from_the_tier(self):
        cmd = self.command("large")
        self.assertEqual(float(cmd[cmd.index("--rsc_fpops_est") + 1]), 1e13)
        self.assertIn("--credit", cmd)


class TestClaimRetry(unittest.TestCase):
    class Cursor:
        def __init__(self, row):
            self.row, self.sql = row, []

        def execute(self, sql, args=None):
            self.sql.append((sql, args))

        def fetchone(self):
            return self.row

    def settings_with(self, science):
        s = settings()
        s["storage"]["science_dir"] = str(science)
        return s

    def test_failed_wu_retried_with_same_impact(self):
        import json
        import tempfile
        record = wu()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "wu").mkdir()
            (Path(tmp) / "wu" / f"{record['wu_id']}.json").write_text(json.dumps(record))
            cur = self.Cursor((record["wu_id"], 1))
            name, attempt, params = work_generator.claim_retry(cur, self.settings_with(tmp), "W_EAM_A", 1000.0, 300.0)
        self.assertEqual((name, attempt), (record["wu_id"], 1))
        self.assertEqual(params, {"direction": tuple(record["pka"]["direction"]), "seed": record["random_seed"]})
        self.assertTrue(any("SET retried = true" in sql for sql, _ in cur.sql))
        self.assertEqual(cur.sql[0][1][-1], 3)  # only attempts below max_attempts are retried

    def test_nothing_to_retry(self):
        self.assertIsNone(work_generator.claim_retry(self.Cursor(None), settings(), "W_EAM_A", 1000.0, 300.0))

    def test_missing_record_falls_back_to_a_new_draw(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cur = self.Cursor(("WA-0001-00000009", 2))
            self.assertIsNone(work_generator.claim_retry(cur, self.settings_with(tmp), "W_EAM_A", 1000.0, 300.0))
        self.assertTrue(any("SET retried = true" in sql for sql, _ in cur.sql))  # not tried again forever


if __name__ == "__main__":
    unittest.main()
