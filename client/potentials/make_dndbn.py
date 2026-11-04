"""Build W_DND_BN.dat: the Derlet-Nguyen-Manh-Dudarev W potential with the Bjorkas short-range fix.

Base: Derlet, Nguyen-Manh & Dudarev, Phys. Rev. B 76, 054107 (2007): E = sum F(rho_i) + 1/2 sum V,
F(rho) = -A sqrt(rho), f(r) = sum f_n (r_n - r)^3 H(r_n - r), V(r) likewise (Table IV, W).
Short range: Bjorkas, Nordlund & Dudarev, Nucl. Instrum. Methods B 267, 3204 (2009), Eqs. 1-5, with
the W values corrected in the erratum, NIMB 268, 1529 (2010): pair term ZBL (no shift for W) below
r1, a fifth-order polynomial to r2, DND above; density a constant below r3, a cubic to r4, DND above.
Values transcribed in docs/literature/potentials_W_campaign2.md sections 3.4-3.5 (UNVERIFIED there;
checked here by reproducing Derlet's published lattice properties, see the tests).

Usage: python3 client/potentials/make_dndbn.py OUTPUT.eam.fs
"""
from __future__ import annotations

import sys

import numpy as np

# Derlet 2007, Table IV (W). Knots in Angstrom.
A = 10.84238200368439
F_KNOTS = [(3.3216, 1.677334871575606), (3.165333333333333, -1.673137509507131),
           (3.009066666666667, -4.737051994974169), (2.8528, 7.870789420780674),
           (2.7411, -3.7924230525563378e-4), (2.604045, 6.190816158916646), (2.46699, -0.9565713891199151)]
V_KNOTS = [(4.2689, -0.1036435865158945), (3.98568, -0.2912948318493851), (3.70246, -2.096765499656263),
           (3.41924, 19.16045452701010), (3.13602, -41.01619862085917), (2.8528, 46.05205617244703),
           (2.7411, 26.42203930654883), (2.604045, 15.35211507804088), (2.46699, 14.12806259323987)]
# Bjorkas 2009 with the 2010 erratum (W row): pair splice r1..r2, density splice r3..r4.
R1, R2 = 1.10002200044, 2.10004200084
R3, R4 = 1.5000300006, 1.80003600072
RHO_PLATEAU = 10.0064910346
POLY = [1.389653276380862e4, -3.596912431628216e4, 3.739206756369099e4,
        -1.933748081656593e4, 0.495516793802426e4, -0.050264585985867e4]  # a0..a5, eV
DENSITY_CUBIC = [-0.659035020672109e3, 1.199684049310425e3, -0.707527073754107e3, 0.136726326994010e3]  # b0..b3
# Universal ZBL (Ziegler, Biersack, Littmark 1985), as in make_jw.py and LAMMPS pair_style zbl.
Z = 74
COULOMB = 14.399645  # e^2 / (4 pi eps0), eV*Angstrom
A_COEF = [0.18175, 0.50986, 0.28022, 0.02817]
D_COEF = [3.19980, 0.94229, 0.40290, 0.20162]
# Table: same grid as the Ackland-Thetford file the JW potential uses.
NRHO, DRHO, NR, DR, CUTOFF = 10000, 0.05, 10000, 0.00044, 4.4
MASS, A0 = 183.84, 3.1652  # Derlet Table II lattice constant (bcc), header only


def knot_sum(r: np.ndarray, knots: list[tuple[float, float]]) -> np.ndarray:
    """sum_n c_n (r_n - r)^3 for r < r_n (Derlet's cubic-knot form)."""
    return sum(c * np.clip(rn - r, 0.0, None) ** 3 for rn, c in knots)


def zbl(r: np.ndarray) -> np.ndarray:
    x = r / (0.46850 / (2 * Z ** 0.23))
    return Z * Z * COULOMB / r * sum(c * np.exp(-d * x) for c, d in zip(A_COEF, D_COEF))


def density(r: np.ndarray) -> np.ndarray:
    """f_BN(r): plateau below r3, cubic to r4, Derlet above."""
    cubic = sum(b * r ** k for k, b in enumerate(DENSITY_CUBIC))
    return np.where(r <= R3, RHO_PLATEAU, np.where(r <= R4, cubic, knot_sum(r, F_KNOTS)))


def r_pair(r: np.ndarray) -> np.ndarray:
    """r * V_BN(r); r = 0 keeps the finite ZBL limit Z^2 e^2 sum(c)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        inner = np.where(r > 0, r * zbl(r), Z * Z * COULOMB * sum(A_COEF))
    middle = r * sum(a * r ** k for k, a in enumerate(POLY))
    return np.where(r <= R1, inner, np.where(r <= R2, middle, r * knot_sum(r, V_KNOTS)))


def table() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """F(rho), rho(r) and r*phi(r) on the eam/fs grid."""
    rho = np.arange(NRHO) * DRHO
    r = np.arange(NR) * DR
    return -A * np.sqrt(rho), density(r), r_pair(r)


def main(dst: str) -> None:
    embed, dens, rphi = table()
    values = np.concatenate([embed, dens, rphi])
    out = ["DND W potential: Derlet, Nguyen-Manh & Dudarev, Phys. Rev. B 76, 054107 (2007), Table IV",
           "Short range: Bjorkas, Nordlund & Dudarev, NIMB 267, 3204 (2009) + erratum NIMB 268, 1529 (2010)",
           "Built by Nuclear@Home client/potentials/make_dndbn.py (eam/fs)",
           "1 W", f"{NRHO} {DRHO} {NR} {DR} {CUTOFF}", f"74    {MASS}    {A0}      bcc"]
    out += [" ".join(f"{v:.16e}" for v in values[i:i + 5]) for i in range(0, len(values), 5)]
    open(dst, "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
