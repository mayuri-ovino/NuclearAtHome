import json
import lzma
import shutil
import tempfile
import unittest
from pathlib import Path

from analysis.lammps_output import build_cascade_record
from scripts.reanalyse_clusters import reanalyse
from server.workunit import render_params
from tests.fixtures.cascade import settings, wu, write_result
from validator.common import cluster_cutoffs, files_by_name


class TestReanalyse(unittest.TestCase):
    def test_stored_result_gives_the_validators_clusters(self):
        s, record = settings(), wu()
        with tempfile.TemporaryDirectory() as tmp:
            science = Path(tmp) / "science"
            (science / "wu").mkdir(parents=True)
            (science / "wu" / f"{record['wu_id']}.json").write_text(json.dumps(record))
            (science / "wu" / f"{record['wu_id']}.params.lmp").write_text(render_params(s, record))
            (Path(tmp) / "upload").mkdir()
            paths = write_result(Path(tmp) / "upload", record, frenkel=3)
            stored = science / "results" / record["wu_id"]
            stored.mkdir(parents=True)
            final = Path(paths[4])
            (stored / "up_4.xz").write_bytes(lzma.compress(final.read_bytes()))  # as the assimilator archives it
            vac_cut, int_cut = cluster_cutoffs(s, "bcc", 3.0)
            expected = build_cascade_record(files_by_name(paths), wu=record, a0=3.0, app_version="1", elapsed_s=1.0,
                                            vacancy_cutoff=vac_cut, interstitial_cutoff=int_cut)["cascade"]
            n_vac, n_int, vac, inter = reanalyse(s, science, record["wu_id"])
            shutil.rmtree(stored)
        self.assertEqual((n_vac, n_int), (expected["n_vacancies"], expected["n_interstitials"]))
        self.assertEqual((vac, inter), (expected["cluster_sizes_vac"], expected["cluster_sizes_int"]))


if __name__ == "__main__":
    unittest.main()
