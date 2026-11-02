"""BOINC script_assimilator script: store a WU's canonical result in the science database.

Configured as: --script "python3 -I /path/server/assimilator.py wu_id files"
BOINC calls it with "--error <code> wu_id" when a WU failed for good.
Idempotent (ON CONFLICT DO NOTHING), because BOINC re-runs a failed assimilation.

Canaries are stored like every other result, so nothing public tells them apart;
stats/jobs.py leaves them out of science aggregates using the server-only table.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import db  # noqa: E402
from server.settings import load, require  # noqa: E402
from validator.checks import zscore  # noqa: E402
from validator.common import bin_population, load_wu, record_for, wu_name_for  # noqa: E402


def canonical_result(boinc_wu_id: int) -> dict:
    """Host, user, team and timing of the WU's canonical result, from BOINC's database."""
    with db.boinc() as conn, conn.cursor() as cur:
        cur.execute("""SELECT r.hostid, r.userid, u.teamid, FROM_UNIXTIME(r.sent_time), FROM_UNIXTIME(r.received_time),
                              r.elapsed_time, r.granted_credit
                       FROM workunit w JOIN result r ON r.id = w.canonical_resultid JOIN user u ON u.id = r.userid
                       WHERE w.id = %s""", (boinc_wu_id,))
        host, user, team, sent, received, elapsed, credit = cur.fetchone()
    return {"host_id": host, "user_id": user, "team_id": team, "sent_at": sent, "reported_at": received,
            "elapsed_s": float(elapsed), "points_awarded": float(credit)}


def is_outlier(settings: dict, wu: dict, n_frenkel: int) -> bool:
    score = zscore(n_frenkel, bin_population(settings, wu), require(settings, "validator.min_bin_samples"))
    return score is not None and score > require(settings, "validator.outlier_sigma")


def assimilate(boinc_wu_id: int, paths: list[str]) -> None:
    settings = load()
    wu_name = wu_name_for(boinc_wu_id)
    wu, _ = load_wu(settings, wu_name)
    meta = canonical_result(boinc_wu_id)
    record = record_for(settings, paths, meta["elapsed_s"])
    cascade = record["cascade"]
    held = is_outlier(settings, wu, cascade["n_vacancies"])

    store = Path(require(settings, "storage.science_dir")) / "results" / wu_name
    store.mkdir(parents=True, exist_ok=True)
    for path in paths:
        shutil.copy2(path, store / Path(path).name)

    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO wu_results (wu_id, wu_type, campaign_id, host_id, user_id, team_id, material_family,
                         potential_id, temperature_k, pka_energy_ev, validated, held, points_base, points_awarded,
                         sent_at, reported_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true,%s,%s,%s,%s,%s) ON CONFLICT (wu_id) DO NOTHING""",
                    (wu_name, "cascade", wu["campaign_id"], meta["host_id"], meta["user_id"], meta["team_id"],
                     wu["material"]["family"], wu["material"]["potential_id"], wu["temperature_k"],
                     wu["pka"]["energy_ev"], held, wu["points"], meta["points_awarded"],
                     meta["sent_at"], meta["reported_at"]))
        cur.execute("""INSERT INTO cascade_stats (wu_id, n_vacancies, n_interstitials, cluster_sizes_vac,
                         cluster_sizes_int, snapshot_file) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (wu_id) DO NOTHING""",
                    (wu_name, cascade["n_vacancies"], cascade["n_interstitials"], cascade["cluster_sizes_vac"],
                     cascade["cluster_sizes_int"], str(store / Path(paths[3]).name)))
        for tpf in record["run"]["tpf_samples_s"]:
            cur.execute("INSERT INTO tpf_samples (host_id, wu_id, tpf_s, recorded_at) VALUES (%s,%s,%s,%s)",
                        (meta["host_id"], wu_name, tpf, meta["reported_at"]))
        cur.execute("UPDATE workunits SET status = 'done' WHERE wu_name = %s", (wu_name,))
        release_confirmed(cur, wu_name)


def release_confirmed(cur, wu_name: str) -> None:
    """A held outlier is released once both of its confirmation WUs have validated results."""
    cur.execute("SELECT confirms_wu_name FROM workunits WHERE wu_name = %s", (wu_name,))
    row = cur.fetchone()
    if row is None or row[0] is None:
        return
    cur.execute("""SELECT count(*) FROM workunits w JOIN wu_results r ON r.wu_id = w.wu_name
                   WHERE w.confirms_wu_name = %s AND r.validated""", (row[0],))
    if cur.fetchone()[0] >= 2:
        cur.execute("UPDATE wu_results SET held = false WHERE wu_id = %s", (row[0],))


def mark_failed(boinc_wu_id: int) -> None:
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("UPDATE workunits SET status = 'failed' WHERE wu_name = %s", (wu_name_for(boinc_wu_id),))


def main(argv: list[str]) -> int:
    try:
        if argv[1] == "--error":
            mark_failed(int(argv[3]))
        else:
            assimilate(int(argv[1]), argv[2:])
    except Exception as error:  # non-zero makes BOINC retry the assimilation later
        print(f"assimilator error: {error!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
