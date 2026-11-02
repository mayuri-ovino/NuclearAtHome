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
WU_ID = r"[A-Z]{2}-[0-9]{4}-[0-9]{8}"


def _float_arg(qs: dict, name: str) -> float | None:
    value = qs.get(name, [None])[0]
    return None if value in (None, "") else float(value)


def host(query: Query, host_id: str, qs) -> dict | None:
    """Host stats, only if the owner lets BOINC show their computers. Times are rounded to the
    day, so the API does not reveal when a computer is switched on."""
    hid = int(host_id)
    if not query("""SELECT 1 FROM privacy p JOIN wu_results r ON r.user_id = p.user_id
                     WHERE r.host_id = %s AND p.show_hosts LIMIT 1""", (hid,)):
        return None
    rows = query("""SELECT day, points, wus_valid, wus_invalid, est_ppd, actual_ppd_7d FROM host_daily
                    WHERE host_id = %s ORDER BY day DESC LIMIT 30""", (hid,))
    if not rows:
        return None
    tpf = query("""SELECT date_trunc('day', recorded_at)::date, tpf_s FROM tpf_samples WHERE host_id = %s
                   ORDER BY recorded_at DESC LIMIT 100""", (hid,))
    latest = rows[0]
    return {"host_id": hid, "est_ppd": latest[4], "actual_ppd_7d": latest[5],
            "wus_valid_30d": sum(r[2] or 0 for r in rows), "wus_invalid_30d": sum(r[3] or 0 for r in rows),
            "tpf_history": [{"day": str(day), "tpf_s": t} for day, t in tpf]}


def member(table: str) -> Callable:
    def handler(query: Query, ident: str, qs) -> dict | None:
        if table == "user_daily" and not query("SELECT 1 FROM privacy WHERE user_id = %s AND stats_export",
                                               (int(ident),)):
            return None  # the user has not consented to stats export
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
    bins = query("SELECT pka_energy_ev, temperature_k, n FROM science_aggregates ORDER BY 1, 2", ())
    return {"active_hosts_7d": active, "wus_per_day": float(per_day),
            "campaign_progress": [{"pka_energy_ev": e, "temperature_k": t, "n": n} for e, t, n in bins]}


def cascades(query: Query, _ident, qs) -> dict:
    """Defect statistics per bin; energy_bin and temp_bin are [min,max) pairs like '1000,5000'."""
    sql = """SELECT material_family, potential_id, pka_energy_ev, temperature_k, n, mean_frenkel, se_frenkel,
                    ci95_low, ci95_high, cluster_size_hist FROM science_aggregates WHERE true"""
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
            "ci95_low", "ci95_high", "cluster_size_hist"]
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
