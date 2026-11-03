"""Work generator: create cascade WUs for the least-sampled bins, some of them canaries.
Run from cron as the BOINC project user, under flock so only one instance runs.

Each WU is first committed to PostgreSQL as 'pending' (serial from a sequence, record files
written with exclusive create), then registered with BOINC and marked 'in_flight'. If
create_work fails the row is marked failed; if the process dies in between, the next run
marks stale 'pending' rows failed. So there is never a live BOINC WU without a record, a
reused serial, or an overwritten record, and no row stays pending forever.
"""
from __future__ import annotations

import hashlib
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import db, sampler  # noqa: E402
from server.settings import ROOT, TodoValue, load, require  # noqa: E402
from server.workunit import make_cascade_wu, render_params  # noqa: E402

_rng = random.SystemRandom()  # seeds must not be predictable from earlier WUs


def staged_name(path: Path, prefix: str) -> str:
    """Content-addressed physical name, so a changed sticky file never reuses an old name."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return f"{prefix}_{digest}{path.suffix}"


def stage(project_dir: Path, src: Path, physical_name: str) -> str:
    """Copy a file into BOINC's download hierarchy (bin/stage_file is idempotent for equal content)."""
    tmp = project_dir / "tmp_nah" / physical_name
    tmp.parent.mkdir(exist_ok=True)
    shutil.copyfile(src, tmp)
    subprocess.run(["bin/stage_file", "--copy", str(tmp)], cwd=project_dir, check=True)
    return physical_name


def shared_inputs(settings: dict, project_dir: Path, potential_id: str) -> list[str]:
    """Stage the files every WU of this potential shares; returns their physical names."""
    potential = require(settings, f"potentials.{potential_id}")
    files = [
        (ROOT / "client" / "in.cascade.lmp", "nah_in_cascade"),
        (ROOT / potential["mod_file"], f"nah_{potential_id}_mod"),
        (ROOT / potential["data_file"], f"nah_{potential_id}_dat"),
        (ROOT / require(settings, "electronic.es_default.stopping_file"), "nah_stopping"),
    ]
    for path, _ in files:
        if not path.is_file() or "TODO" in path.read_text(errors="ignore"):
            raise TodoValue(f"{path} is missing or still contains TODO")
    return [stage(project_dir, path, staged_name(path, prefix)) for path, prefix in files]


def create_work(settings: dict, project_dir: Path, wu: dict, params_name: str, shared: list[str]) -> None:
    """Register one WU with BOINC. Credit is fixed server-side (validator --credit_from_wu)."""
    b, tier = "boinc", wu["size_tier"]
    cmd = ["bin/create_work",
           "--appname", require(settings, f"{b}.app_name"),
           "--wu_name", wu["wu_id"],
           "--wu_template", require(settings, f"{b}.wu_template"),
           "--result_template", require(settings, f"{b}.result_template"),
           "--rsc_fpops_est", str(require(settings, f"{b}.{tier}.fpops_est")),
           "--rsc_fpops_bound", str(require(settings, f"{b}.{tier}.fpops_bound")),
           "--rsc_memory_bound", str(require(settings, f"{b}.{tier}.memory_bytes")),
           "--delay_bound", str(require(settings, f"{b}.{tier}.delay_bound_s")),
           "--size_class", str(require(settings, f"{b}.{tier}.size_class")),  # big WUs to fast computers
           "--min_quorum", str(require(settings, f"{b}.min_quorum")),
           "--target_nresults", str(require(settings, f"{b}.target_nresults")),
           "--credit", f"{wu['points']:.6f}",  # sets wu.canonical_credit, which --credit_from_wu grants (sched/validator.cpp)
           shared[0], params_name, *shared[1:]]
    subprocess.run(cmd, cwd=project_dir, check=True)


def save_record(settings: dict, wu: dict, params: str) -> Path:
    """Write the WU record and params; exclusive create, so an existing record is never overwritten."""
    wu_dir = Path(require(settings, "storage.science_dir")) / "wu"
    wu_dir.mkdir(parents=True, exist_ok=True)
    with open(wu_dir / f"{wu['wu_id']}.json", "x") as handle:
        json.dump(wu, handle, indent=1)
    params_path = wu_dir / f"{wu['wu_id']}.params.lmp"
    with open(params_path, "x") as handle:
        handle.write(params)
    return params_path


def bin_counts(cur) -> dict[tuple[float, float], int]:
    """Non-canary WUs per bin that are in flight or validated (failed ones are re-generated)."""
    cur.execute("""SELECT w.energy_ev, w.temperature_k, count(*) FROM workunits w
                   LEFT JOIN wu_results r ON r.wu_id = w.wu_name
                   WHERE w.wu_name NOT IN (SELECT wu_name FROM canaries)
                     AND (w.status IN ('pending', 'in_flight') OR r.validated)
                   GROUP BY 1, 2""")
    return {(e, t): n for e, t, n in cur.fetchall()}


def claim_canary(cur, energy: float, temperature: float, exclusion: float) -> tuple[int, dict] | None:
    """An unused reference run for this open bin, or None. Rows that a normal WU could not
    have produced (channeling direction, off-grid values) are skipped, never issued."""
    cur.execute("""SELECT pool_id, wu_record FROM canary_pool WHERE used_by_wu_name IS NULL
                     AND (wu_record->'pka'->>'energy_ev')::float8 = %s AND (wu_record->>'temperature_k')::float8 = %s
                   ORDER BY random() LIMIT 5 FOR UPDATE SKIP LOCKED""", (energy, temperature))
    for pool_id, record in cur.fetchall():
        direction = tuple(float(c) for c in record["pka"]["direction"])
        seed = int(record["random_seed"])
        if sampler.angle_to_low_index_deg(direction) >= exclusion and 1 <= seed <= 899_990_000:
            return pool_id, {"direction": direction, "seed": seed}
    return None


def create_one(settings: dict, project_dir: Path, shared: list[str], energy: float, temperature: float,
               canary_fraction: float, exclusion: float) -> None:
    """Commit one WU's row and record, then register it with BOINC."""
    with db.pg() as conn:
        with conn.cursor() as cur:
            canary = claim_canary(cur, energy, temperature, exclusion) if _rng.random() < canary_fraction else None
            params = canary[1] if canary else {"direction": sampler.sample_direction(_rng, exclusion),
                                               "seed": sampler.sample_seed(_rng)}
            cur.execute("SELECT nextval('wu_serial')")
            wu = make_cascade_wu(settings, serial=cur.fetchone()[0], energy_ev=float(energy),
                                 temperature_k=float(temperature), **params)
            params_path = save_record(settings, wu, render_params(settings, wu))
            cur.execute("INSERT INTO workunits (wu_name, energy_ev, temperature_k, points_base) VALUES (%s, %s, %s, %s)",
                        (wu["wu_id"], wu["pka"]["energy_ev"], wu["temperature_k"], wu["points"]))
            if canary:
                cur.execute("INSERT INTO canaries (wu_name, pool_id) VALUES (%s, %s)", (wu["wu_id"], canary[0]))
                cur.execute("UPDATE canary_pool SET used_by_wu_name = %s WHERE pool_id = %s", (wu["wu_id"], canary[0]))
        conn.commit()
        try:
            create_work(settings, project_dir, wu, stage(project_dir, params_path, f"{wu['wu_id']}_params"), shared)
        except (subprocess.CalledProcessError, OSError):
            with conn.cursor() as cur:
                cur.execute("UPDATE workunits SET status = 'failed' WHERE wu_name = %s", (wu["wu_id"],))
            conn.commit()
            raise
        with conn.cursor() as cur:
            cur.execute("UPDATE workunits SET status = 'in_flight' WHERE wu_name = %s", (wu["wu_id"],))
        conn.commit()


def generate(settings: dict) -> int:
    """Fill the in-flight queue. Returns the number of WUs created."""
    project_dir = Path(require(settings, "boinc.project_dir"))
    energies = require(settings, "campaign.energies_ev")
    temperatures = require(settings, "campaign.temperatures_k")
    target = require(settings, "campaign.target_per_bin")
    max_in_flight = require(settings, "campaign.max_in_flight")
    canary_fraction = require(settings, "campaign.canary_fraction")
    exclusion = require(settings, "simulation.channeling_exclusion_deg")
    shared = shared_inputs(settings, project_dir, require(settings, "campaign.potential_id"))
    with db.pg() as conn, conn.cursor() as cur:
        # A row still pending after 30 minutes belongs to a run that died before create_work finished.
        cur.execute("UPDATE workunits SET status = 'failed' WHERE status = 'pending' "
                    "AND created_at < now() - interval '30 minutes'")
        cur.execute("SELECT count(*) FROM workunits WHERE status IN ('pending', 'in_flight')")
        room = max_in_flight - cur.fetchone()[0]
    created = 0
    while created < room:
        with db.pg() as conn, conn.cursor() as cur:
            chosen = sampler.pick_bin(bin_counts(cur), energies, temperatures, target)
        if chosen is None:
            break
        create_one(settings, project_dir, shared, *chosen, canary_fraction, exclusion)
        created += 1
    return created


def main() -> int:
    try:
        print(f"created {generate(load())} work units")
    except TodoValue as error:
        print(f"work generator refuses to run: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
