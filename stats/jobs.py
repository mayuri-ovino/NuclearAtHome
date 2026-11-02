"""Stats aggregation jobs (stats_spec.md). Run from cron:

    python3 -I stats/jobs.py hourly     # estimated PPD per host
    python3 -I stats/jobs.py daily      # host/user/team tables, ranks, badges, science aggregates

BOINC's own db_dump produces the standard XML stats export; nothing here duplicates it.
"""
from __future__ import annotations

import datetime as dt
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.aggregate import summarize  # noqa: E402
from server import db  # noqa: E402
from server.settings import TodoValue, load, require  # noqa: E402
from stats import ppd  # noqa: E402


# BOINC lib/common_defs.h (checked against BOINC master, 2026-11-02).
SERVER_IN_PROGRESS, SERVER_OVER = 4, 5
OUTCOME_SUCCESS, OUTCOME_CLIENT_ERROR, OUTCOME_NO_REPLY, OUTCOME_VALIDATE_ERROR = 1, 3, 4, 6
VALIDATE_VALID, VALIDATE_INVALID, VALIDATE_TOO_LATE = 1, 2, 5


def result_status(server_state: int, outcome: int, validate_state: int) -> str:
    """One word for a BOINC task's state, as volunteers see it."""
    if server_state == SERVER_IN_PROGRESS:
        return "running"
    if server_state != SERVER_OVER:
        return "queued"
    if outcome == OUTCOME_SUCCESS:
        return {VALIDATE_VALID: "valid", VALIDATE_INVALID: "invalid", VALIDATE_TOO_LATE: "too late"}.get(
            validate_state, "pending check")
    return {OUTCOME_CLIENT_ERROR: "error", OUTCOME_NO_REPLY: "timed out",
            OUTCOME_VALIDATE_ERROR: "invalid"}.get(outcome, "cancelled")


def gpus_from_serialnum(serialnum: str) -> str | None:
    """GPU names from BOINC's host.serialnum ("[BOINC|8.0][CUDA|NVIDIA GeForce ...|1|...][vbox|...]")."""
    names = [part.split("|")[1] for part in serialnum.strip("[]").split("][")
             if part.split("|")[0] in ("CUDA", "CAL", "INTEL", "opencl_nvidia", "opencl_ati") and "|" in part]
    return ", ".join(dict.fromkeys(names)) or None


def sync_boinc_hosts(cur) -> None:
    """Copy host hardware and the last 14 days of tasks from BOINC (no host names, no IPs)."""
    with db.boinc() as conn, conn.cursor() as bcur:
        bcur.execute("SELECT id, userid, p_model, os_name, p_ncpus, serialnum FROM host")
        hosts = bcur.fetchall()
        bcur.execute("""SELECT r.name, r.hostid, w.name, COALESCE(av.plan_class, ''), r.server_state, r.outcome,
                               r.validate_state, IF(r.sent_time > 0, FROM_UNIXTIME(r.sent_time), NULL),
                               IF(r.received_time > 0, FROM_UNIXTIME(r.received_time), NULL)
                        FROM result r JOIN workunit w ON w.id = r.workunitid
                        LEFT JOIN app_version av ON av.id = r.app_version_id
                        WHERE r.hostid > 0 AND r.sent_time > UNIX_TIMESTAMP(NOW() - INTERVAL 14 DAY)""")
        results = bcur.fetchall()
    cur.execute("TRUNCATE hosts, host_results")
    cur.executemany("INSERT INTO hosts VALUES (%s, %s, %s, %s, %s, %s)",
                    [(h, u, cpu, gpus_from_serialnum(serial or ""), os_name, n) for h, u, cpu, os_name, n, serial in hosts])
    cur.executemany("INSERT INTO host_results VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    [(name, host, wu, plan, result_status(state, outcome, valid), sent, got)
                     for name, host, wu, plan, state, outcome, valid, sent, got in results])


def host_est_ppd(tpf_samples: list[float], points_per_wu: list[float]) -> float | None:
    """Estimated PPD for one CPU slot: median recent TPF and mean recent points (no bonus, D2)."""
    if not tpf_samples or not points_per_wu:
        return None
    return ppd.estimated_ppd(statistics.fmean(points_per_wu), statistics.median(tpf_samples))


def milestones_reached(total_points: float, milestones: list[list]) -> list[str]:
    """Credit-milestone badge ids whose threshold total_points has reached."""
    return [badge for badge, threshold in milestones if total_points >= threshold]


def hourly(cur, today: dt.date) -> None:
    cur.execute("""SELECT t.host_id, array_agg(t.tpf_s), array_agg(r.points_base) FROM tpf_samples t
                   JOIN wu_results r USING (wu_id) WHERE t.recorded_at > now() - interval '7 days'
                   GROUP BY t.host_id""")
    for host, tpfs, points in cur.fetchall():
        est = host_est_ppd(tpfs, points)
        cur.execute("""INSERT INTO host_daily (host_id, day, est_ppd) VALUES (%s, %s, %s)
                       ON CONFLICT (host_id, day) DO UPDATE SET est_ppd = EXCLUDED.est_ppd""", (host, today, est))


def daily(cur, day: dt.date, settings: dict, invalid_by_host: dict[int, int]) -> None:
    """Credit tables for day (UTC), ranks by 7-day PPD, badges, science aggregates."""
    cur.execute("""INSERT INTO host_daily (host_id, day, points, wus_valid, actual_ppd_7d)
                   SELECT host_id, %(day)s,
                          sum(points_awarded) FILTER (WHERE reported_at::date = %(day)s),
                          count(*) FILTER (WHERE reported_at::date = %(day)s),
                          sum(points_awarded) / 7.0
                   FROM wu_results WHERE reported_at::date > %(day)s::date - 7 AND reported_at::date <= %(day)s
                   GROUP BY host_id
                   ON CONFLICT (host_id, day) DO UPDATE SET points = EXCLUDED.points,
                     wus_valid = EXCLUDED.wus_valid, actual_ppd_7d = EXCLUDED.actual_ppd_7d""", {"day": day})
    for host, n in invalid_by_host.items():
        cur.execute("""INSERT INTO host_daily (host_id, day, wus_invalid) VALUES (%s, %s, %s)
                       ON CONFLICT (host_id, day) DO UPDATE SET wus_invalid = EXCLUDED.wus_invalid""", (host, day, n))
    for table, key, extra in (("user_daily", "user_id", ""), ("team_daily", "team_id", "AND team_id <> 0")):
        cur.execute(f"""INSERT INTO {table} (id, day, points, ppd, rank)
                        SELECT {key}, %(day)s, today, ppd, rank() OVER (ORDER BY ppd DESC) FROM (
                          SELECT {key}, sum(points_awarded) FILTER (WHERE reported_at::date = %(day)s) AS today,
                                 sum(points_awarded) / 7.0 AS ppd
                          FROM wu_results WHERE reported_at::date > %(day)s::date - 7 AND reported_at::date <= %(day)s
                            {extra}
                          GROUP BY {key}) s
                        ON CONFLICT (id, day) DO UPDATE SET points = EXCLUDED.points, ppd = EXCLUDED.ppd,
                          rank = EXCLUDED.rank""", {"day": day})
    award_badges(cur, settings)
    science_aggregates(cur, settings)


def award_badges(cur, settings: dict) -> None:
    """Credit milestones, Reliable and Veteran (credit_spec.md 4). Tritium Hunter waits for trapping (D1)."""
    try:
        milestones = require(settings, "badges.credit_milestones")
        last_n, min_rate = require(settings, "badges.reliable_last_n"), require(settings, "badges.reliable_min_rate")
        veteran_days = require(settings, "badges.veteran_days")
    except TodoValue as error:
        print(f"badges skipped: {error}", file=sys.stderr)
        return
    awards = []
    cur.execute("SELECT user_id, sum(points_awarded) FROM wu_results GROUP BY user_id")
    awards += [(user, badge) for user, total in cur.fetchall() for badge in milestones_reached(total, milestones)]
    # Reliable: of the user's last N judged results (valid or invalid), at least min_rate valid.
    cur.execute("""SELECT user_id, count(*), count(*) FILTER (WHERE status = 'valid') FROM (
                     SELECT h.user_id, r.status, row_number() OVER (PARTITION BY h.user_id ORDER BY r.reported_at DESC) AS k
                     FROM host_results r JOIN hosts h USING (host_id) WHERE r.status IN ('valid', 'invalid')) recent
                   WHERE k <= %s GROUP BY user_id""", (last_n,))
    awards += [(user, "reliable") for user, n, valid in cur.fetchall() if reliable(n, valid, last_n, min_rate)]
    cur.execute("SELECT user_id FROM wu_results WHERE validated GROUP BY user_id "
                "HAVING min(reported_at) <= now() - make_interval(days => %s)", (veteran_days,))
    awards += [(user, "veteran") for (user,) in cur.fetchall()]
    for user, badge in awards:
        cur.execute("INSERT INTO badges (user_id, badge_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user, badge))


def reliable(judged: int, valid: int, last_n: int, min_rate: float) -> bool:
    """A full window of last_n judged results with at least min_rate of them valid."""
    return judged >= last_n and valid >= min_rate * judged


def science_aggregates(cur, settings: dict) -> None:
    """Frenkel-pair statistics per bin, from validated non-canary results (outliers are physics, so they count)."""
    samples = require(settings, "analysis.bootstrap_samples")
    cur.execute("""SELECT r.material_family, r.potential_id, r.pka_energy_ev, r.temperature_k,
                          array_agg(c.n_vacancies), array_agg(array_to_string(c.cluster_sizes_vac, ','))
                   FROM wu_results r JOIN cascade_stats c USING (wu_id)
                   WHERE r.validated AND r.wu_id NOT IN (SELECT wu_name FROM canaries)
                   GROUP BY 1, 2, 3, 4""")
    for material, potential, energy, temperature, counts, cluster_lists in cur.fetchall():
        s = summarize(counts, samples)
        hist: dict[str, int] = {}
        for sizes in cluster_lists:
            for size in filter(None, sizes.split(",")):
                hist[size] = hist.get(size, 0) + 1
        ci = s["ci95"] or [None, None]
        cur.execute("""INSERT INTO science_aggregates VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb, now())
                       ON CONFLICT (material_family, potential_id, pka_energy_ev, temperature_k) DO UPDATE SET
                         n = EXCLUDED.n, mean_frenkel = EXCLUDED.mean_frenkel, se_frenkel = EXCLUDED.se_frenkel,
                         ci95_low = EXCLUDED.ci95_low, ci95_high = EXCLUDED.ci95_high,
                         cluster_size_hist = EXCLUDED.cluster_size_hist, updated_at = now()""",
                    (material, potential, energy, temperature, s["n"], s["mean"], s["se"], ci[0], ci[1],
                     json.dumps(hist)))


def sync_privacy(cur) -> None:
    """Copy BOINC privacy choices; anonymize rows of deleted accounts (science data stays)."""
    with db.boinc() as conn, conn.cursor() as bcur:
        bcur.execute("""SELECT u.id, u.show_hosts, COALESCE((SELECT c.consent_flag FROM consent c
                          JOIN consent_type t ON t.id = c.consent_type_id
                          WHERE c.userid = u.id AND t.shortname = 'STATSEXPORT'
                          ORDER BY c.consent_time DESC LIMIT 1), 0) FROM user u""")
        rows = bcur.fetchall()
    cur.execute("TRUNCATE privacy")
    cur.executemany("INSERT INTO privacy VALUES (%s, %s, %s)", [(u, bool(h), bool(c)) for u, h, c in rows])
    gone = "SELECT host_id FROM wu_results WHERE user_id <> 0 AND user_id NOT IN (SELECT user_id FROM privacy)"
    cur.execute(f"DELETE FROM tpf_samples WHERE host_id IN ({gone})")
    cur.execute(f"DELETE FROM host_daily WHERE host_id IN ({gone})")
    cur.execute("UPDATE wu_results SET user_id = 0, host_id = 0, team_id = 0 WHERE user_id <> 0 "
                "AND user_id NOT IN (SELECT user_id FROM privacy)")
    for table in ("user_daily", "badges"):
        key = "id" if table == "user_daily" else "user_id"
        cur.execute(f"DELETE FROM {table} WHERE {key} NOT IN (SELECT user_id FROM privacy)")


def invalid_counts(day: dt.date) -> dict[int, int]:
    """Invalid results per host on day, from BOINC (invalid results never reach PostgreSQL)."""
    with db.boinc() as conn, conn.cursor() as cur:
        cur.execute("""SELECT hostid, count(*) FROM result WHERE validate_state = 2
                       AND DATE(FROM_UNIXTIME(received_time)) = %s GROUP BY hostid""", (day,))
        return dict(cur.fetchall())


def main(argv: list[str]) -> int:
    today = dt.datetime.now(dt.timezone.utc).date()
    try:
        settings = load()
        with db.pg() as conn, conn.cursor() as cur:
            if argv[1:] == ["hourly"]:
                hourly(cur, today)
                sync_boinc_hosts(cur)
            elif argv[1:] == ["daily"]:
                yesterday = today - dt.timedelta(days=1)
                sync_privacy(cur)
                daily(cur, yesterday, settings, invalid_counts(yesterday))
            else:
                print(__doc__, file=sys.stderr)
                return 2
    except TodoValue as error:
        print(f"stats job refuses to run: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
