"""Synthetic cascade results: the raw files LAMMPS would upload, with test settings.

Numbers are arbitrary test values (tests/fixtures/settings_test.toml), not physics.
"""
from __future__ import annotations

import gzip
from pathlib import Path

import numpy as np

from analysis.defects import lattice_sites
from analysis.lammps_output import OUTPUT_FILES
from server.settings import load
from server.workunit import make_cascade_wu, render_params

SETTINGS_PATH = Path(__file__).with_name("settings_test.toml")


def settings() -> dict:
    return load(SETTINGS_PATH)


def wu(serial: int = 1) -> dict:
    return make_cascade_wu(settings(), serial=serial, energy_ev=1000.0, temperature_k=300.0,
                           direction=(0.3, 0.5, 0.8), seed=42)


def dump_text(step: int, length: float, columns: list[str], rows: np.ndarray) -> str:
    head = [f"ITEM: TIMESTEP", str(step), "ITEM: NUMBER OF ATOMS", str(len(rows)),
            "ITEM: BOX BOUNDS pp pp pp", *[f"0 {length}"] * 3, "ITEM: ATOMS " + " ".join(columns)]
    return "\n".join(head + [" ".join(f"{v:.6g}" for v in row) for row in rows]) + "\n"


def write_result(directory: Path, record: dict, *, frenkel: int = 1, drift_per_row: float = 0.0,
                 restart: bool = False, gz: bool = False) -> list[str]:
    """Write the six output files for WU `record`; returns paths in output-template order."""
    s = settings()
    params = render_params(s, record)
    a0, cells = 3.0, record["box"]["unit_cells"][0]
    length = a0 * cells
    log = "LAMMPS (29 Aug 2024)\ninclude params.lmp\n" + params + "units metal\n"
    if restart:
        log += "include params.lmp\n" + params + "units metal\n"
    energy = [f"{100 * i} {0.1 * i:.1f} {-1000.0 + drift_per_row * i} 0.0 0.0" for i in range(101)]
    history = [f"{100 * i} {0.1 * i:.1f} {max(frenkel, 30 - i) if i < 50 else frenkel}" for i in range(101)]
    if restart:  # rows after the checkpoint at row 80 were written twice
        energy[81:81] = energy[80:90]
        history[81:81] = history[80:90]
    sites = lattice_sites("bcc", cells, a0)
    positions = sites.copy()
    for k in range(frenkel):  # move atom 2k onto the site of atom 2k+1: one vacancy, one interstitial
        positions[2 * k] = sites[2 * k + 1] + np.array([0.4, 0.0, 0.0])
    final = np.column_stack([np.arange(1, len(sites) + 1), np.ones(len(sites)), positions % length,
                             np.zeros((len(sites), 3))])
    snap = np.array([[1, 1, 1.0, 2.0, 3.0, 50.0, 0, 0.0, 0.0, 0.0]])
    contents = {
        "log.lammps": log,
        "energy.txt": "\n".join(energy) + "\n",
        "history.txt": "\n".join(history) + "\n",
        "snapshots.dump": dump_text(500, length, ["id", "type", "x", "y", "z", "c_ke", "c_ws[1]",
                                                  "f_ref[1]", "f_ref[2]", "f_ref[3]"], snap),
        "final.dump": dump_text(10000, length, ["id", "type", "x", "y", "z", "ix", "iy", "iz"], final),
        "run.state": f"md_steps 10000\nsimulated_time_ps 10.0\nn_atoms {len(sites)}\ncheckpoints_written 1\n"
                     f"restarts {int(restart)}\nstop_reason stabilized\n",
    }
    paths = []
    for i, name in enumerate(OUTPUT_FILES):
        path = Path(directory) / f"{record['wu_id']}_0_r1_{i}"
        data = contents[name].encode()
        path.write_bytes(gzip.compress(data) if gz else data)
        paths.append(str(path))
    return paths
