"""Work generator: create cascade WUs for the least-sampled bins, plus canaries and
outlier confirmations. Run from cron (e.g. every 10 minutes) as the BOINC project user.

For each new WU it writes the server-side record and params.lmp to the science
directory, stages the input files, and calls BOINC's create_work.
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


def create_work(settings: dict, project_dir: Path, wu: dict, params_name: str,
                shared: list[str], priority: int = 0) -> None:
    """Register one WU with BOINC. Credit is fixed server-side (validator --credit_from_wu)."""
    b = "boinc"
    cmd = ["bin/create_work",
           "--appname", require(settings, f"{b}.app_name"),
           "--wu_name", wu["wu_id"],
           "--wu_template", require(settings, f"{b}.wu_template"),
           "--result_template", require(settings, f"{b}.result_template"),
           "--rsc_fpops_est", str(require(settings, f"{b}.fpops_est")),
           "--rsc_fpops_bound", str(require(settings, f"{b}.fpops_bound")),
           "--rsc_memory_bound", str(require(settings, f"{b}.memory_bytes")),
           "--delay_bound", str(require(settings, f"{b}.delay_bound_s")),
           "--min_quorum", str(require(settings, f"{b}.min_quorum")),
           "--target_nresults", str(require(settings, f"{b}.target_nresults")),
           "--priority", str(priority),
           "--additional_xml", f"<credit>{wu['points']:.6f}</credit>",
           shared[0], params_name, *shared[1:]]
    subprocess.run(cmd, cwd=project_dir, check=True)


def save_record(settings: dict, wu: dict, params: str) -> Path:
    """Keep the WU record and its params on the server; the validator compares against them."""
    wu_dir = Path(require(settings, "storage.science_dir")) / "wu"
    wu_dir.mkdir(parents=True, exist_ok=True)
    (wu_dir / f"{wu['wu_id']}.json").write_text(json.dumps(wu, indent=1))
    params_path = wu_dir / f"{wu['wu_id']}.params.lmp"
    params_path.write_text(params)
    return params_path


def bin_counts(cur, campaign_energies: list[float]) -> dict[tuple[float, float], int]:
    """WUs per bin that are in flight or validated (failed ones are re-generated)."""
    cur.execute("""SELECT w.energy_ev, w.temperature_k, count(*) FROM workunits w
                   LEFT JOIN wu_results r ON r.wu_id = w.wu_name
                   WHERE w.confirms_wu_name IS NULL AND w.wu_name NOT IN (SELECT wu_name FROM canaries)
                     AND (w.status = 'in_flight' OR r.validated)
                   GROUP BY 1, 2""")
    return {(e, t): n for e, t, n in cur.fetchall()}


def next_serial(cur) -> int:
    # shortcut: count-based serial assumes one generator instance at a time (cron with flock);
    # switch to a PostgreSQL sequence if generators ever run in parallel.
    cur.execute("SELECT count(*) FROM workunits")
    return cur.fetchone()[0] + 1


def issue(settings, project_dir, cur, wu, shared, *, confirms=None, priority=0) -> None:
    """Save, stage, register with BOINC, and record one WU."""
    params = render_params(settings, wu)
    params_path = save_record(settings, wu, params)
    params_name = stage(project_dir, params_path, f"{wu['wu_id']}_params")
    create_work(settings, project_dir, wu, params_name, shared, priority)
    cur.execute("INSERT INTO workunits (wu_name, energy_ev, temperature_k, points_base, confirms_wu_name) "
                "VALUES (%s, %s, %s, %s, %s)",
                (wu["wu_id"], wu["pka"]["energy_ev"], wu["temperature_k"], wu["points"], confirms))


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
    created = 0
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM workunits WHERE status = 'in_flight'")
        room = max_in_flight - cur.fetchone()[0]
        # Held outliers first: two confirmation runs each, at high priority (reliable hosts).
        cur.execute("""SELECT r.wu_id FROM wu_results r WHERE r.held AND
                       (SELECT count(*) FROM workunits c WHERE c.confirms_wu_name = r.wu_id) < 2""")
        for (held,) in cur.fetchall():
            record = json.loads((Path(require(settings, "storage.science_dir")) / "wu" / f"{held}.json").read_text())
            for _ in range(2):
                if room <= 0:
                    break
                wu = make_cascade_wu(settings, serial=next_serial(cur), energy_ev=record["pka"]["energy_ev"],
                                     temperature_k=record["temperature_k"],
                                     direction=sampler.sample_direction(_rng, exclusion), seed=sampler.sample_seed(_rng))
                issue(settings, project_dir, cur, wu, shared, confirms=held, priority=10)
                room, created = room - 1, created + 1
        while room > 0:
            if _rng.random() < canary_fraction and issue_canary(settings, project_dir, cur, shared):
                room, created = room - 1, created + 1
                continue
            chosen = sampler.pick_bin(bin_counts(cur, energies), energies, temperatures, target)
            if chosen is None:
                break
            wu = make_cascade_wu(settings, serial=next_serial(cur), energy_ev=chosen[0], temperature_k=chosen[1],
                                 direction=sampler.sample_direction(_rng, exclusion), seed=sampler.sample_seed(_rng))
            issue(settings, project_dir, cur, wu, shared)
            room, created = room - 1, created + 1
    return created


def issue_canary(settings, project_dir, cur, shared) -> bool:
    """Issue one unused reference run as a normal-looking WU. False if the pool is empty."""
    cur.execute("SELECT pool_id, wu_record FROM canary_pool WHERE used_by_wu_name IS NULL "
                "ORDER BY random() LIMIT 1 FOR UPDATE SKIP LOCKED")
    row = cur.fetchone()
    if row is None:
        return False
    pool_id, record = row
    wu = make_cascade_wu(settings, serial=next_serial(cur), energy_ev=record["pka"]["energy_ev"],
                         temperature_k=record["temperature_k"], direction=tuple(record["pka"]["direction"]),
                         seed=record["random_seed"])
    issue(settings, project_dir, cur, wu, shared)
    cur.execute("INSERT INTO canaries (wu_name, pool_id) VALUES (%s, %s)", (wu["wu_id"], pool_id))
    cur.execute("UPDATE canary_pool SET used_by_wu_name = %s WHERE pool_id = %s", (wu["wu_id"], pool_id))
    return True


def main() -> int:
    try:
        print(f"created {generate(load())} work units")
    except TodoValue as error:
        print(f"work generator refuses to run: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
