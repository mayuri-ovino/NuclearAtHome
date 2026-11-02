"""Shared plumbing for the BOINC script_validator entry points."""
from __future__ import annotations

import json
from pathlib import Path

from analysis.lammps_output import OUTPUT_FILES, build_cascade_record, params_digest
from server.settings import require
from server.workunit import parse_params


def files_by_name(paths: list[str]) -> dict[str, Path]:
    """Map uploaded files to output names, by the order in server/boinc/nah_cascade_out."""
    if len(paths) != len(OUTPUT_FILES):
        raise ValueError(f"expected {len(OUTPUT_FILES)} files, got {len(paths)}")
    return dict(zip(OUTPUT_FILES, map(Path, paths)))


def load_wu(settings: dict, wu_name: str) -> tuple[dict, str]:
    """The stored WU record and the sha256 of its stored params (canonical form)."""
    wu_dir = Path(require(settings, "storage.science_dir")) / "wu"
    wu = json.loads((wu_dir / f"{wu_name}.json").read_text())
    params = parse_params((wu_dir / f"{wu_name}.params.lmp").read_text())
    return wu, params_digest(params)


def record_for(settings: dict, paths: list[str], runtime_s: float) -> dict:
    return build_cascade_record(
        files_by_name(paths), app_version="1", elapsed_s=runtime_s,
        vacancy_cutoff=require(settings, "analysis.vacancy_cluster_cutoff_angstrom"),
        interstitial_cutoff=require(settings, "analysis.interstitial_cluster_cutoff_angstrom"))


def wu_name_for(boinc_wu_id: int) -> str:
    """Authoritative WU name from BOINC's database, so a result cannot claim another WU."""
    from server import db
    with db.boinc() as conn, conn.cursor() as cur:
        cur.execute("SELECT name FROM workunit WHERE id = %s", (boinc_wu_id,))
        return cur.fetchone()[0]


def bin_population(settings: dict, wu: dict) -> list[float]:
    """Frenkel counts of validated, non-held, non-canary results in this WU's bin."""
    from server import db
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("""SELECT c.n_vacancies FROM cascade_stats c JOIN wu_results r USING (wu_id)
                       WHERE r.validated AND NOT r.held AND r.material_family = %s AND r.potential_id = %s
                         AND r.pka_energy_ev = %s AND r.temperature_k = %s
                         AND r.wu_id NOT IN (SELECT wu_name FROM canaries)""",
                    (wu["material"]["family"], wu["material"]["potential_id"],
                     wu["pka"]["energy_ev"], wu["temperature_k"]))
        return [float(n) for (n,) in cur.fetchall()]
