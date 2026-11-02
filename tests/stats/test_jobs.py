import unittest

from stats.jobs import host_est_ppd, milestones_reached


class TestJobs(unittest.TestCase):
    def test_est_ppd_uses_median_tpf(self):
        self.assertAlmostEqual(host_est_ppd([180.0, 180.0, 9999.0], [1000.0, 1000.0]), 4800.0)
        self.assertIsNone(host_est_ppd([], [1000.0]))

    def test_milestones(self):
        milestones = [["lithium", 100.0], ["beryllium", 1000.0]]
        self.assertEqual(milestones_reached(150.0, milestones), ["lithium"])
        self.assertEqual(milestones_reached(50.0, milestones), [])


if __name__ == "__main__":
    unittest.main()
