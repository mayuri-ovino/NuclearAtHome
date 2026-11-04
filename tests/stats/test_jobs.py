import unittest

from stats.jobs import gpus_from_serialnum, host_est_ppd, milestones_reached, reliable, result_status


class TestJobs(unittest.TestCase):
    def test_est_ppd_uses_median_tpf(self):
        self.assertAlmostEqual(host_est_ppd([180.0, 180.0, 9999.0], [1000.0, 1000.0]), 4800.0)
        self.assertIsNone(host_est_ppd([], [1000.0]))

    def test_result_status(self):
        self.assertEqual(result_status(4, 0, 0), "running")
        self.assertEqual(result_status(2, 0, 0), "queued")
        self.assertEqual(result_status(5, 1, 1), "valid")
        self.assertEqual(result_status(5, 1, 2), "invalid")
        self.assertEqual(result_status(5, 1, 0), "pending check")
        self.assertEqual(result_status(5, 3, 0), "error")
        self.assertEqual(result_status(5, 4, 0), "timed out")

    def test_gpus_from_serialnum(self):
        serial = "[BOINC|8.0.2][CUDA|NVIDIA GeForce RTX 4070 Laptop GPU|1|8188MB|58018|300][vbox|7.0.14|0|1]"
        self.assertEqual(gpus_from_serialnum(serial), "NVIDIA GeForce RTX 4070 Laptop GPU")
        self.assertIsNone(gpus_from_serialnum("[BOINC|8.0.2]"))

    def test_milestones(self):
        milestones = [["lithium", 100.0], ["beryllium", 1000.0]]
        self.assertEqual(milestones_reached(150.0, milestones), ["lithium"])
        self.assertEqual(milestones_reached(50.0, milestones), [])

    def test_reliable(self):
        self.assertTrue(reliable(50, 49, 50, 0.98))
        self.assertFalse(reliable(50, 48, 50, 0.98))
        self.assertFalse(reliable(10, 10, 50, 0.98))  # too few results to judge


class TestScienceAggregates(unittest.TestCase):
    def test_lists_reach_the_right_tail_statistics(self):
        import json
        from stats.jobs import science_aggregates
        from tests.fixtures.cascade import settings

        class Cursor:
            def __init__(self):
                self.inserts = []

            def execute(self, sql, args=None):
                if sql.lstrip().startswith("INSERT"):
                    self.inserts.append(args)

            def fetchall(self):  # 3 cascades: vacancy clusters small, interstitial clusters large
                return [("W", "W_EAM_A", 1000.0, 300.0, [2, 4, 6], ["1,1", "2,1,1", "3,2,1"], ["2", "5,1", "6"],
                         [False, False, True])]

        cur = Cursor()
        science_aggregates(cur, settings())
        (row,) = cur.inserts
        tails = json.loads(row[-1])
        self.assertEqual(json.loads(row[-2]), {"1": 5, "2": 2, "3": 1})  # vacancy histogram
        self.assertEqual(tails["boundary_hits"], 1)
        by_size = {r["size"]: r["count"] for r in tails["largest_interstitial_cluster_at_least"]}
        self.assertEqual(by_size, {2: 3, 5: 2})  # interstitial lists, not vacancy ones
        self.assertEqual({r["size"]: r["count"] for r in tails["largest_vacancy_cluster_at_least"]}, {2: 2, 5: 0})


if __name__ == "__main__":
    unittest.main()
