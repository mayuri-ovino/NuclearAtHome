"""Read-only JSON API (stats_spec.md), as a plain WSGI app.

Run under any WSGI server, e.g. `gunicorn 'stats.api:application'`, with
NAH_API_PG_DSN pointing at the nah_api role, which cannot read canary tables.
Never returns IP addresses, emails, or anything BOINC does not already show.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs

Query = Callable[[str, tuple], list[tuple]]
WU_ID = r"[A-Z]{2}-[0-9]{4}-[0-9]{8}"


def _float_arg(qs: dict, name: str) -> float | None:
    value = qs.get(name, [None])[0]
    return None if value in (None, "") else float(value)


def host(query: Query, host_id: str, qs) -> dict | None:
    rows = query("""SELECT day, points, wus_valid, wus_invalid, est_ppd, actual_ppd_7d FROM host_daily
                    WHERE host_id = %s ORDER BY day DESC LIMIT 30""", (int(host_id),))
    if not rows:
        return None
    tpf = query("""SELECT recorded_at, tpf_s FROM tpf_samples WHERE host_id = %s
                   ORDER BY recorded_at DESC LIMIT 100""", (int(host_id),))
    latest = rows[0]
    return {"host_id": int(host_id), "est_ppd": latest[4], "actual_ppd_7d": latest[5],
            "wus_valid_30d": sum(r[2] or 0 for r in rows), "wus_invalid_30d": sum(r[3] or 0 for r in rows),
            "tpf_history": [{"at": str(at), "tpf_s": t} for at, t in tpf]}


def member(table: str) -> Callable:
    def handler(query: Query, ident: str, qs) -> dict | None:
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


def make_app(query: Query, read_file: Callable[[str], bytes] = lambda p: Path(p).read_bytes()):
    """WSGI app over a query function (injected, so tests need no database)."""
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
            if not rows or not rows[0][0]:
                return respond(start, "404 Not Found", b'{"error": "not found"}')
            return respond(start, "200 OK", read_file(rows[0][0]), "application/octet-stream")
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


def _pg_query(sql: str, args: tuple) -> list[tuple]:
    import psycopg  # dependency: psycopg[binary] >= 3.1 (server only)
    with psycopg.connect(os.environ["NAH_API_PG_DSN"]) as conn, conn.cursor() as cur:
        cur.execute(sql, args)
        return cur.fetchall()


def application(environ, start):
    """Production entry point for the WSGI server."""
    return make_app(_pg_query)(environ, start)
