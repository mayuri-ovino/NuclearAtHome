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


if __name__ == "__main__":
    unittest.main()
