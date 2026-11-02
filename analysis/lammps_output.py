"""Turn a cascade result's raw LAMMPS files into the record in result_schema.json.

Clients run no project code, so this is where a result is first given structure.
Every parser fails loudly (ValueError) on malformed input; the validator treats
that as an invalid result.
"""
from __future__ import annotations

import gzip
import hashlib
import math
from pathlib import Path
from typing import Iterator

import numpy as np

from server.workunit import parse_params

OUTPUT_FILES = ["log.lammps", "energy.txt", "history.txt", "snapshots.dump", "final.dump", "run.state"]


def read_bytes(path: Path) -> bytes:
    """File content, transparently un-gzipped (BOINC gzips uploads with gzip_when_done)."""
    data = Path(path).read_bytes()
    return gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data


def read_text(path: Path) -> str:
    return read_bytes(path).decode("utf-8")


def _finite_floats(line: str, ncols: int) -> list[float]:
    parts = line.split()
    if len(parts) != ncols:
        raise ValueError(f"expected {ncols} columns, got {len(parts)}: {line!r}")
    values = [float(p) for p in parts]
    if not all(math.isfinite(v) for v in values):
        raise ValueError(f"non-finite value in {line!r}")
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


def dump_frames(text: str) -> Iterator[dict]:
    """Frames of a LAMMPS text dump: timestep, box bounds, column names, data array."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i] != "ITEM: TIMESTEP":
            raise ValueError(f"bad dump line {i}: {lines[i]!r}")
        step = int(lines[i + 1])
        n = int(lines[i + 3])
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


def build_cascade_record(files: dict[str, Path], *, app_version: str, elapsed_s: float,
                         vacancy_cutoff: float, interstitial_cutoff: float) -> dict:
    """The result_schema.json record for one cascade result.

    files maps each name in OUTPUT_FILES to its uploaded path. elapsed_s is BOINC's
    elapsed time for the result (suspensions excluded), so TPF = elapsed_s / 100.
    """
    from analysis.defects import clusters, final_defects

    missing = [name for name in OUTPUT_FILES if name not in files]
    if missing:
        raise ValueError(f"result lacks {missing}")
    params = echoed_params(read_text(files["log.lammps"]))
    state = read_run_state(read_text(files["run.state"]))
    energy = read_rows(read_text(files["energy.txt"]), 5)
    history = read_rows(read_text(files["history.txt"]), 3)
    final = next(dump_frames(read_text(files["final.dump"])))
    vac, inter, box_length = final_defects(final, lattice=params["lat"], cells=int(params["n"]), a0=float(params["a0"]))
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
