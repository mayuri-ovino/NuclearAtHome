"""Tests for the reference credit/PPD implementation (stats/ppd.py).

Constants used here are illustrative test values, not the project's real
calibration (those are TODO-DECIDE / TODO-CALIBRATE in credit_spec.md).
"""
import math
import unittest

from stats import ppd


class TestBasePoints(unittest.TestCase):
    def test_reference_wu_earns_reference_points(self):
        ref_work = ppd.work_done(250_000, 100_000, 1.0)
        self.assertAlmostEqual(
            ppd.base_points(250_000, 100_000, 1.0, ref_work, 1000.0), 1000.0)

    def test_points_scale_linearly_with_work(self):
        ref_work = ppd.work_done(250_000, 100_000, 1.0)
        double_atoms = ppd.base_points(500_000, 100_000, 1.0, ref_work, 1000.0)
        ml_potential = ppd.base_points(250_000, 100_000, 20.0, ref_work, 1000.0)
        self.assertAlmostEqual(double_atoms, 2000.0)
        self.assertAlmostEqual(ml_potential, 20_000.0)

    def test_invalid_inputs_raise(self):
        with self.assertRaises(ValueError):
            ppd.work_done(0, 100, 1.0)
        with self.assertRaises(ValueError):
            ppd.base_points(10, 10, 1.0, 0.0, 1000.0)


class TestBonus(unittest.TestCase):
    def test_unvalidated_gets_nothing(self):
        self.assertEqual(ppd.quick_return_multiplier(100, 1000, 0.75, 3.0, validated=False), 0.0)

    def test_untrusted_gets_no_bonus(self):
        self.assertEqual(ppd.quick_return_multiplier(100, 1000, 0.75, 3.0, trusted=False), 1.0)

    def test_bonus_is_capped(self):
        self.assertEqual(ppd.quick_return_multiplier(1, 1_000_000, 0.75, 3.0), 3.0)

    def test_slow_return_floors_at_one(self):
        self.assertEqual(ppd.quick_return_multiplier(10_000, 1000, 0.75, 3.0), 1.0)

    def test_formula_in_range(self):
        expected = math.sqrt(0.75 * 864_000 / 36_000)
        self.assertAlmostEqual(ppd.quick_return_multiplier(36_000, 864_000, 0.75, 10.0), expected)


class TestPPD(unittest.TestCase):
    def test_worked_example_from_spec(self):
        # 1,000-point WU, TPF = 180 s -> 4,800 PPD (credit_spec.md section 3)
        self.assertAlmostEqual(ppd.estimated_ppd(1000.0, 180.0), 4800.0)

    def test_faster_machine_earns_more(self):
        self.assertGreater(ppd.estimated_ppd(1000.0, 90.0), ppd.estimated_ppd(1000.0, 180.0))

    def test_ppd_with_bonus_at_least_base_ppd(self):
        with_bonus = ppd.estimated_ppd_with_bonus(1000.0, 180.0, 864_000, 0.75, 3.0)
        self.assertGreaterEqual(with_bonus, ppd.estimated_ppd(1000.0, 180.0))

    def test_machine_ppd_sums_slots(self):
        cpu_slots = [ppd.estimated_ppd(1000.0, 180.0)] * 8
        gpu = ppd.estimated_ppd(5000.0, 60.0)
        self.assertAlmostEqual(ppd.machine_ppd(cpu_slots + [gpu]), 8 * 4800.0 + 72_000.0)

    def test_actual_ppd(self):
        self.assertAlmostEqual(ppd.actual_ppd(70_000.0), 10_000.0)

    def test_zero_tpf_raises(self):
        with self.assertRaises(ValueError):
            ppd.estimated_ppd(1000.0, 0.0)


if __name__ == "__main__":
    unittest.main()
