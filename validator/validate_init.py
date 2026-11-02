"""BOINC script_validator init script: is one result valid?

Configured as: --init_script "python3 -I /path/validator/validate_init.py wu_id runtime files"
Exit 0 = valid, 1 = invalid. An invalid result earns no credit and resets the host's
consecutive_valid count in BOINC, which returns it to full replication (D3); a failed
canary is reported this way too. Exit 3 = infrastructure error (logged, not a verdict).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.settings import load, require  # noqa: E402
from validator.checks import load_ranges, run_checks  # noqa: E402
from validator.common import load_wu, record_for, wu_name_for  # noqa: E402


def canary_verdict(wu_name: str, n_frenkel: int, canary_sigma: float) -> tuple[bool, str] | None:
    """None for normal WUs; for canaries, whether the result matches the reference runs."""
    from server import db
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("""SELECT p.ref_mean_frenkel, p.ref_sd_frenkel FROM canaries c
                       JOIN canary_pool p USING (pool_id) WHERE c.wu_name = %s""", (wu_name,))
        row = cur.fetchone()
    if row is None:
        return None
    mean, sd = row
    ok = abs(n_frenkel - mean) <= canary_sigma * sd
    return ok, "ok" if ok else "canary mismatch"


def verdict(boinc_wu_id: int, runtime_s: float, paths: list[str]) -> tuple[bool, list[str]]:
    settings = load()
    wu_name = wu_name_for(boinc_wu_id)
    wu, stored_digest = load_wu(settings, wu_name)
    try:
        record = record_for(settings, paths, runtime_s)
    except ValueError as error:
        return False, [f"unparseable result: {error}"]
    ctx = {"settings": settings, "ranges": load_ranges(), "stored_params_sha256": stored_digest}
    passed, failures = run_checks(record, wu, ctx)
    if passed:
        canary = canary_verdict(wu_name, record["cascade"]["n_vacancies"], require(settings, "validator.canary_sigma"))
        if canary is not None and not canary[0]:
            return False, [canary[1]]
    return passed, failures


def main(argv: list[str]) -> int:
    try:
        passed, failures = verdict(int(argv[1]), float(argv[2]), argv[3:])
    except Exception as error:  # infrastructure problem: say so, never call it valid
        print(f"validator error: {error!r}", file=sys.stderr)
        return 3
    for failure in failures:
        print(failure, file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
