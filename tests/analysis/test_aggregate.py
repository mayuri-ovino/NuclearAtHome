import unittest

import numpy as np

from analysis.aggregate import clusters_per_cascade, exact_interval, percentile, summarize, tails


class TestAggregate(unittest.TestCase):
    def test_mean_se_ci(self):
        s = summarize([2.0, 4.0, 6.0, 8.0], bootstrap_samples=500)
        self.assertEqual(s["n"], 4)
        self.assertAlmostEqual(s["mean"], 5.0)
        self.assertAlmostEqual(s["se"], 2.5819888974716 / 2)
        self.assertLessEqual(s["ci95"][0], 5.0)
        self.assertGreaterEqual(s["ci95"][1], 5.0)

    def test_reproducible(self):
        self.assertEqual(summarize([1.0, 3.0, 9.0], 100), summarize([1.0, 3.0, 9.0], 100))

    def test_small_samples(self):
        self.assertEqual(summarize([], 10)["n"], 0)
        self.assertIsNone(summarize([3.0], 10)["se"])


if __name__ == "__main__":
    unittest.main()


class TestTails(unittest.TestCase):
    def test_exact_interval(self):
        low, high = exact_interval(0, 100)  # no event in 100: an honest upper bound, not zero
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 0.0362, places=4)

    def test_percentiles_need_enough_cascades_beyond(self):
        x = np.arange(1, 101)
        self.assertIsNone(percentile(x, 0.99, 10))  # only 1 of 100 above p99
        self.assertEqual(percentile(x, 0.9, 10)["value"], 90)  # exactly 10 above: shown (no 9.999... rounding)
        p50 = percentile(x, 0.5, 10)
        self.assertEqual(p50["value"], 50)
        self.assertLess(p50["ci95"][0], 50)
        self.assertGreater(p50["ci95"][1], 50)

    def test_rare_cluster_means_withhold_their_interval(self):
        lists = [[]] * 99 + [[12, 12, 12]]  # one cascade with three big clusters
        row = clusters_per_cascade(lists, 10, 200, min_cascades=10)
        self.assertAlmostEqual(row["mean"], 0.03)
        self.assertEqual(row["cascades_with_one"], 1)
        self.assertIsNone(row["ci95"])  # the bootstrap would claim [0, 0.09]: false certainty
        common = clusters_per_cascade([[12]] * 20 + [[]] * 80, 10, 200, min_cascades=10)
        self.assertLess(common["ci95"][0], 0.2)
        self.assertGreater(common["ci95"][1], 0.2)

    def test_tails_per_cascade_and_boundary_hits(self):
        int_clusters = [[1]] * 90 + [[12, 6]] * 9 + [[60, 12]]
        hits = [False] * 99 + [True]  # the biggest cascade reached the boundary
        out = tails(list(range(1, 101)), int_clusters, [[]] * 100, hits, [5, 10, 50], 10, 200)
        self.assertEqual(out["boundary_hits"], 1)
        self.assertEqual(out["frenkel"]["largest_of_n"], 100)
        self.assertEqual(out["frenkel"]["p90"]["boundary_hits_above"], 1)
        rows = out["largest_interstitial_cluster_at_least"]
        self.assertEqual([r["count"] for r in rows], [10, 10, 1])
        self.assertEqual([r["boundary_hits"] for r in rows], [1, 1, 1])
        per = out["interstitial_clusters_per_cascade_at_least"]
        self.assertAlmostEqual(per[0]["mean"], 0.2)  # 10 cascades x 2 clusters >= 5, over 100
        self.assertAlmostEqual(per[1]["mean"], 0.11)

    def test_empty_bin(self):
        self.assertEqual(tails([], [], [], [], [5], 10, 10), {"n": 0})
