"""Read-only JSON API (stats_spec.md), as a plain WSGI app.

Run under any WSGI server, e.g. `gunicorn 'stats.api:application'`, with
NAH_API_PG_DSN pointing at the nah_api role, which cannot read canary tables.
Never returns IP addresses, emails, or anything BOINC does not already show.
"""
from __future__ import annotations

import json
import os
import re
from typing import Callable
from urllib.parse import parse_qs

Query = Callable[[str, tuple], list[tuple]]


def _campaign() -> dict:
    """Public campaign facts from config/settings.toml (no secrets live there)."""
    from server.settings import load
    c = load()["campaign"]
    from server.sampler import campaign_bins
    targets = campaign_bins(c["potential_ids"], c["energies_ev"], c["temperatures_k"], c["target_per_bin"],
                            c.get("bin_targets", []))
    return {"id": c["id"], "material": c["material_family"], "potential_ids": c["potential_ids"],
            "energies_ev": c["energies_ev"], "temperatures_k": c["temperatures_k"],
            "target_per_bin": c["target_per_bin"],
            "bins": [{"potential_id": p, "pka_energy_ev": e, "temperature_k": t, "target": n}
                     for (p, e, t), n in targets.items()]}


CAMPAIGN = _campaign()


def _cores() -> dict:
    """Plan class -> public core ID, resource (CPU/GPU) and label, from config/settings.toml."""
    from server.settings import load
    return load().get("cores", {})


CORES = _cores()


def _boinc_url() -> str:
    from server.settings import load
    return load().get("web", {}).get("boinc_url", "")


BOINC_URL = _boinc_url()
WU_ID = r"[A-Z]{2}-[0-9]{4}-[0-9]{8}"


def _float_arg(qs: dict, name: str) -> float | None:
    value = qs.get(name, [None])[0]
    return None if value in (None, "") else float(value)


def host(query: Query, host_id: str, qs) -> dict | None:
    """Host stats, only if the owner lets BOINC show their computers. Times are rounded to the
    day, so the API does not reveal when a computer is switched on. A new computer is shown from
    its first contact (hardware, tasks); its points appear once results are validated."""
    hid = int(host_id)
    if not query("""SELECT 1 FROM privacy p JOIN hosts h ON h.user_id = p.user_id
                     WHERE h.host_id = %s AND p.show_hosts""", (hid,)):
        return None
    rows = query("""SELECT day, points, wus_valid, wus_invalid, est_ppd, actual_ppd_7d FROM host_daily
                    WHERE host_id = %s ORDER BY day DESC LIMIT 30""", (hid,))
    tpf = query("""SELECT date_trunc('day', recorded_at)::date, tpf_s FROM tpf_samples WHERE host_id = %s
                   ORDER BY recorded_at DESC LIMIT 100""", (hid,))
    latest = rows[0] if rows else (None,) * 6
    hardware = query("SELECT cpu_model, gpu, os_name, ncpus FROM hosts WHERE host_id = %s", (hid,))
    tasks = query("""SELECT h.wu_name, h.plan_class, h.status, h.sent_at::date, h.reported_at::date,
                            c.snapshot_file IS NOT NULL FROM host_results h
                     LEFT JOIN cascade_stats c ON c.wu_id = h.wu_name
                     WHERE h.host_id = %s ORDER BY h.sent_at DESC LIMIT 20""", (hid,))
    return {"host_id": hid, "est_ppd": latest[4], "actual_ppd_7d": latest[5],
            "wus_valid_30d": sum(r[2] or 0 for r in rows), "wus_invalid_30d": sum(r[3] or 0 for r in rows),
            "hardware": dict(zip(["cpu", "gpu", "os", "ncpus"], hardware[0])) if hardware else None,
            "recent_work": [{"wu_id": wu, "project": int(wu[3:7]), **_core(plan), "status": status,
                             "sent": str(sent) if sent else None, "returned": str(got) if got else None,
                             "has_3d": bool(has_3d)} for wu, plan, status, sent, got, has_3d in tasks],
            "tpf_history": [{"day": str(day), "tpf_s": t} for day, t in tpf]}


def _core(plan_class: str) -> dict:
    core = CORES.get(plan_class, {})
    return {"core": core.get("id", "?"), "resource": core.get("resource", "?")}


MIN_TEAM_MEMBERS = 2  # contributing users before a team total is shown (privacy.md)


def member(table: str) -> Callable:
    def handler(query: Query, ident: str, qs) -> dict | None:
        if table == "user_daily" and not query("SELECT 1 FROM privacy WHERE user_id = %s AND stats_export",
                                               (int(ident),)):
            return None  # the user has not consented to stats export
        if table == "team_daily" and query("SELECT count(DISTINCT user_id) FROM wu_results WHERE team_id = %s AND user_id <> 0",
                                           (int(ident),))[0][0] < MIN_TEAM_MEMBERS:
            return None  # a one-person team's total would show that person's points
        rows = query(f"SELECT day, points, ppd, rank FROM {table} WHERE id = %s ORDER BY day DESC LIMIT 1", (int(ident),))
        if not rows:
            return None
        day, points, ppd_value, rank = rows[0]
        result = {"id": int(ident), "day": str(day), "points": points, "ppd": ppd_value, "rank": rank}
        if table == "user_daily":
            result["badges"] = [b for (b,) in query("SELECT badge_id FROM badges WHERE user_id = %s", (int(ident),))]
        return result
    return handler


def summary(query: Query, _ident, qs) -> dict:
    (active,), = query("SELECT count(DISTINCT host_id) FROM wu_results WHERE reported_at > now() - interval '7 days'", ())
    (per_day,), = query("SELECT count(*) / 7.0 FROM wu_results WHERE reported_at > now() - interval '7 days'", ())
    (total_wus, total_points), = query("SELECT count(*), coalesce(sum(points_awarded), 0) FROM wu_results", ())
    bins = query("SELECT potential_id, pka_energy_ev, temperature_k, n FROM science_aggregates ORDER BY 1, 2, 3", ())
    return {"active_hosts_7d": active, "wus_per_day": float(per_day), "total_wus": total_wus,
            "total_points": float(total_points), "campaign": CAMPAIGN, "boinc_url": BOINC_URL,
            "campaign_progress": [{"potential_id": p, "pka_energy_ev": e, "temperature_k": t, "n": n}
                                  for p, e, t, n in bins]}


def recent(query: Query, _ident, qs) -> dict:
    """The latest validated cascades (no host or user: those follow the privacy rules)."""
    rows = query("""SELECT r.wu_id, r.pka_energy_ev, r.temperature_k, c.n_vacancies, r.points_awarded,
                           r.reported_at::date, c.snapshot_file IS NOT NULL
                    FROM wu_results r JOIN cascade_stats c USING (wu_id)
                    ORDER BY r.reported_at DESC LIMIT 50""", ())
    keys = ["wu_id", "pka_energy_ev", "temperature_k", "frenkel_pairs", "points", "day", "has_3d"]
    return {"workunits": [dict(zip(keys, row)) for row in rows]}


def cascades(query: Query, _ident, qs) -> dict:
    """Defect statistics per bin; energy_bin and temp_bin are [min,max) pairs like '1000,5000'."""
    sql = """SELECT material_family, potential_id, pka_energy_ev, temperature_k, n, mean_frenkel, se_frenkel,
                    ci95_low, ci95_high, cluster_size_hist, tails FROM science_aggregates WHERE true"""
    args: list = []
    if "material" in qs:
        sql += " AND material_family = %s"
        args.append(qs["material"][0])
    for name, column in (("energy_bin", "pka_energy_ev"), ("temp_bin", "temperature_k")):
        if name in qs:
            low, high = (float(v) for v in qs[name][0].split(","))
            sql += f" AND {column} >= %s AND {column} < %s"
            args += [low, high]
    keys = ["material", "potential_id", "pka_energy_ev", "temperature_k", "n", "mean_frenkel", "se_frenkel",
            "ci95_low", "ci95_high", "cluster_size_hist", "tails"]
    return {"bins": [dict(zip(keys, row)) for row in query(sql + " ORDER BY 1, 2, 3, 4", tuple(args))]}


def snapshots(query: Query, wu_id: str, qs) -> dict | None:
    """Snapshot URLs plus the facts the viewer's info panel shows."""
    rows = query("""SELECT c.snapshot_file, r.material_family, r.pka_energy_ev, r.temperature_k, r.points_awarded,
                           c.n_vacancies FROM cascade_stats c JOIN wu_results r USING (wu_id) WHERE wu_id = %s""", (wu_id,))
    if not rows or not rows[0][0]:
        return None
    _, material, energy, temperature, points, frenkel = rows[0]
    return {"wu_id": wu_id, "files": [f"/api/v1/cascades/{wu_id}/snapshots/0"], "material": material,
            "pka_energy_ev": energy, "temperature_k": temperature, "points": points, "frenkel_pairs": frenkel}


ROUTES = [
    (re.compile(r"^/api/v1/hosts/([0-9]{1,18})$"), host),
    (re.compile(r"^/api/v1/users/([0-9]{1,18})$"), member("user_daily")),
    (re.compile(r"^/api/v1/teams/([0-9]{1,18})$"), member("team_daily")),
    (re.compile(r"^/api/v1/project/summary$()"), summary),
    (re.compile(r"^/api/v1/science/cascades$()"), cascades),
    (re.compile(r"^/api/v1/workunits/recent$()"), recent),
    (re.compile(rf"^/api/v1/cascades/({WU_ID})/snapshots$"), snapshots),
]
SNAPSHOT_FILE = re.compile(rf"^/api/v1/cascades/({WU_ID})/snapshots/0$")
STORED_FILE = re.compile(rf"^{WU_ID}/[A-Za-z0-9_-][A-Za-z0-9_.-]*$")  # no "." or ".." names


def make_app(query: Query):
    """WSGI app over a query function (injected, so tests need no database).

    Snapshot files are handed to nginx with X-Accel-Redirect (internal location /_results/),
    so a large file is never read into a Python worker.
    """
    def respond(start, status: str, body: bytes, ctype: str = "application/json"):
        start(status, [("Content-Type", ctype), ("Content-Length", str(len(body))),
                       ("Cache-Control", "public, max-age=300"), ("X-Content-Type-Options", "nosniff")])
        return [body]

    def app(environ, start):
        if environ["REQUEST_METHOD"] != "GET":
            return respond(start, "405 Method Not Allowed", b'{"error": "read-only API"}')
        path = environ.get("PATH_INFO", "")
        qs = parse_qs(environ.get("QUERY_STRING", ""))
        match = SNAPSHOT_FILE.match(path)
        if match:
            rows = query("SELECT snapshot_file FROM cascade_stats WHERE wu_id = %s", (match.group(1),))
            if not rows or not rows[0][0] or not STORED_FILE.match(rows[0][0]):
                return respond(start, "404 Not Found", b'{"error": "not found"}')
            start("200 OK", [("Content-Type", "application/octet-stream"), ("X-Content-Type-Options", "nosniff"),
                             ("X-Accel-Redirect", f"/_results/{rows[0][0]}")])
            return [b""]
        for pattern, handler in ROUTES:
            match = pattern.match(path)
            if match:
                try:
                    body = handler(query, match.group(1), qs)
                except ValueError:
                    return respond(start, "400 Bad Request", b'{"error": "bad parameter"}')
                if body is None:
                    return respond(start, "404 Not Found", b'{"error": "not found"}')
                return respond(start, "200 OK", json.dumps(body, default=str).encode())
        return respond(start, "404 Not Found", b'{"error": "not found"}')

    return app


_conn = None


def _pg_query(sql: str, args: tuple) -> list[tuple]:
    """One read-only connection per worker process, reopened if it drops (no connection per query).
    The nah_api login role also has a CONNECTION LIMIT, and nginx rate-limits requests."""
    import psycopg  # dependency: psycopg[binary] (server only)
    global _conn
    for attempt in (1, 2):
        try:
            if _conn is None or _conn.closed:
                _conn = psycopg.connect(os.environ["NAH_API_PG_DSN"], autocommit=True)
            with _conn.cursor() as cur:
                cur.execute(sql, args)
                return cur.fetchall()
        except psycopg.OperationalError:
            _conn = None
            if attempt == 2:
                raise


def application(environ, start):
    """Production entry point for the WSGI server."""
    return make_app(_pg_query)(environ, start)
