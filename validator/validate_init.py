"""BOINC script_validator init script: is one result valid?

Configured as: --init_script "nah_validate_init result_id runtime files"
(script_validator runs ../bin/<name>; server/boinc/bin/nah_validate_init is that wrapper.)
Exit 0 = valid. Exit 1 = invalid: anything wrong with the upload (malformed, truncated,
oversized, failing a check, failed canary). An invalid result earns no credit and resets the
host's consecutive_valid count in BOINC (D3).
Exit 3 = our own infrastructure failed (settings, databases, stored WU files): not the
volunteer's fault. 3 is BOINC's VAL_RESULT_TRANSIENT_ERROR (sched/validate_util2.h), so the WU
is validated again after a delay; checked against BOINC master source, 2026-11-01.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.settings import load, require  # noqa: E402
from validator.checks import load_ranges, run_checks  # noqa: E402
from validator.common import limit_resources, load_wu, record_for, stored_digest, wu_name_for_result  # noqa: E402

VALID, INVALID, INFRASTRUCTURE = 0, 1, 3  # 3 = VAL_RESULT_TRANSIENT_ERROR


def canary_reference(wu_name: str) -> tuple[float, float] | None:
    """(mean, sd) of the reference runs if this WU is a canary, else None."""
    from server import db
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("""SELECT p.ref_mean_frenkel, p.ref_sd_frenkel FROM canaries c
                       JOIN canary_pool p USING (pool_id) WHERE c.wu_name = %s""", (wu_name,))
        return cur.fetchone()


def duplicate_of(record: dict) -> str | None:
    """A stored result with the same final.dump or energy.txt, if any."""
    from server import db
    hashes = record["integrity"]["output_sha256"]
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute("SELECT wu_id FROM cascade_stats WHERE final_sha256 = %s OR energy_sha256 = %s LIMIT 1",
                    (hashes["final.dump"], hashes["energy.txt"]))
        row = cur.fetchone()
    return row[0] if row else None


def judge(record: dict, wu: dict, ctx: dict, canary: tuple[float, float] | None, canary_sigma: float) -> list[str]:
    """Failures for one parsed result (empty list = valid). Pure, so it is unit-tested."""
    passed, failures = run_checks(record, wu, ctx)
    if passed and canary is not None:
        mean, sd = canary
        if abs(record["cascade"]["n_vacancies"] - mean) > canary_sigma * sd:
            failures.append("canary mismatch")
    return failures


def main(argv: list[str]) -> int:
    limit_resources()
    try:  # our side: anything failing here is not the volunteer's fault
        settings = load()
        wu_name = wu_name_for_result(int(argv[1]))
        wu, params = load_wu(settings, wu_name)
        ctx = {"settings": settings, "ranges": load_ranges(), "stored_params_sha256": stored_digest(params),
               "a0": float(params["a0"])}
        canary = canary_reference(wu_name)
        canary_sigma = require(settings, "validator.canary_sigma")
    except Exception as error:
        print(f"validator infrastructure error: {error!r}"[:500], file=sys.stderr)
        return INFRASTRUCTURE
    try:  # the upload: anything failing here makes the result invalid
        record = record_for(settings, argv[3:], float(argv[2]), wu, params)
    except (Exception, MemoryError) as error:
        record, failures = None, [f"unparseable result: {error!r}"[:500]]
    if record is not None:
        try:  # our side again
            ctx["duplicate_of"] = duplicate_of(record)
        except Exception as error:
            print(f"validator infrastructure error: {error!r}"[:500], file=sys.stderr)
            return INFRASTRUCTURE
        try:
            failures = judge(record, wu, ctx, canary, canary_sigma)
        except (Exception, MemoryError) as error:
            failures = [f"malformed result: {error!r}"[:500]]
    for failure in failures:
        print(failure, file=sys.stderr)
    return INVALID if failures else VALID


if __name__ == "__main__":
    sys.exit(main(sys.argv))
