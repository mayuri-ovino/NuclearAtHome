"""Convert a SRIM SR Module table to a LAMMPS fix electron/stopping file.

Keeps only ion energy (eV) and ELECTRONIC stopping (eV/Å): nuclear stopping is already in
the MD forces. The SRIM table must be in eV/Angstrom units (checked).

Usage: python3 client/potentials/srim_to_lammps.py SRIM_TABLE E_MAX_EV OUTPUT
"""
from __future__ import annotations

import re
import sys

UNIT = {"eV": 1.0, "keV": 1e3, "MeV": 1e6, "GeV": 1e9}
ROW = re.compile(r"^\s*([0-9.]+)\s*(eV|keV|MeV|GeV)\s+([0-9.Ee+-]+)\s+[0-9.Ee+-]+\s")


def convert(text: str, e_max_ev: float) -> list[tuple[float, float]]:
    """(energy eV, electronic stopping eV/Å) rows, ascending, from the first row up to e_max_ev.

    Under Wine the SR Module writes a fixed-size buffer: after the last real row (E-Max) the
    file holds leftover junk rows. The table ends at the first non-increasing energy, and it
    must reach the requested E-Max, so a truncated table is rejected.
    """
    if "Stopping Units =  eV/Angstrom" not in text:
        raise ValueError("SRIM table is not in eV/Angstrom")
    rows: list[tuple[float, float]] = []
    for match in map(ROW.match, text.splitlines()):
        if match:
            row = (float(match[1]) * UNIT[match[2]], float(match[3]))
            if rows and row[0] <= rows[-1][0]:
                break
            rows.append(row)
    if len(rows) < 2 or abs(rows[-1][0] - e_max_ev) > 1e-6 * e_max_ev:
        raise ValueError(f"SRIM table does not reach E-Max {e_max_ev} eV")
    return rows


def main(src: str, e_max_ev: str, dst: str) -> None:
    rows = convert(open(src).read(), float(e_max_ev))
    with open(dst, "w") as handle:
        handle.write(f"# Electronic stopping of W ions in W, eV vs eV/Angstrom, from {src.split('/')[-1]}\n"
                     "# (SRIM-2013 SR Module, density 19.35 g/cm3); converted by srim_to_lammps.py\n")
        handle.writelines(f"{e:.6g} {s:.6g}\n" for e, s in rows)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
