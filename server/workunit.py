"""Build cascade work units: the WU record (workunit_schema.json) and params.lmp.

The WU record stays on the server. Volunteers receive only params.lmp, which the
LAMMPS template (client/in.cascade.lmp) includes; LAMMPS echoes it into log.lammps,
and the validator checks that echo against the stored record.
"""
from __future__ import annotations

import json
import math

import jsonschema

from server.settings import ROOT, require

WU_SCHEMA = json.loads((ROOT / "docs" / "interfaces" / "workunit_schema.json").read_text())
ATOMS_PER_CELL = {"bcc": 2, "fcc": 4}
SCHEMA_VERSION = "0.1.0"


def wu_name(prefix: str, campaign_number: int, serial: int) -> str:
    """WU id in the schema's XX-NNNN-NNNNNNNN form."""
    return f"{prefix}-{campaign_number:04d}-{serial:08d}"


def unit_cells_for(settings: dict, energy_ev: float) -> int:
    """Cells per side from the box rule: the first rule whose energy limit covers the PKA."""
    for max_energy, cells in require(settings, "simulation.box_rule"):
        if energy_ev <= max_energy:
            return int(cells)
    raise ValueError(f"no box rule covers a {energy_ev} eV PKA")


def size_tier_for(settings: dict, n_atoms: int) -> str:
    """The first tier whose atom limit covers this box."""
    for max_atoms, tier in require(settings, "campaign.size_tiers"):
        if n_atoms <= max_atoms:
            return tier
    raise ValueError(f"no size tier covers {n_atoms} atoms")


def planned_md_steps(settings: dict) -> int:
    """Steps used for points: equilibration plus the hard time limit at the largest timestep.

    The adaptive timestep never exceeds dt_max, so this is a lower bound on the real count.
    """
    dt_max = require(settings, "simulation.dt_max_ps")
    equil = math.ceil(require(settings, "simulation.equilibration_ps") / dt_max)
    return equil + math.ceil(require(settings, "simulation.max_time_ps") / dt_max)


def make_cascade_wu(settings: dict, *, serial: int, energy_ev: float, temperature_k: float,
                    direction: tuple[float, float, float], seed: int) -> dict:
    """Return a schema-valid cascade WU record. Raises TodoValue if any needed setting is TODO."""
    from stats.ppd import base_points

    potential_id = require(settings, "campaign.potential_id")
    potential = require(settings, f"potentials.{potential_id}")
    cells = unit_cells_for(settings, energy_ev)
    n_atoms = ATOMS_PER_CELL[potential["lattice"]] * cells ** 3
    norm = math.sqrt(sum(c * c for c in direction))
    points = base_points(n_atoms, planned_md_steps(settings), potential["cost_factor"],
                         require(settings, "credit.ref_work"), require(settings, "credit.ref_points"))
    wu = {
        "schema_version": SCHEMA_VERSION,
        "wu_id": wu_name(require(settings, "campaign.wu_prefix"), require(settings, "campaign.number"), serial),
        "campaign_id": require(settings, "campaign.id"),
        "wu_type": "cascade",
        "app_version_min": "1",
        "random_seed": seed,
        "size_tier": size_tier_for(settings, n_atoms),
        "points": points,
        "checkpoint_interval_steps": require(settings, "simulation.check_interval_steps")
                                     * require(settings, "simulation.checkpoint_every_checks"),
        "material": {
            "family": require(settings, "campaign.material_family"),
            "composition": require(settings, "campaign.composition"),
            "potential_id": potential_id,
        },
        "temperature_k": temperature_k,
        "pka": {
            "energy_ev": energy_ev,
            "direction": [c / norm for c in direction],
            "element": require(settings, "campaign.pka_element"),
        },
        "box": {"unit_cells": [cells] * 3, "lattice": potential["lattice"], "n_atoms_expected": n_atoms},
        "electronic": {"stopping_model": "es_default", "eph_coupling": "none"},
        "initial_state": {"kind": "pristine"},
    }
    jsonschema.validate(wu, WU_SCHEMA)
    return wu


def render_params(settings: dict, wu: dict) -> str:
    """params.lmp for the LAMMPS template. Every value is a LAMMPS variable definition."""
    sim = "simulation"
    potential = require(settings, f"potentials.{wu['material']['potential_id']}")
    dt_max = require(settings, f"{sim}.dt_max_ps")
    if wu["electronic"]["eph_coupling"] != "none":
        raise ValueError("electron-phonon coupling is not supported by the alpha template")
    values = {
        "seed": wu["random_seed"],
        "n": wu["box"]["unit_cells"][0],
        "a0": require(settings, f"potentials.{wu['material']['potential_id']}.lattice_constant_angstrom"),
        "temp": wu["temperature_k"],
        "pka_e": wu["pka"]["energy_ev"],
        "pka_dx": wu["pka"]["direction"][0],
        "pka_dy": wu["pka"]["direction"][1],
        "pka_dz": wu["pka"]["direction"][2],
        "tcells": require(settings, f"{sim}.thermostat_cells"),
        "tdamp": require(settings, f"{sim}.thermostat_damp_ps"),
        "dt_max": dt_max,
        "dx_max": require(settings, f"{sim}.dx_max_angstrom"),
        "equil_steps": math.ceil(require(settings, f"{sim}.equilibration_ps") / dt_max),
        "check_steps": require(settings, f"{sim}.check_interval_steps"),
        "ckpt_every": require(settings, f"{sim}.checkpoint_every_checks"),
        "snap_every": require(settings, f"{sim}.snapshot_every_checks"),
        "snap_ke": require(settings, f"{sim}.snapshot_min_ke_ev"),
        "stop_window": require(settings, f"{sim}.stop_window_ps"),
        "stop_tol": require(settings, f"{sim}.stop_tolerance_pairs"),
        "max_time": require(settings, f"{sim}.max_time_ps"),
        "es_cutoff": require(settings, "electronic.es_default.cutoff_ev"),
    }
    lines = [f"variable wu_name string {wu['wu_id']}", f"variable lat string {potential['lattice']}"]
    lines += [f"variable {key} equal {value!r}" for key, value in values.items()]
    return "\n".join(lines) + "\n"


def parse_params(text: str) -> dict[str, str]:
    """Inverse of render_params: variable name -> value text."""
    params = {}
    for line in text.splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) == 4 and parts[0] == "variable" and parts[2] in ("equal", "string"):
            params[parts[1]] = parts[3]
    return params
