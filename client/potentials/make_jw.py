"""Build W_EAM_A.dat: the Juslin-Wirth (2013) modified Ackland-Thetford W potential.

Juslin & Wirth, J. Nucl. Mater. 432, 61-66 (2013), Eq. (3) and Table 2: the W-W pair term is
ZBL - 10 eV below r1, a fifth-order polynomial between r1 and r2, and the original
Ackland-Thetford pair term above r2. Embedding and density functions are unchanged.
The AT tables come from the NIST IPR file Ackland_Thetford_1987_W.eam.fs.

Usage: python3 client/potentials/make_jw.py SOURCE.eam.fs OUTPUT.eam.fs
"""
from __future__ import annotations

import sys

import numpy as np

# Juslin & Wirth 2013, Table 2 (units: eV and Å).
R1, R2 = 1.39139856, 2.60079984
POLY = [6.02476984e+03, -1.31022346e+04, 1.14668996e+04, -5.02451407e+03, 1.09903719e+03, -9.58391332e+01]  # a0..a5
ZBL_SHIFT = 10.0  # eV, "the ZBL potential was reduced by 10 eV" (Sec. 2.1)
Z = 74
# Universal ZBL screening (Ziegler, Biersack, Littmark 1985), as in LAMMPS pair_style zbl.
COULOMB = 14.399645  # e^2 / (4 pi eps0) in eV·Å, LAMMPS metal units (force->qqr2e)
A_COEF = [0.18175, 0.50986, 0.28022, 0.02817]
D_COEF = [3.19980, 0.94229, 0.40290, 0.20162]


def zbl(r: np.ndarray) -> np.ndarray:
    """phi_ZBL(r) for W-W in eV."""
    x = r / (0.46850 / (2 * Z ** 0.23))
    return Z * Z * COULOMB / r * sum(c * np.exp(-d * x) for c, d in zip(A_COEF, D_COEF))


def polynomial(r: np.ndarray) -> np.ndarray:
    return sum(a * r ** k for k, a in enumerate(POLY))


def jw_r_phi(r: np.ndarray, r_phi_at: np.ndarray) -> np.ndarray:
    """r * phi_JW(r) on the table grid; r = 0 keeps the finite ZBL limit Z^2 e^2 sum(c)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        inner = np.where(r > 0, r * (zbl(r) - ZBL_SHIFT), Z * Z * COULOMB * sum(A_COEF))
    middle = r * polynomial(r)
    return np.where(r <= R1, inner, np.where(r <= R2, middle, r_phi_at))


def main(src: str, dst: str) -> None:
    lines = open(src).read().splitlines()
    nrho, _, nr, dr, _ = lines[4].split()
    nrho, nr, dr = int(nrho), int(nr), float(dr)
    values = np.array(" ".join(lines[6:]).split(), dtype=float)
    # eam/fs, one element: F(rho) [nrho], rho(r) [nr], then r*phi(r) [nr]
    if len(values) != nrho + 2 * nr:
        raise ValueError(f"unexpected table length {len(values)}")
    r = np.arange(nr) * dr
    values[nrho + nr:] = jw_r_phi(r, values[nrho + nr:])
    note = "Pair term modified per Juslin & Wirth, J. Nucl. Mater. 432, 61 (2013), Eq. 3 / Table 2 (make_jw.py)."
    out = [lines[0], lines[1], note, *lines[3:6]]
    out += [" ".join(f"{v:.16e}" for v in values[i:i + 5]) for i in range(0, len(values), 5)]
    open(dst, "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
