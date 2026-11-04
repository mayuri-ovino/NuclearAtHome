import random
import unittest

from server.sampler import LOW_INDEX, angle_to_low_index_deg, campaign_bins, pick_bin, sample_direction, sample_seed


class TestSampler(unittest.TestCase):
    def test_low_index_family_sizes(self):
        self.assertEqual(len(LOW_INDEX), 6 + 12 + 8)

    def test_pick_least_sampled_bin(self):
        targets = campaign_bins(["A"], [1.0, 2.0], [300.0, 600.0], 3, [])
        counts = {("A", 1.0, 300.0): 2, ("A", 2.0, 300.0): 0, ("A", 1.0, 600.0): 1}
        self.assertEqual(pick_bin(counts, targets), ("A", 2.0, 300.0))

    def test_all_bins_full(self):
        self.assertIsNone(pick_bin({("A", 1.0, 300.0): 3}, campaign_bins(["A"], [1.0], [300.0], 3, [])))

    def test_every_potential_gets_every_scenario(self):
        targets = campaign_bins(["A", "B"], [1.0], [300.0, 600.0], 100, [])
        self.assertEqual(sorted(targets), [("A", 1.0, 300.0), ("A", 1.0, 600.0), ("B", 1.0, 300.0), ("B", 1.0, 600.0)])

    def test_tail_bin_filled_in_proportion(self):
        targets = campaign_bins(["A"], [1.0, 2.0], [300.0], 100,
                                [{"potential_id": "A", "energy_ev": 2.0, "temperature_k": 300.0, "target": 10000}])
        self.assertEqual(targets[("A", 2.0, 300.0)], 10000)
        # 50 of 100 is further along than 600 of 10,000: the tail bin is picked next
        self.assertEqual(pick_bin({("A", 1.0, 300.0): 50, ("A", 2.0, 300.0): 600}, targets), ("A", 2.0, 300.0))
        bad = [[{"potential_id": "B", "energy_ev": 1.0, "temperature_k": 300.0, "target": 500}],  # not a campaign bin
               [{"potential_id": "A", "energy_ev": 1.0, "temperature_k": 300.0, "target": 5}],    # lowers the target
               [{"potential_id": "A", "energy_ev": 1.0, "temperature_k": 300.0, "target": 500}] * 2]  # listed twice
        with self.assertRaises(ValueError):
            campaign_bins(["A"], [1.0], [300.0], 0, [])  # a zero target would divide by zero when picking
        for entries in bad:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                campaign_bins(["A"], [1.0], [300.0], 100, entries)

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
