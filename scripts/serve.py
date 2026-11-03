#!/usr/bin/env python3
r"""Local web server for the Nuclear@Home site: static pages from viewer/ plus the read-only API.

Standard library only (no nginx needed locally). Production and the Raspberry Pi use nginx +
gunicorn instead (docs/deploy.md). Binds to 127.0.0.1, or NAH_WEB_HOST (e.g. this computer's
home-network address, so other PCs on the network can open it; never a public address).

    NAH_API_PG_DSN="dbname=nuclear" NAH_SCIENCE_DIR=~/nah-science python3 scripts/serve.py [port]

Live view of the tasks running on this computer: open /cascade.html?live=1. The BOINC slot folders
are found in the usual data folder (Windows: C:\ProgramData\BOINC; Linux: /var/lib/boinc-client,
readable with `sg boinc`); NAH_BOINC_DATA overrides it, NAH_LIVE_DIR serves one folder as slot 0.
Only snapshots.dump, progress.txt and history.txt are served from a slot. Needs no database.

Windows: install Python 3.11+ from python.org, then in this folder:  py scripts\serve.py
"""
import json
import mimetypes
import os
import re
import sys
from pathlib import Path
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.settings import load  # noqa: E402
from stats.api import application as api  # noqa: E402

VIEWER = ROOT / "viewer"
RESULTS = Path(load()["storage"]["science_dir"]) / "results"
HEADERS = [("X-Content-Type-Options", "nosniff"), ("Referrer-Policy", "no-referrer")]
LIVE_DIR = Path(os.environ["NAH_LIVE_DIR"]) if os.environ.get("NAH_LIVE_DIR") else None
LIVE_FILES = {"snapshots.dump", "progress.txt", "history.txt"}
BOINC_DATA = [Path(os.environ["NAH_BOINC_DATA"])] if os.environ.get("NAH_BOINC_DATA") else [
    Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "BOINC",  # Windows
    Path("/var/lib/boinc-client"), Path("/var/lib/boinc")]           # Linux (Debian/Ubuntu, others)


def live_slots() -> dict[str, Path]:
    """Slot number -> folder, for every BOINC slot running a Nuclear@Home cascade on this computer."""
    if LIVE_DIR:
        return {"0": LIVE_DIR}
    slots = {}
    for data in BOINC_DATA:
        try:
            for slot in (data / "slots").iterdir():
                if slot.name.isdigit() and (slot / "in.cascade.lmp").is_file():
                    slots[slot.name] = slot
        except OSError:  # missing, or not readable by this user
            continue
    return slots


def live_tasks() -> list[dict]:
    """The running cascades, most advanced first: slot, work unit name, fraction done."""
    tasks = []
    for name, slot in live_slots().items():
        try:
            params = (slot / "params.lmp").read_text()
            progress = float((slot / "progress.txt").read_text().strip() or 0)
        except (OSError, ValueError):
            params, progress = "", 0.0
        wu = re.search(r"variable wu_name string (\S+)", params)
        tasks.append({"slot": name, "wu": wu.group(1) if wu else "?", "progress": progress})
    return sorted(tasks, key=lambda task: -task["progress"])


def file_under(base: Path, rel: str) -> Path | None:
    """The file base/rel, or None if it is missing or outside base (no path traversal)."""
    target = (base / rel).resolve()
    return target if target.is_relative_to(base.resolve()) and target.is_file() else None


def app(environ, start):
    path = environ.get("PATH_INFO", "/")
    if path.startswith("/api/") and not os.environ.get("NAH_API_PG_DSN"):
        start("503 Service Unavailable", [("Content-Type", "application/json")] + HEADERS)
        return [b'{"error": "no science database on this computer (live view only)"}']
    if path.startswith("/api/"):
        captured = {}
        body = api(environ, lambda status, headers: captured.update(status=status, headers=headers))
        accel = dict(captured["headers"]).get("X-Accel-Redirect")
        if not accel:
            start(captured["status"], captured["headers"] + HEADERS)
            return body
        target = file_under(RESULTS, accel[len("/_results/"):])  # nginx's internal handoff, done here locally
    elif path.startswith("/_results/"):
        target = None  # internal only, like nginx's "internal" location
    elif path == "/live/tasks.json":
        data = json.dumps(live_tasks()).encode()
        start("200 OK", [("Content-Type", "application/json"), ("Cache-Control", "no-store")] + HEADERS)
        return [data]
    elif path.startswith("/live/"):  # /live/<slot>/<file>
        slot, _, name = path[len("/live/"):].partition("/")
        folder = live_slots().get(slot)
        target = file_under(folder, name) if folder and name in LIVE_FILES else None
    else:
        target = file_under(VIEWER, path.lstrip("/") or "index.html")
    if target is None:
        start("404 Not Found", [("Content-Type", "text/plain")] + HEADERS)
        return [b"not found"]
    ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    data = target.read_bytes()  # one read: a live file may grow while we serve it
    start("200 OK", [("Content-Type", ctype), ("Content-Length", str(len(data))), ("Cache-Control", "no-store")] + HEADERS)
    return [data]


class ThreadingServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


HOST = os.environ.get("NAH_WEB_HOST", "127.0.0.1")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    try:
        server = make_server(HOST, port, app, server_class=ThreadingServer)
    except OSError as error:
        sys.exit(f"Port {port} is busy ({error.strerror}). Stop the other server, or pick a port: "
                 f"python3 scripts/serve.py {port + 10}")
    print(f"Nuclear@Home on http://{HOST}:{port}/  (Ctrl+C to stop)")
    server.serve_forever()
