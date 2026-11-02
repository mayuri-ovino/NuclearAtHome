import csv
import tempfile
import unittest
from pathlib import Path

from analysis.lammps_output import build_cascade_record, params_digest
from server.workunit import parse_params, render_params
from tests.fixtures.cascade import settings, wu, write_result
from validator.checks import load_ranges, run_checks, zscore
from validator.common import files_by_name

RANGE = {"material": "W", "energy_bin_kev_min": "0.5", "energy_bin_kev_max": "1.5", "temp_bin_k_min": "200",
         "temp_bin_k_max": "400", "frenkel_min": "0", "frenkel_max": "10", "source": "test fixture"}


class TestChecks(unittest.TestCase):
    def setUp(self):
        self.wu = wu()
        self.ctx = {"settings": settings(), "ranges": [RANGE],
                    "stored_params_sha256": params_digest(parse_params(render_params(settings(), self.wu))), "a0": 3.0}

    def record(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_result(Path(tmp), self.wu, **kwargs)
            return build_cascade_record(files_by_name(paths), wu=self.wu, a0=3.0, app_version="1", elapsed_s=100.0,
                                        vacancy_cutoff=2.9, interstitial_cutoff=2.9)

    def assert_fails(self, record, check_id, ctx=None):
        passed, failures = run_checks(record, self.wu, ctx or self.ctx)
        self.assertFalse(passed)
        self.assertTrue(any(f.startswith(check_id) for f in failures), failures)

    def test_good_result_passes(self):
        passed, failures = run_checks(self.record(), self.wu, self.ctx)
        self.assertTrue(passed, failures)

    def test_other_wu_rejected(self):
        other = wu(serial=2)
        passed, failures = run_checks(self.record(), other, self.ctx)
        self.assertTrue(any(f.startswith("V1") for f in failures), failures)

    def test_replayed_result_rejected(self):
        self.assert_fails(self.record(), "V2", dict(self.ctx, duplicate_of="WA-0001-00000009"))

    def test_pka_must_move_along_this_wus_direction(self):
        record = self.record()
        start = record["cascade"]["pka_start"]
        record["cascade"]["pka_first"] = [start[0] - 0.4, start[1], start[2]]
        self.assert_fails(record, "V2")

    def test_pka_must_start_on_the_centre_site(self):
        record = self.record()
        record["cascade"]["pka_start"] = [0.0, 0.0, 0.0]
        self.assert_fails(record, "V2")

    def test_params_mismatch(self):
        ctx = dict(self.ctx, stored_params_sha256="0" * 64)
        self.assert_fails(self.record(), "V2", ctx)

    def test_energy_drift(self):
        self.assert_fails(self.record(drift_per_row=1.0), "V4")

    def test_unstable_history(self):
        record = self.record()
        record["cascade"]["defect_count_history"][-1][1] = 9
        self.assert_fails(record, "V5")

    def test_v5_accepts_what_the_template_accepts(self):
        # Reviewer's case: tol 1, counts drift within tol of the reference but 2 apart from each other.
        record = self.record()
        # reference count 2; later counts 3 and 1 are each within tol of it, though 2 apart from each other
        record["cascade"]["defect_count_history"] = [[0.1 * i, 2 if i < 50 else (3 if i % 2 else 1)] for i in range(101)]
        record["cascade"]["n_vacancies"] = record["cascade"]["n_interstitials"] = 1
        passed, failures = run_checks(record, self.wu, self.ctx)
        self.assertTrue(passed, failures)

    def test_hard_limit_run_must_reach_the_limit(self):
        record = self.record()
        record["run"]["stop_reason"] = "hard_limit"
        record["run"]["simulated_time_ps"] = 10.0
        self.assertTrue(run_checks(record, self.wu, self.ctx)[0])
        record["run"]["simulated_time_ps"] = 9.0
        self.assert_fails(record, "V5")

    def test_client_and_server_counts_must_agree(self):
        record = self.record()
        record["cascade"]["defect_count_history"][-1][1] = 5
        self.assert_fails(record, "V6")

    def test_frenkel_imbalance(self):
        record = self.record()
        record["cascade"]["n_interstitials"] += 1
        self.assert_fails(record, "V6")

    def test_no_range_for_bin(self):
        self.assert_fails(self.record(), "V7", dict(self.ctx, ranges=[]))

    def test_atom_count(self):
        record = self.record()
        record["run"]["n_atoms"] = 127
        self.assert_fails(record, "V8")

    def test_nan_rejected(self):
        record = self.record()
        record["energy_log"][3]["total_energy_ev"] = float("nan")
        self.assert_fails(record, "V1")

    def test_todo_threshold_fails_closed(self):
        s = settings()
        s["validator"]["energy_tolerance"] = "TODO-DECIDE"
        self.assert_fails(self.record(), "V4", dict(self.ctx, settings=s))

    def test_empty_energy_log_fails(self):
        record = self.record()
        record["energy_log"] = []
        self.assert_fails(record, "V1")


class TestCanaryVerdict(unittest.TestCase):
    def test_canary_mismatch_is_invalid(self):
        from validator.validate_init import judge
        t = TestChecks()
        t.setUp()
        record = t.record()  # 1 Frenkel pair
        self.assertEqual(judge(record, t.wu, t.ctx, None, 3.0), [])
        self.assertEqual(judge(record, t.wu, t.ctx, (1.5, 1.0), 3.0), [])
        self.assertEqual(judge(record, t.wu, t.ctx, (20.0, 2.0), 3.0), ["canary mismatch"])


class TestRangesAndPopulation(unittest.TestCase):
    def test_row_without_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "r.csv"
            with open(path, "w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(RANGE))
                writer.writeheader()
                writer.writerow(dict(RANGE, source=""))
            with self.assertRaises(ValueError):
                load_ranges(path)

    def test_repo_ranges_have_sources(self):
        self.assertEqual([r["frenkel_max"] for r in load_ranges()], ["47", "95"])

    def test_zscore(self):
        self.assertIsNone(zscore(5, [1, 2, 3], min_samples=5))
        self.assertAlmostEqual(zscore(4, [1, 2, 3, 2, 2], min_samples=5), 2 / (0.5 ** 0.5))


if __name__ == "__main__":
    unittest.main()
