# Physics settings

Status: DRAFT

The single source of truth for every physics and analysis choice. Subagents read
values from here and never choose their own. Every number must trace to a verified
source (`TODO-LIT`), a measurement (`TODO-CALIBRATE`), or an explicit decision
(`TODO-DECIDE`) recorded in the decision log at the bottom.

## 1. Interatomic potentials

| potential_id | Material | Type | Short-range treatment | Source | Validated properties | Status |
|---|---|---|---|---|---|---|
| `W_EAM_A` | W | EAM/FS: Juslin-Wirth 2013 (Ackland-Thetford hardened at short range), J. Nucl. Mater. 432, 61 | ZBL join r1/r2 = 1.39/2.6 Å (secondary: Warrier & Bhardwaj, arXiv:2402.00359; primary paper not opened) | `docs/literature/w_potentials.md` A4 | TODO | chosen (UNVERIFIED) |
| `W_ML_A` | W | ML (GAP/ACE/MTP) | trained on short-range data? TODO-LIT | TODO-LIT | TODO | candidate |
| `WRe_A` | W-Re | TODO | TODO-LIT | TODO-LIT | TODO | candidate |
| `WH_A` | W-H | TODO | TODO-LIT | TODO-LIT | TODO | candidate (trapping) |
| `FeCr_A` | Fe-Cr (RAFM proxy) | TODO | TODO-LIT | TODO-LIT | TODO | later campaign |

Before a potential is approved, record: threshold displacement energies,
vacancy and interstitial formation energies, elastic constants, melting point,
and (for H/T potentials) H solution and vacancy–H binding energies, each compared
to DFT or experiment with sources.

## 2. Electronic effects

| key | Model | Parameters | Source |
|---|---|---|---|
| `es_default` | Electronic stopping (friction above a cutoff energy) | cutoff 10 eV (Byggmästar 2025, SRIM-based; papers range 1-100 eV), stopping table from SRIM TODO-LIT | UNVERIFIED |
| `eph_ttm_A` | Two-temperature model | coupling constant TODO-LIT, electronic heat capacity TODO-LIT | TODO-LIT |
| `none` | No electron–phonon coupling | — | — |

## 3. Simulation setup

| Setting | Value | Notes |
|---|---|---|
| Box size rule | 5 keV: 50³ cells; 10 keV: 75³ cells (Warrier & Bhardwaj Table 1, UNVERIFIED) | Must be confirmed by convergence tests |
| Boundary conditions | Periodic | |
| Thermostat | Edge layer only, thickness TODO-DECIDE, never in cascade core | |
| Timestep | Adaptive, max displacement 0.005 Å per step (Setyawan 2015, UNVERIFIED), max timestep TODO-DECIDE | |
| Equilibration before PKA | 10 ps (Warrier & Bhardwaj, UNVERIFIED; they use NPT, we use a fixed lattice constant at T) | |
| Stop condition | Frenkel pair count stable within TODO-DECIDE over TODO-DECIDE ps, with a hard maximum time of 20 ps (Warrier & Bhardwaj NVE length, UNVERIFIED) | |
| Checkpoint interval | TODO-DECIDE steps (target: every few minutes of wall time) | |
| PKA direction | Random on the unit sphere, avoiding low-index channeling directions within TODO-DECIDE degrees? | Decide and justify |
| PKA energy sampling | From recoil spectrum file (human supplies) | Spectrum ID recorded per WU |

## 4. Trapping stage

| Setting | Value |
|---|---|
| Tritium mass | Use the standard atomic mass of ³H (≈3.016 u); confirm exact value from a standard reference |
| Insertion methods allowed | random_interstitial, near_defects, uniform_grid |
| Anneal times | TODO-DECIDE |
| Trapped vs free criterion | TODO-DECIDE (distance to defect, or local energy) |
| Binding energy method | relaxation for all sites; NEB for a subset of TODO-DECIDE sites |

## 5. Analysis settings

| Setting | Value |
|---|---|
| Defect identification | Wigner–Seitz cell analysis (primary); TODO-DECIDE secondary method for comparison |
| Vacancy cluster cutoff | 4th-nearest neighbour, a0·√11/2 (Setyawan 2015, UNVERIFIED) |
| Interstitial cluster cutoff | 3rd-nearest neighbour, a0·√2 (Setyawan 2015, UNVERIFIED) |
| Uncertainty reporting | Standard error and bootstrap 95% interval, with sample size |

## 6. Benchmarks to reproduce before launch

| Case | Material | Energy | Temperature | Potential | Published value | Source |
|---|---|---|---|---|---|---|
| B1 | W | 5 keV | 300 K | Juslin-Wirth EAM | defect counts vs arc-dpa (Fig. 2, figure only; digitize) | Warrier & Bhardwaj arXiv:2402.00359 (UNVERIFIED) |
| B2 | W | 10 keV | 300 K | Juslin-Wirth EAM | defect counts (Fig. 2) and Setyawan 2015 Fig. 1a power law | Warrier & Bhardwaj; Setyawan JNM 462, 329 (UNVERIFIED) |
| B3 | Fe | TODO | TODO | TODO | TODO-LIT | TODO-LIT |

## Decision log

| Date | Decision | Reason | Approved by |
|---|---|---|---|
| 2026-11-01 | EAM potentials only for the alpha | Fast, well studied; benchmark papers use EAM | human |
| 2026-11-01 | PKA energies from benchmark papers: 5 and 10 keV, 300 K | Small tier, direct benchmark comparison | human |
| 2026-11-01 | Reference WU earns 1760 points (`ref_points`) | Credit calibration | human |
| 2026-11-01 | Values marked UNVERIFIED were taken from lit-researcher notes; the human must check each against the paper | Science integrity | pending |
