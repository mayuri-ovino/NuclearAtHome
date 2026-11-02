import math
import unittest

from server.settings import TodoValue, load
from server.workunit import make_cascade_wu, parse_params, planned_md_steps, render_params, unit_cells_for
from tests.fixtures.cascade import settings, wu


class TestWorkunit(unittest.TestCase):
    def test_cascade_wu_is_schema_valid_and_normalized(self):
        record = wu(7)
        self.assertEqual(record["wu_id"], "WA-0001-00000007")
        self.assertEqual(record["box"], {"unit_cells": [4, 4, 4], "lattice": "bcc", "n_atoms_expected": 128})
        self.assertAlmostEqual(math.dist(record["pka"]["direction"], (0, 0, 0)), 1.0)
        self.assertNotIn("is_canary", record)

    def test_points_from_planned_steps(self):
        s = settings()
        self.assertEqual(planned_md_steps(s), 1000 + 10000)
        self.assertAlmostEqual(wu()["points"], 1000.0 * 128 * 11000 * 1.0 / 1.0e9)

    def test_size_tier_from_atom_count(self):
        s = settings()
        self.assertEqual(wu()["size_tier"], "small")  # 4^3 cells, 128 atoms
        big = make_cascade_wu(s, serial=2, energy_ev=2000.0, temperature_k=300.0, direction=(0, 0, 1), seed=1)
        self.assertEqual(big["size_tier"], "large")  # 6^3 cells, 432 atoms

    def test_box_rule(self):
        s = settings()
        self.assertEqual(unit_cells_for(s, 1500.0), 4)
        self.assertEqual(unit_cells_for(s, 1501.0), 6)
        with self.assertRaises(ValueError):
            unit_cells_for(s, 9000.0)

    def test_params_round_trip(self):
        record = wu()
        params = parse_params(render_params(settings(), record))
        self.assertEqual(params["wu_name"], record["wu_id"])
        self.assertEqual(params["n"], "4")
        self.assertEqual(params["lat"], "bcc")
        self.assertEqual(float(params["max_time"]), 10.0)

    def test_undecided_settings_refuse(self):
        s = settings()
        s["simulation"]["dt_max_ps"] = "TODO-DECIDE"
        with self.assertRaises(TodoValue):
            make_cascade_wu(s, serial=1, energy_ev=1000.0, temperature_k=300.0, direction=(1, 0, 0), seed=1)

    def test_repo_settings_build_reference_wu_worth_1760_points(self):
        record = make_cascade_wu(load(), serial=1, energy_ev=5000.0, temperature_k=300.0, direction=(1, 2, 3), seed=7)
        self.assertEqual((record["size_tier"], record["box"]["n_atoms_expected"]), ("small", 250_000))
        self.assertAlmostEqual(record["points"], 1760.0)


if __name__ == "__main__":
    unittest.main()
