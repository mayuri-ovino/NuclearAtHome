import unittest

from analysis.aggregate import summarize


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
