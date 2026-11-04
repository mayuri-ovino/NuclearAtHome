#!/usr/bin/env python3
"""Recompute defect clusters of stored, validated results with the current analysis settings.

Use after a change to the clustering rule (e.g. the 2026-11-02 cutoff fix). Reads each result's
stored final positions (gzip upload or .xz archive) and its WU record and params, then rewrites
cascade_stats.cluster_sizes_vac / cluster_sizes_int. Defect counts are unchanged by construction
(Wigner-Seitz does not depend on the cutoffs): both are checked, never rewritten. Run the stats
job afterwards (bin/nah_stats daily) to refresh science_aggregates.

    NAH_PG_DSN="host=127.0.0.1 port=5433 dbname=nuclear user=postgres" \
    NAH_SCIENCE_DIR=~/nah-staging/science python3 scripts/reanalyse_clusters.py [--dry-run]
"""
from __future__ import annotations

import gzip
import json
import lzma
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.defects import clusters, final_defects  # noqa: E402
from analysis.lammps_output import dump_frames  # noqa: E402
from server import db  # noqa: E402
from server.settings import load, require  # noqa: E402
from server.workunit import parse_params  # noqa: E402
from validator.common import cluster_cutoffs  # noqa: E402


def read_final(folder: Path) -> str:
    """The final positions file of a stored result (index 4 of the output files)."""
    xz = sorted(folder.glob("*_4.xz"))
    if xz:
        return lzma.open(xz[0], "rt").read()
    plain = sorted(folder.glob("*_4"))
    with open(plain[0], "rb") as handle:
        gzipped = handle.read(2) == b"\x1f\x8b"
    return (gzip.open if gzipped else open)(plain[0], "rt").read()


def reanalyse(settings: dict, science: Path, wu_id: str) -> tuple[int, int, list[int], list[int]]:
    """Vacancy and interstitial counts and cluster sizes of one stored result."""
    wu = json.loads((science / "wu" / f"{wu_id}.json").read_text())
    a0 = float(parse_params((science / "wu" / f"{wu_id}.params.lmp").read_text())["a0"])
    expected = wu["box"]["n_atoms_expected"]
    frame = next(dump_frames(read_final(science / "results" / wu_id), expected))
    lattice = wu["box"]["lattice"]
    vac, inter, box = final_defects(frame, lattice=lattice, cells=wu["box"]["unit_cells"][0], a0=a0,
                                    max_defects=max(100, expected // 100))
    vacancy_cutoff, interstitial_cutoff = cluster_cutoffs(settings, lattice, a0)
    return len(vac), len(inter), clusters(vac, vacancy_cutoff, box), clusters(inter, interstitial_cutoff, box)


def main(dry_run: bool) -> int:
    settings = load()
    science = Path(require(settings, "storage.science_dir"))
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("""SELECT r.wu_id, c.n_vacancies, c.n_interstitials, c.cluster_sizes_vac, c.cluster_sizes_int
                       FROM wu_results r JOIN cascade_stats c USING (wu_id) WHERE r.validated ORDER BY r.wu_id""")
        for wu_id, n_vac, n_int, old_vac, old_int in cur.fetchall():
            vac_count, int_count, new_vac, new_int = reanalyse(settings, science, wu_id)
            if (vac_count, int_count) != (n_vac, n_int):
                raise SystemExit(f"{wu_id}: defect counts {vac_count}/{int_count} != stored {n_vac}/{n_int}; nothing written")
            print(f"{wu_id}: vac {list(old_vac)} -> {new_vac}; int {list(old_int)} -> {new_int}")
            if not dry_run:
                cur.execute("UPDATE cascade_stats SET cluster_sizes_vac = %s, cluster_sizes_int = %s WHERE wu_id = %s",
                            (new_vac, new_int, wu_id))
        if not dry_run:
            conn.commit()
    return 0


if __name__ == "__main__":
    sys.exit(main("--dry-run" in sys.argv[1:]))
