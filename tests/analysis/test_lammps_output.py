import json
import tempfile
import unittest
from pathlib import Path

import jsonschema

from analysis.lammps_output import build_cascade_record, echoed_params, read_rows
from server.settings import ROOT
from tests.fixtures.cascade import wu, write_result
from validator.common import files_by_name

SCHEMA = json.loads((ROOT / "docs" / "interfaces" / "result_schema.json").read_text())


class TestParsing(unittest.TestCase):
    def test_rows_rewind_after_restart(self):
        rows = read_rows("0 1\n10 2\n20 3\n10 9\n20 8\n30 7\n", 2)
        self.assertEqual(rows, [[0, 1], [10, 9], [20, 8], [30, 7]])

    def test_rows_reject_nan_and_bad_width(self):
        for text in ("0 nan\n", "0 1 2\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                read_rows(text, 2)

    def test_params_must_match_across_restarts(self):
        block = "variable wu_name string WA-0001-00000001\nvariable n equal 4\n"
        self.assertEqual(echoed_params(block + "units metal\n" + block)["n"], "4")
        with self.assertRaises(ValueError):
            echoed_params(block + "units metal\n" + block.replace("4", "5"))
        with self.assertRaises(ValueError):
            echoed_params("no params here\n")


class TestRecord(unittest.TestCase):
    def build(self, **kwargs):
        record = wu()
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_result(Path(tmp), record, **kwargs)
            return build_cascade_record(files_by_name(paths), app_version="1", elapsed_s=3600.0,
                                        vacancy_cutoff=2.9, interstitial_cutoff=2.9)

    def test_record_is_schema_valid(self):
        result = self.build(frenkel=2)
        jsonschema.validate(result, SCHEMA)
        self.assertEqual(result["cascade"]["n_vacancies"], 2)
        self.assertEqual(result["cascade"]["n_interstitials"], 2)
        self.assertEqual(result["run"]["tpf_samples_s"], [36.0])
        self.assertEqual(result["energy_log"][0]["step"], 0)

    def test_gzipped_and_restarted_results(self):
        result = self.build(gz=True, restart=True)
        self.assertEqual(len(result["energy_log"]), 101)
        self.assertEqual(result["run"]["restarts"], 1)


if __name__ == "__main__":
    unittest.main()
