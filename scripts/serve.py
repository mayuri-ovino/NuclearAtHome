#!/usr/bin/env python3
"""Local web server for the Nuclear@Home site: static pages from viewer/ plus the read-only API.

Standard library only (no nginx needed locally). Production and the Raspberry Pi use nginx +
gunicorn instead (docs/deploy.md). Binds to 127.0.0.1 only.

    NAH_API_PG_DSN="dbname=nuclear" NAH_SCIENCE_DIR=~/nah-science python3 scripts/serve.py [port]
"""
import mimetypes
import os
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


def file_under(base: Path, rel: str) -> Path | None:
    """The file base/rel, or None if it is missing or outside base (no path traversal)."""
    target = (base / rel).resolve()
    return target if target.is_relative_to(base.resolve()) and target.is_file() else None


def app(environ, start):
    path = environ.get("PATH_INFO", "/")
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
    else:
        target = file_under(VIEWER, path.lstrip("/") or "index.html")
    if target is None:
        start("404 Not Found", [("Content-Type", "text/plain")] + HEADERS)
        return [b"not found"]
    ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    start("200 OK", [("Content-Type", ctype), ("Content-Length", str(target.stat().st_size))] + HEADERS)
    return [target.read_bytes()]


class ThreadingServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Nuclear@Home on http://127.0.0.1:{port}/  (Ctrl+C to stop)")
    make_server("127.0.0.1", port, app, server_class=ThreadingServer).serve_forever()
