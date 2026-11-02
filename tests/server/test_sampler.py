import random
import unittest

from server.sampler import LOW_INDEX, angle_to_low_index_deg, pick_bin, sample_direction, sample_seed


class TestSampler(unittest.TestCase):
    def test_low_index_family_sizes(self):
        self.assertEqual(len(LOW_INDEX), 6 + 12 + 8)

    def test_pick_least_sampled_bin(self):
        counts = {(1.0, 300.0): 2, (2.0, 300.0): 0, (1.0, 600.0): 1}
        self.assertEqual(pick_bin(counts, [1.0, 2.0], [300.0, 600.0], target=3), (2.0, 300.0))

    def test_all_bins_full(self):
        self.assertIsNone(pick_bin({(1.0, 300.0): 3}, [1.0], [300.0], target=3))

    def test_directions_avoid_channels(self):
        rng = random.Random(1)
        for _ in range(200):
            d = sample_direction(rng, 10.0)
            self.assertGreaterEqual(angle_to_low_index_deg(d), 10.0)
            self.assertAlmostEqual(sum(c * c for c in d), 1.0)

    def test_seeds_stay_below_lammps_limit(self):
        rng = random.Random(3)
        self.assertTrue(all(1 <= sample_seed(rng) < 900_000_000 for _ in range(1000)))

    def test_channel_direction_has_zero_angle(self):
        self.assertAlmostEqual(angle_to_low_index_deg((0.0, 0.0, 1.0)), 0.0)


if __name__ == "__main__":
    unittest.main()
