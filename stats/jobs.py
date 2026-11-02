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
    """Credit milestones. Other badges wait for their thresholds (TODO-DECIDE) and trapping (D1)."""
    try:
        milestones = require(settings, "badges.credit_milestones")
    except TodoValue as error:
        print(f"badges skipped: {error}", file=sys.stderr)
        return
    cur.execute("SELECT user_id, sum(points_awarded) FROM wu_results GROUP BY user_id")
    for user, total in cur.fetchall():
        for badge in milestones_reached(total, milestones):
            cur.execute("INSERT INTO badges (user_id, badge_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user, badge))


def science_aggregates(cur, settings: dict) -> None:
    """Frenkel-pair statistics per bin, from validated results that are not held and not canaries."""
    samples = require(settings, "analysis.bootstrap_samples")
    cur.execute("""SELECT r.material_family, r.potential_id, r.pka_energy_ev, r.temperature_k,
                          array_agg(c.n_vacancies), array_agg(array_to_string(c.cluster_sizes_vac, ','))
                   FROM wu_results r JOIN cascade_stats c USING (wu_id)
                   WHERE r.validated AND NOT r.held AND r.wu_id NOT IN (SELECT wu_name FROM canaries)
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
            elif argv[1:] == ["daily"]:
                yesterday = today - dt.timedelta(days=1)
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
