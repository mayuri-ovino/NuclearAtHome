"""Turn a cascade result's raw LAMMPS files into the record in result_schema.json.

Clients run no project code, so this is where a result is first given structure.
Every parser fails loudly (ValueError) on malformed input; the validator treats
that as an invalid result.
"""
from __future__ import annotations

import hashlib
import math
import zlib
from pathlib import Path
from typing import Iterator

import numpy as np

from server.workunit import parse_params

OUTPUT_FILES = ["log.lammps", "energy.txt", "history.txt", "snapshots.dump", "final.dump", "run.state"]
# Largest decompressed size accepted per file. Uploads are hostile input: a small gzip can
# expand enormously, so decompression stops at the cap instead of filling memory.
MAX_BYTES = {"log.lammps": 50_000_000, "energy.txt": 20_000_000, "history.txt": 5_000_000,
             "snapshots.dump": 150_000_000, "final.dump": 150_000_000, "run.state": 10_000}


def read_bytes(path: Path, limit: int) -> bytes:
    """File content, un-gzipped if needed (BOINC gzip_when_done), refusing more than limit bytes."""
    with open(path, "rb") as handle:
        data = handle.read(limit + 1)
    if data[:2] == b"\x1f\x8b":
        inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
        data = inflater.decompress(data, limit + 1)
        if not inflater.eof and len(data) <= limit:
            raise ValueError(f"{Path(path).name}: truncated or oversized gzip")
    if len(data) > limit:
        raise ValueError(f"{Path(path).name}: larger than {limit} bytes")
    return data


def read_text(path: Path, name: str) -> str:
    return read_bytes(path, MAX_BYTES[name]).decode("utf-8")


def _short(line: str) -> str:
    """A hostile line can be megabytes long; log only its start."""
    return repr(line[:200])


def _finite_floats(line: str, ncols: int) -> list[float]:
    parts = line.split()
    if len(parts) != ncols:
        raise ValueError(f"expected {ncols} columns, got {len(parts)}: {_short(line)}")
    values = [float(p) for p in parts]
    if not all(math.isfinite(v) for v in values):
        raise ValueError(f"non-finite value in {_short(line)}")
    return values


def read_rows(text: str, ncols: int) -> list[list[float]]:
    """Numeric rows keyed by column 0, rewound after restarts.

    After a restart LAMMPS re-runs from the checkpoint, so a key smaller than or equal to
    an earlier one means everything from that key on was recomputed: drop the old rows.
    """
    rows: list[list[float]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        row = _finite_floats(line, ncols)
        while rows and rows[-1][0] >= row[0]:
            rows.pop()
        rows.append(row)
    return rows


def echoed_params(log_text: str) -> dict[str, str]:
    """The params.lmp variables as echoed into log.lammps (once per start or restart).

    Raises ValueError if the copies differ: every restart must have read the same params.
    """
    blocks, current = [], None
    for line in log_text.splitlines() + [""]:
        if line.startswith("variable wu_name string"):
            current = [line]
        elif current is not None and line.startswith("variable "):
            current.append(line)
        elif current is not None:
            blocks.append(current)
            current = None
    if not blocks:
        raise ValueError("log.lammps has no echoed params")
    parsed = [parse_params("\n".join(block)) for block in blocks]
    if any(p != parsed[0] for p in parsed[1:]):
        raise ValueError("params differ between restarts")
    return parsed[0]


def pka_trace(log_text: str) -> tuple[list[float], list[float]]:
    """PKA position right after the kick and after the first check (last copy, if the fresh start
    was repeated after an early crash)."""
    found = {}
    for line in log_text.splitlines():
        if line.startswith(("PKA_START ", "PKA_FIRST ")):
            parts = line.split()
            found[parts[0]] = _finite_floats(" ".join(parts[1:]), 3)
    if set(found) != {"PKA_START", "PKA_FIRST"}:
        raise ValueError("log.lammps lacks the PKA trace")
    return found["PKA_START"], found["PKA_FIRST"]


def params_digest(params: dict[str, str]) -> str:
    """sha256 of params in canonical form (sorted name=value lines)."""
    canonical = "\n".join(f"{k}={params[k]}" for k in sorted(params))
    return hashlib.sha256(canonical.encode()).hexdigest()


def read_run_state(text: str) -> dict[str, str]:
    state = dict(line.split(maxsplit=1) for line in text.splitlines() if line.strip())
    missing = {"md_steps", "simulated_time_ps", "n_atoms", "checkpoints_written", "restarts", "stop_reason"} - set(state)
    if missing:
        raise ValueError(f"run.state lacks {sorted(missing)}")
    return state


def dump_frames(text: str, expected_atoms: int | None = None) -> Iterator[dict]:
    """Frames of a LAMMPS text dump: timestep, box bounds, column names, data array.

    With expected_atoms, a frame claiming any other count is rejected before it is parsed.
    """
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i] != "ITEM: TIMESTEP":
            raise ValueError(f"bad dump line {i}: {lines[i]!r}")
        step = int(lines[i + 1])
        n = int(lines[i + 3])
        if expected_atoms is not None and n != expected_atoms:
            raise ValueError(f"dump frame has {n} atoms, expected {expected_atoms}")
        bounds = np.array([[float(v) for v in lines[i + 5 + k].split()[:2]] for k in range(3)])
        columns = lines[i + 8].split()[2:]
        body = lines[i + 9:i + 9 + n]
        data = np.array([[float(v) for v in row.split()] for row in body]).reshape(n, len(columns))
        if not np.isfinite(data).all():
            raise ValueError(f"non-finite value in dump frame at step {step}")
        yield {"step": step, "bounds": bounds, "columns": columns, "data": data}
        i += 9 + n


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_cascade_record(files: dict[str, Path], *, wu: dict, a0: float, app_version: str, elapsed_s: float,
                         vacancy_cutoff: float, interstitial_cutoff: float) -> dict:
    """The result_schema.json record for one cascade result.

    files maps each name in OUTPUT_FILES to its uploaded path. wu and a0 are the server's
    stored WU record and lattice constant: geometry never comes from the upload. elapsed_s
    is BOINC's elapsed time (suspensions excluded; client-reported, so TPF and PPD estimates
    can be skewed by a host, never credit), and TPF = elapsed_s / 100.
    """
    from analysis.defects import clusters, final_defects

    missing = [name for name in OUTPUT_FILES if name not in files]
    if missing:
        raise ValueError(f"result lacks {missing}")
    log_text = read_text(files["log.lammps"], "log.lammps")
    params = echoed_params(log_text)
    pka_start, pka_first = pka_trace(log_text)
    state = read_run_state(read_text(files["run.state"], "run.state"))
    energy = read_rows(read_text(files["energy.txt"], "energy.txt"), 5)
    history = read_rows(read_text(files["history.txt"], "history.txt"), 4)
    expected = wu["box"]["n_atoms_expected"]
    final = next(dump_frames(read_text(files["final.dump"], "final.dump"), expected), None)
    if final is None:
        raise ValueError("final.dump is empty")
    vac, inter, box_length = final_defects(final, lattice=wu["box"]["lattice"], cells=wu["box"]["unit_cells"][0],
                                           a0=a0, max_defects=max(100, expected // 100))
    return {
        "schema_version": "0.1.0",
        "wu_id": params["wu_name"],
        "wu_type": "cascade",
        "app_version": app_version,
        "platform": "x86_64-linux",
        "run": {
            "md_steps_completed": int(state["md_steps"]),
            "simulated_time_ps": float(state["simulated_time_ps"]),
            "n_atoms": int(state["n_atoms"]),
            "checkpoints_written": int(state["checkpoints_written"]),
            "restarts": int(state["restarts"]),
            "stop_reason": state["stop_reason"].strip(),
            "tpf_samples_s": [elapsed_s / 100.0] if elapsed_s > 0 else [],
        },
        "energy_log": [{"step": int(r[0]), "time_ps": r[1], "total_energy_ev": r[2],
                        "thermostat_energy_ev": r[3], "electronic_loss_ev": r[4]} for r in energy],
        "cascade": {
            "n_vacancies": len(vac),
            "n_interstitials": len(inter),
            "defect_count_history": [[r[1], r[2]] for r in history],
            "max_boundary_ke_ev": max(r[3] for r in history),
            "pka_start": pka_start,
            "pka_first": pka_first,
            "cluster_sizes_vac": clusters(vac, vacancy_cutoff, box_length),
            "cluster_sizes_int": clusters(inter, interstitial_cutoff, box_length),
            "defect_file": "final.dump",
            "snapshot_files": ["snapshots.dump"],
            "final_config_file": "final.dump",
        },
        "integrity": {
            "output_sha256": {name: file_sha256(files[name]) for name in OUTPUT_FILES},
            "input_sha256": params_digest(params),
        },
        "_final_atom_count": int(final["data"].shape[0]),
    }
