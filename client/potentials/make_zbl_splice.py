"""Build W_EAM_A.dat: the Ackland-Thetford 1987 W potential with a ZBL short-range pair term.

Reconstructs the Juslin-Wirth (J. Nucl. Mater. 432, 61, 2013) hardening, whose own file is
not publicly available: the pair potential is ZBL below r1, Ackland-Thetford above r2, and a
quintic smoothstep blend between them. r1 = 1.39 Å and r2 = 2.6 Å are the JW transition
distances in Warrier & Bhardwaj, arXiv:2402.00359, Table 2. Embedding and density are unchanged.

Usage: python3 client/potentials/make_zbl_splice.py SOURCE.eam.fs OUTPUT.eam.fs
"""
from __future__ import annotations

import sys

import numpy as np

R1, R2 = 1.39, 2.6
Z = 74
# Universal ZBL screening (Ziegler, Biersack, Littmark 1985), as in LAMMPS pair_style zbl.
COULOMB = 14.399645  # e^2 / (4 pi eps0) in eV·Å, LAMMPS metal units (force->qqr2e)
A_COEF = [0.18175, 0.50986, 0.28022, 0.02817]
D_COEF = [3.19980, 0.94229, 0.40290, 0.20162]


def zbl_r_phi(r: np.ndarray) -> np.ndarray:
    """r * phi_ZBL(r) for W-W, in eV·Å (finite at r = 0)."""
    a = 0.46850 / (2 * Z ** 0.23)
    x = r / a
    return Z * Z * COULOMB * sum(c * np.exp(-d * x) for c, d in zip(A_COEF, D_COEF))


def smoothstep(x: np.ndarray) -> np.ndarray:
    """0 below 0, 1 above 1, C2-continuous quintic in between."""
    x = np.clip(x, 0.0, 1.0)
    return x ** 3 * (10 - 15 * x + 6 * x ** 2)


def splice(r: np.ndarray, r_phi_eam: np.ndarray) -> np.ndarray:
    s = smoothstep((r - R1) / (R2 - R1))
    return (1 - s) * zbl_r_phi(r) + s * r_phi_eam


def main(src: str, dst: str) -> None:
    lines = open(src).read().splitlines()
    header, element_line = lines[:5], lines[5]
    nrho, drho, nr, dr, cutoff = lines[4].split()
    nrho, nr, dr = int(nrho), int(nr), float(dr)
    values = np.array(" ".join(lines[6:]).split(), dtype=float)
    # eam/fs, one element: F(rho) [nrho], rho(r) [nr], then r*phi(r) [nr]
    if len(values) != nrho + 2 * nr:
        raise ValueError(f"unexpected table length {len(values)}")
    r = np.arange(nr) * dr
    values[nrho + nr:] = splice(r, values[nrho + nr:])
    note = (f"ZBL pair term spliced in by make_zbl_splice.py: ZBL below {R1} A, quintic blend to "
            f"Ackland-Thetford at {R2} A (Juslin-Wirth transition distances).")
    out = [header[0], header[1], note, *header[3:5], element_line]
    out += [" ".join(f"{v:.16e}" for v in values[i:i + 5]) for i in range(0, len(values), 5)]
    open(dst, "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
