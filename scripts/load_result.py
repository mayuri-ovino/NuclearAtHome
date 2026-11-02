#!/usr/bin/env python3
"""Load a finished local run (e.g. a calibration run) into the science database as a validated
result, so the website shows real data without a BOINC server.

The run directory must hold wu.json, params.lmp and the six LAMMPS output files. The result is
checked with the same validator first; it is stored only if it passes. Host/user default to 1.

    NAH_PG_DSN="dbname=nuclear" NAH_SCIENCE_DIR=~/nah-science python3 scripts/load_result.py RUN_DIR [host_id user_id]
"""
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.lammps_output import OUTPUT_FILES  # noqa: E402
from server import db  # noqa: E402
from server.assimilator import store_result  # noqa: E402
from server.settings import load, require  # noqa: E402
from server.workunit import parse_params  # noqa: E402
from stats.jobs import daily, hourly  # noqa: E402
from validator.checks import load_ranges  # noqa: E402
from validator.common import record_for, stored_digest  # noqa: E402
from validator.validate_init import judge  # noqa: E402


def elapsed_seconds(run: Path) -> float:
    """Wall time from /usr/bin/time -v output if present, else the newest-minus-oldest file times."""
    timing = run / "time.txt"
    if timing.exists():
        for line in timing.read_text().splitlines():
            if "Elapsed (wall clock)" in line:
                parts = [float(p) for p in line.rsplit(" ", 1)[1].split(":")]
                return sum(v * 60 ** i for i, v in enumerate(reversed(parts)))
    times = [p.stat().st_mtime for p in run.iterdir()]
    return max(times) - min(times)


def main(run: Path, host_id: int, user_id: int) -> int:
    settings = load()
    wu = json.loads((run / "wu.json").read_text())
    params = parse_params((run / "params.lmp").read_text())
    paths = [str(run / name) for name in OUTPUT_FILES]
    record = record_for(settings, paths, elapsed_seconds(run), wu, params)
    ctx = {"settings": settings, "ranges": load_ranges(), "stored_params_sha256": stored_digest(params),
           "a0": float(params["a0"])}
    failures = judge(record, wu, ctx, None, 0.0)
    if failures:
        print("not loaded, the result fails validation:", *failures, sep="\n  ", file=sys.stderr)
        return 1
    wu_dir = Path(require(settings, "storage.science_dir")) / "wu"
    wu_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(run / "wu.json", wu_dir / f"{wu['wu_id']}.json")
    shutil.copy(run / "params.lmp", wu_dir / f"{wu['wu_id']}.params.lmp")
    now = dt.datetime.now(dt.timezone.utc)
    meta = {"host_id": host_id, "user_id": user_id, "team_id": 0, "sent_at": now, "reported_at": now,
            "elapsed_s": elapsed_seconds(run), "points_awarded": wu["points"]}
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO workunits (wu_name, energy_ev, temperature_k, points_base, status) "
                    "VALUES (%s, %s, %s, %s, 'done') ON CONFLICT DO NOTHING",
                    (wu["wu_id"], wu["pka"]["energy_ev"], wu["temperature_k"], wu["points"]))
        cur.execute("INSERT INTO privacy VALUES (%s, true, true) ON CONFLICT DO NOTHING", (user_id,))
    store_result(settings, wu["wu_id"], wu, record, meta, paths)
    with db.pg() as conn, conn.cursor() as cur:  # refresh the stats tables the site reads
        hourly(cur, now.date())
        daily(cur, now.date(), settings, {})
    print(f"loaded {wu['wu_id']}: {record['cascade']['n_vacancies']} Frenkel pairs, {wu['points']:.0f} points")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(args[0]), int(args[1]) if len(args) > 1 else 1, int(args[2]) if len(args) > 2 else 1))
