# Physics settings

Status: DRAFT

The single source of truth for every physics and analysis choice. Subagents read
values from here and never choose their own. Every number must trace to a verified
source (`TODO-LIT`), a measurement (`TODO-CALIBRATE`), or an explicit decision
(`TODO-DECIDE`) recorded in the decision log at the bottom.

## 1. Interatomic potentials

| potential_id | Material | Type | Short-range treatment | Source | Validated properties | Status |
|---|---|---|---|---|---|---|
| `W_EAM_A` | W | EAM | ZBL blended, range TODO-LIT | TODO-LIT | TODO | candidate |
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
| `es_default` | Electronic stopping (friction above a cutoff energy) | cutoff TODO-LIT, stopping data TODO-LIT | TODO-LIT |
| `eph_ttm_A` | Two-temperature model | coupling constant TODO-LIT, electronic heat capacity TODO-LIT | TODO-LIT |
| `none` | No electron–phonon coupling | — | — |

## 3. Simulation setup

| Setting | Value | Notes |
|---|---|---|
| Box size rule | TODO-DECIDE (minimum unit cells as a function of PKA energy) | Must be confirmed by convergence tests |
| Boundary conditions | Periodic | |
| Thermostat | Edge layer only, thickness TODO-DECIDE, never in cascade core | |
| Timestep | Adaptive, max displacement per step TODO-DECIDE, max timestep TODO-DECIDE | |
| Equilibration before PKA | TODO-DECIDE ps | |
| Stop condition | Frenkel pair count stable within TODO-DECIDE over TODO-DECIDE ps, with a hard maximum time TODO-DECIDE | |
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
| Vacancy cluster cutoff | TODO-DECIDE (e.g., between nth-nearest neighbors) |
| Interstitial cluster cutoff | TODO-DECIDE |
| Uncertainty reporting | Standard error and bootstrap 95% interval, with sample size |

## 6. Benchmarks to reproduce before launch

| Case | Material | Energy | Temperature | Potential | Published value | Source |
|---|---|---|---|---|---|---|
| B1 | W | TODO | TODO | TODO | TODO-LIT | TODO-LIT |
| B2 | W | TODO | TODO | TODO | TODO-LIT | TODO-LIT |
| B3 | Fe | TODO | TODO | TODO | TODO-LIT | TODO-LIT |

## Decision log

| Date | Decision | Reason | Approved by |
|---|---|---|---|
| | | | |
