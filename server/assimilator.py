"""BOINC script_assimilator script: store a WU's canonical result in the science database.

Configured as: --script "nah_assimilate wu_name files" (wrapper in server/boinc/bin/).
BOINC calls it as "--error <code> <wu_name> <wu_id> <batch_id>" when a WU failed for good
(sched/script_assimilator.cpp).
Idempotent (ON CONFLICT DO NOTHING), because BOINC re-runs a failed assimilation.

Outliers (far from their bin) are kept and flagged: rare cascades are physics, and cheating
is handled by replication and canaries. Canaries are stored like every other result, so nothing public tells them apart;
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
from validator.common import bin_population, limit_resources, load_wu, record_for  # noqa: E402


def canonical_result(wu_name: str) -> dict:
    """Host, user, team and timing of the WU's canonical result, from BOINC's database."""
    with db.boinc() as conn, conn.cursor() as cur:
        cur.execute("""SELECT r.hostid, r.userid, u.teamid, FROM_UNIXTIME(r.sent_time), FROM_UNIXTIME(r.received_time),
                              r.elapsed_time, r.granted_credit
                       FROM workunit w JOIN result r ON r.id = w.canonical_resultid JOIN user u ON u.id = r.userid
                       WHERE w.name = %s""", (wu_name,))
        host, user, team, sent, received, elapsed, credit = cur.fetchone()
    return {"host_id": host, "user_id": user, "team_id": team, "sent_at": sent, "reported_at": received,
            "elapsed_s": float(elapsed), "points_awarded": float(credit)}


def is_outlier(settings: dict, wu: dict, n_frenkel: int) -> bool:
    score = zscore(n_frenkel, bin_population(settings, wu), require(settings, "validator.min_bin_samples"))
    return score is not None and score > require(settings, "validator.outlier_sigma")


def assimilate(wu_name: str, paths: list[str]) -> None:
    settings = load()
    wu, params = load_wu(settings, wu_name)
    meta = canonical_result(wu_name)
    store_result(settings, wu_name, wu, record_for(settings, paths, meta["elapsed_s"], wu, params), meta, paths)


def store_result(settings: dict, wu_name: str, wu: dict, record: dict, meta: dict, paths: list[str]) -> None:
    """Copy the result files to science storage and insert its rows (shared with scripts/load_result.py)."""
    cascade = record["cascade"]
    outlier = is_outlier(settings, wu, cascade["n_vacancies"])

    store = Path(require(settings, "storage.science_dir")) / "results" / wu_name
    store.mkdir(parents=True, exist_ok=True)
    for path in paths:
        shutil.copy2(path, store / Path(path).name)

    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO wu_results (wu_id, wu_type, campaign_id, host_id, user_id, team_id, material_family,
                         potential_id, temperature_k, pka_energy_ev, validated, outlier, points_base, points_awarded,
                         sent_at, reported_at)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true,%s,%s,%s,%s,%s) ON CONFLICT (wu_id) DO NOTHING""",
                    (wu_name, "cascade", wu["campaign_id"], meta["host_id"], meta["user_id"], meta["team_id"],
                     wu["material"]["family"], wu["material"]["potential_id"], wu["temperature_k"],
                     wu["pka"]["energy_ev"], outlier, wu["points"], meta["points_awarded"],
                     meta["sent_at"], meta["reported_at"]))
        hashes = record["integrity"]["output_sha256"]
        boundary_hit = cascade["max_boundary_ke_ev"] > require(settings, "validator.boundary_ke_flag_ev")
        cur.execute("""INSERT INTO cascade_stats (wu_id, n_vacancies, n_interstitials, final_sha256, energy_sha256,
                         boundary_hit, cluster_sizes_vac, cluster_sizes_int, snapshot_file)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (wu_id) DO NOTHING""",
                    (wu_name, cascade["n_vacancies"], cascade["n_interstitials"], hashes["final.dump"],
                     hashes["energy.txt"], boundary_hit, cascade["cluster_sizes_vac"],
                     cascade["cluster_sizes_int"], f"{wu_name}/{Path(paths[3]).name}"))  # relative to science_dir/results
        # Keep a 3D snapshot only for this computer's newest result (science files are always kept).
        cur.execute("""UPDATE cascade_stats c SET snapshot_file = NULL FROM wu_results r
                       WHERE r.wu_id = c.wu_id AND r.host_id = %s AND c.wu_id <> %s AND c.snapshot_file IS NOT NULL
                       RETURNING c.snapshot_file""", (meta["host_id"], wu_name))
        old_snapshots = [row[0] for row in cur.fetchall()]
        for tpf in record["run"]["tpf_samples_s"]:
            cur.execute("INSERT INTO tpf_samples (host_id, wu_id, tpf_s, recorded_at) VALUES (%s,%s,%s,%s)",
                        (meta["host_id"], wu_name, tpf, meta["reported_at"]))
        cur.execute("UPDATE workunits SET status = 'done' WHERE wu_name = %s", (wu_name,))
    results_dir = Path(require(settings, "storage.science_dir")) / "results"
    for rel in old_snapshots:  # after the commit, so a failed delete never loses the database update
        (results_dir / rel).unlink(missing_ok=True)


def mark_failed(wu_name: str) -> None:
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("UPDATE workunits SET status = 'failed' WHERE wu_name = %s", (wu_name,))


def main(argv: list[str]) -> int:
    limit_resources()
    try:
        if argv[1] == "--error":
            mark_failed(argv[3])
        else:
            assimilate(argv[1], argv[2:])
    except Exception as error:  # non-zero makes BOINC retry the assimilation later
        print(f"assimilator error: {error!r}"[:500], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
