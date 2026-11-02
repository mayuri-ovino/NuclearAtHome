"""Shared plumbing for the BOINC script_validator and script_assimilator entry points."""
from __future__ import annotations

import json
import resource
from pathlib import Path

from analysis.lammps_output import OUTPUT_FILES, build_cascade_record, params_digest
from server.settings import require
from server.workunit import parse_params

# Parsing one hostile upload must not take the server down: cap address space and CPU time.
MEMORY_LIMIT_BYTES = 4 * 1024 ** 3
CPU_LIMIT_S = 600


def limit_resources() -> None:
    """Called at the top of each script; exceeding either limit kills only this result's check."""
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT_S, CPU_LIMIT_S))


def files_by_name(paths: list[str]) -> dict[str, Path]:
    """Map uploaded files to output names, by the order in server/boinc/nah_cascade_out."""
    if len(paths) != len(OUTPUT_FILES):
        raise ValueError(f"expected {len(OUTPUT_FILES)} files, got {len(paths)}")
    return dict(zip(OUTPUT_FILES, map(Path, paths)))


def load_wu(settings: dict, wu_name: str) -> tuple[dict, dict[str, str]]:
    """The stored WU record and its stored params (the server's copy, never the upload's)."""
    wu_dir = Path(require(settings, "storage.science_dir")) / "wu"
    wu = json.loads((wu_dir / f"{wu_name}.json").read_text())
    return wu, parse_params((wu_dir / f"{wu_name}.params.lmp").read_text())


def stored_digest(params: dict[str, str]) -> str:
    return params_digest(params)


def record_for(settings: dict, paths: list[str], runtime_s: float, wu: dict, params: dict[str, str]) -> dict:
    """Parse one result's uploads into a result record. Raises on any malformed upload."""
    return build_cascade_record(
        files_by_name(paths), wu=wu, a0=float(params["a0"]), app_version="1", elapsed_s=runtime_s,
        vacancy_cutoff=require(settings, "analysis.vacancy_cluster_cutoff_angstrom"),
        interstitial_cutoff=require(settings, "analysis.interstitial_cluster_cutoff_angstrom"))


def wu_name_for_result(result_id: int) -> str:
    """Authoritative WU name from BOINC's database, so a result cannot claim another WU.
    (script_validator passes result_id, runtime and files; it has no wu_id macro.)"""
    from server import db
    with db.boinc() as conn, conn.cursor() as cur:
        cur.execute("SELECT w.name FROM result r JOIN workunit w ON w.id = r.workunitid WHERE r.id = %s", (result_id,))
        return cur.fetchone()[0]


def bin_population(settings: dict, wu: dict) -> list[float]:
    """Frenkel counts of validated, non-canary results in this WU's bin and campaign."""
    from server import db
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("""SELECT c.n_vacancies FROM cascade_stats c JOIN wu_results r USING (wu_id)
                       WHERE r.validated AND r.campaign_id = %s AND r.material_family = %s AND r.potential_id = %s
                         AND r.pka_energy_ev = %s AND r.temperature_k = %s
                         AND r.wu_id NOT IN (SELECT wu_name FROM canaries)""",
                    (wu["campaign_id"], wu["material"]["family"], wu["material"]["potential_id"],
                     wu["pka"]["energy_ev"], wu["temperature_k"]))
        return [float(n) for (n,) in cur.fetchall()]
