"""Per-result validation checks V1-V8 (docs/interfaces/validator_spec.md).

Each check is a pure function (record, wu, ctx) -> (passed, reason). They fail
closed: missing data, malformed data, or a TODO threshold is a FAIL, never a pass.
record is the result_schema.json record built by analysis/lammps_output.py, wu the
server-side WU record, ctx holds settings, the plausible-range table and the
params stored when the WU was created.

V9-V10 (trapping) arrive with the trapping stage (post-alpha, D1).
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Callable

import jsonschema

from server.settings import ROOT, TodoValue, require

RESULT_SCHEMA = json.loads((ROOT / "docs" / "interfaces" / "result_schema.json").read_text())
RANGES_PATH = ROOT / "validator" / "plausible_ranges.csv"
Check = Callable[[dict, dict, dict], tuple[bool, str]]


def load_ranges(path: Path = RANGES_PATH) -> list[dict]:
    """Rows of plausible_ranges.csv. A row without a source is rejected, not skipped."""
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if not row.get("source", "").strip() or "TODO" in row["source"]:
            raise ValueError(f"plausible range row without a verified source: {row}")
    return rows


def _all_finite(value) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_all_finite(v) for v in value.values())
    if isinstance(value, list):
        return all(_all_finite(v) for v in value)
    return True


def v1_schema(record, wu, ctx):
    """Valid against result_schema.json, all numbers finite, and bound to this WU."""
    errors = sorted(jsonschema.Draft202012Validator(RESULT_SCHEMA).iter_errors(record), key=str)
    if errors:
        return False, f"schema: {errors[0].message}"
    if not _all_finite(record):
        return False, "non-finite number in result"
    if record["wu_id"] != wu["wu_id"] or record["wu_type"] != wu["wu_type"]:
        return False, "result belongs to a different WU or type"
    return True, "ok"


def v2_integrity(record, wu, ctx):
    """The result belongs to this WU and is not a copy of another result.

    Echoed params match the stored params; the PKA started on the box-centre site and first
    moved along this WU's direction; no stored result has the same final.dump or energy.txt
    (catches one honest result replayed for many WUs); every referenced file is hashed.
    Transfer integrity itself rests on BOINC's upload size limits and HTTPS.
    """
    if record["integrity"]["input_sha256"] != ctx["stored_params_sha256"]:
        return False, "params echoed in log.lammps differ from the WU's params"
    if ctx.get("duplicate_of"):
        return False, f"outputs identical to stored result {ctx['duplicate_of']}"
    cascade = record["cascade"]
    a0, cells = ctx["a0"], wu["box"]["unit_cells"][0]
    site = [(cells // 2) * a0] * 3
    if math.dist(cascade["pka_start"], site) > 0.25 * a0:
        return False, "PKA did not start on the WU's site"
    step = [f - s for f, s in zip(cascade["pka_first"], cascade["pka_start"])]
    length = math.sqrt(sum(c * c for c in step))
    cosine = sum(c * d for c, d in zip(step, wu["pka"]["direction"])) / length if length else -1.0
    if not cosine > 0.9:
        return False, f"PKA moved off the WU's direction (cos {cosine:.2f})"
    hashed = record["integrity"]["output_sha256"]
    referenced = [cascade.get("defect_file"), cascade.get("final_config_file"), *cascade.get("snapshot_files", [])]
    missing = [name for name in referenced if name not in hashed]
    return (False, f"unhashed output files {missing}") if missing else (True, "ok")


def v3_completeness(record, wu, ctx):
    """Enough MD steps, and the run ended by the stop condition."""
    min_steps = require(ctx["settings"], "validator.min_md_steps")
    run = record["run"]
    if run["md_steps_completed"] < min_steps:
        return False, f"only {run['md_steps_completed']} steps (< {min_steps})"
    if run["stop_reason"] not in ("stabilized", "hard_limit"):
        return False, f"unknown stop reason {run['stop_reason']!r}"
    return True, "ok"


def v4_energy(record, wu, ctx):
    """|E(t) + removed by thermostat + electronic loss - E(0)| / E_PKA within tolerance at every sample."""
    tolerance = require(ctx["settings"], "validator.energy_tolerance")
    log = record["energy_log"]
    if log[0]["step"] != 0:
        return False, "energy log does not start at step 0"
    e0 = log[0]["total_energy_ev"]
    pka = wu["pka"]["energy_ev"]
    for row in log:
        drift = abs(row["total_energy_ev"] + row["thermostat_energy_ev"] + row["electronic_loss_ev"] - e0) / pka
        if not drift <= tolerance:  # written so NaN fails
            return False, f"energy drift {drift:.3g} at step {row['step']} exceeds {tolerance}"
    return True, "ok"


def v5_stabilization(record, wu, ctx):
    """A run that hit the time limit must really have reached it (valid even if not stabilized:
    volunteers are not punished for physics they cannot control). An early stop must satisfy the
    template's rule, replayed: the reference count resets whenever a count differs from it by more
    than the tolerance; the run is stable once no reset happened for a whole window."""
    run = record["run"]
    if run["stop_reason"] == "hard_limit":
        max_time = require(ctx["settings"], "simulation.max_time_ps")
        reached = run["simulated_time_ps"] >= max_time * (1 - 1e-9)
        return (True, "ok") if reached else (False, "stopped before the time limit")
    window = require(ctx["settings"], "simulation.stop_window_ps")
    tolerance = require(ctx["settings"], "simulation.stop_tolerance_pairs")
    history = record["cascade"]["defect_count_history"]
    reference, since = 0, 0.0
    for time, count in history:
        if abs(count - reference) > tolerance:
            reference, since = count, time
    if history[-1][0] - since < window:
        return False, "Frenkel count not stable over the final window"
    return True, "ok"


def v6_frenkel_balance(record, wu, ctx):
    """Vacancies equal interstitials, and the client's own final count (LAMMPS Voronoi occupation)
    equals the server's Wigner-Seitz count: for a bcc lattice both are the same analysis."""
    c = record["cascade"]
    if c["n_vacancies"] != c["n_interstitials"]:
        return False, f"{c['n_vacancies']} vacancies vs {c['n_interstitials']} interstitials"
    client = c["defect_count_history"][-1][1]
    if client != c["n_vacancies"]:
        return False, f"client counted {client} Frenkel pairs, server {c['n_vacancies']}"
    return True, "ok"


def v7_plausible_range(record, wu, ctx):
    """Frenkel pairs inside the sourced range for (material, energy bin, temperature bin)."""
    energy_kev = wu["pka"]["energy_ev"] / 1000.0
    temperature = wu["temperature_k"]
    for row in ctx["ranges"]:
        if (row["material"] == wu["material"]["family"]
                and float(row["energy_bin_kev_min"]) <= energy_kev < float(row["energy_bin_kev_max"])
                and float(row["temp_bin_k_min"]) <= temperature < float(row["temp_bin_k_max"])):
            pairs = record["cascade"]["n_vacancies"]
            if float(row["frenkel_min"]) <= pairs <= float(row["frenkel_max"]):
                return True, "ok"
            return False, f"{pairs} Frenkel pairs outside [{row['frenkel_min']}, {row['frenkel_max']}]"
    return False, "no plausible range for this bin"


def v8_atom_count(record, wu, ctx):
    """Atom count equals the WU's expected count, in run.state and in final.dump."""
    expected = wu["box"]["n_atoms_expected"]
    seen = {record["run"]["n_atoms"], record.get("_final_atom_count")}
    return (True, "ok") if seen == {expected} else (False, f"atom counts {sorted(map(str, seen))} != {expected}")


CASCADE_CHECKS: list[tuple[str, Check]] = [
    ("V1", v1_schema), ("V2", v2_integrity), ("V3", v3_completeness), ("V4", v4_energy),
    ("V5", v5_stabilization), ("V6", v6_frenkel_balance), ("V7", v7_plausible_range), ("V8", v8_atom_count),
]


def run_checks(record: dict, wu: dict, ctx: dict) -> tuple[bool, list[str]]:
    """Run every check the WU's type needs (chosen from the WU, never from the result)."""
    if wu["wu_type"] != "cascade":
        return False, [f"no checks implemented for wu_type {wu['wu_type']!r}"]
    failures = []
    for check_id, check in CASCADE_CHECKS:
        try:
            passed, reason = check(record, wu, ctx)
        except TodoValue as error:
            passed, reason = False, f"threshold not decided: {error}"
        except (KeyError, IndexError, TypeError, ValueError) as error:
            passed, reason = False, f"malformed result: {error!r}"
        if not passed:
            failures.append(f"{check_id}: {reason}")
    return not failures, failures


def zscore(value: float, population: list[float], min_samples: int) -> float | None:
    """Distance from the population mean in standard deviations; None while the bin is too small."""
    if len(population) < min_samples:
        return None
    n = len(population)
    mean = sum(population) / n
    sd = math.sqrt(sum((p - mean) ** 2 for p in population) / (n - 1))
    if sd == 0:
        return 0.0 if value == mean else math.inf
    return abs(value - mean) / sd
