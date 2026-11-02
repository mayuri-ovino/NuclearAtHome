# Physics settings

Status: DRAFT

The single source of truth for every physics and analysis choice. Subagents read
values from here and never choose their own. Every number must trace to a verified
source (`TODO-LIT`), a measurement (`TODO-CALIBRATE`), or an explicit decision
(`TODO-DECIDE`) recorded in the decision log at the bottom.

## 1. Interatomic potentials

| potential_id | Material | Type | Short-range treatment | Source | Validated properties | Status |
|---|---|---|---|---|---|---|
| `W_EAM_A` | W | EAM/FS: "AT1987 + ZBL core": Ackland-Thetford 1987 (NIST IPR file, sha256 308e805b…) with a ZBL pair core, transition distances r1/r2 borrowed from Juslin-Wirth. NOT a reconstruction of JW: between 1.6 and 2.6 Å it is AT to within ~10%, so JW's own refit there is absent; file built by `client/potentials/make_zbl_splice.py` | ZBL below 1.39 Å, quintic smoothstep blend to AT by 2.6 Å (JW r1/r2 from Warrier & Bhardwaj Table 2, read 2026-11-01) | measured here: a0 3.1652 Å (0 K), 3.1674 Å (300 K NPT); E_coh 8.90 eV; vacancy formation 3.63 eV (unrelaxed volume); TDE ⟨100⟩ ≈ 69 eV (0 K, exact direction). JW per Warrier Table 3: a 3.160, VFE 3.84, TDE⟨100⟩ 54.3 eV. So TDE⟨100⟩ is ~27% above JW and VFE 0.21 eV below: expect fewer Frenkel pairs than JW papers. B1/B2 are a qualitative comparison until the real JW file is used. TODO: TDE measured as Warrier does (TODO-LIT method), SIA ⟨111⟩/⟨110⟩ dumbbell formation energies | chosen (human sign-off before any published B1/B2 comparison) |
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
| `es_default` | Electronic stopping, `fix electron/stopping` (friction above a cutoff energy, as Warrier & Bhardwaj) | cutoff 10 eV (Byggmästar 2025; papers range 1-100 eV), stopping table for W in W from SRIM: TODO-LIT (human runs SRIM) | UNVERIFIED |
| `eph_ttm_A` | Two-temperature model | coupling constant TODO-LIT, electronic heat capacity TODO-LIT | TODO-LIT |
| `none` | No electron–phonon coupling | — | — |

## 3. Simulation setup

| Setting | Value | Notes |
|---|---|---|
| Box size rule | 5 keV: 50³ cells; 10 keV: 75³ cells (Warrier & Bhardwaj Table 1, read 2026-11-01) | Must be confirmed by convergence tests; boundary hits are flagged |
| Boundary conditions | Periodic; outermost 1 unit cell held fixed during the cascade, next 2 cells Langevin-thermostatted at T (Warrier & Bhardwaj Sec. 2) | |
| Thermostat | Edge layer only: 2 unit cells, Langevin damping 0.1 ps (damping is a convention; not given in the benchmark papers) | |
| Timestep | Adaptive (`fix dt/reset`), max displacement 0.005 Å per step (Setyawan 2015, UNVERIFIED), max timestep 1 fs (Warrier & Bhardwaj) | Smoke runs conserve energy to ~2e-4 of the PKA energy |
| Equilibration before PKA | 10 ps Langevin at T in a box at the measured 300 K lattice constant (Warrier & Bhardwaj use 10 ps NPT; equivalent at 300 K only) | |
| Stop condition | Frenkel pair count stable within TODO-DECIDE over TODO-DECIDE ps, with a hard maximum time of 20 ps (Warrier & Bhardwaj NVE length). Decision: no early stop (window = 20 ps), so every run is 20 ps like the benchmark | |
| Checkpoint interval | every 20 checks of 100 steps (2,000 steps) | measure wall time per checkpoint in calibration |
| PKA direction | Uniformly random on the unit sphere, no channeling exclusion | Matches the benchmark's random directions; channeling events are physics |
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
| Uncertainty reporting | Standard error and bootstrap 95% interval (2,000 resamples, fixed seed), with sample size |

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
| 2026-11-01 | Human delegated physics decisions to the main agent; each row below states its basis | Human request | human |
| 2026-11-01 | W_EAM_A = AT1987 + ZBL core with r1/r2 borrowed from JW (the JW file is not publicly available) | Reproducible and public; it is not JW (physics review): differences recorded in section 1 | main agent |
| 2026-11-01 | a0 = 3.1674 Å, measured (NPT, 300 K, 0 bar) with this potential | Measurement; matches Setyawan's 3.167 Å for JW at 300 K | main agent |
| 2026-11-01 | Fixed outer cell + 2-cell thermostat, 1 fs max timestep, 10 ps equilibration, 20 ps runs | Warrier & Bhardwaj protocol (read directly) | main agent |
| 2026-11-01 | No early stop; V5 = run reached 20 ps; non-stabilized runs stay valid | Benchmark uses fixed-length runs; volunteers not punished for physics | main agent |
| 2026-11-01 | Replicas equivalent when both pass V1-V8; outliers (>5 sd, bins of ≥30) kept and flagged, never held or rejected | Rare cascades are physics; cheating is handled by replication + canaries | main agent |
| 2026-11-01 | V4 tolerance 0.2% of PKA energy; V3 minimum 20,000 steps | 10× the measured drift (physics review: 1% was loose); 20 ps at ≤1 fs | main agent |
| 2026-11-01 | V7 range 0..NRT(E_PKA, E_d = 42 eV): 47 at 5 keV, 95 at 10 keV | Crash/garbage detector only, never to be cited as a physical range; replace with benchmark-derived ranges | main agent |
| 2026-11-01 | V2 also rejects replays (same final.dump/energy.txt as a stored result) and runs whose PKA did not start on the centre site and move along the WU direction (cos > 0.9 over the first ~0.5 Å) | Replication no longer compares replicas, so these replace that anti-cheat role (physics review) | main agent |
| 2026-11-01 | Flag, not reject, runs where a recoil above 10 eV reaches the thermostat/fixed layers | Channelled PKAs can hit the rigid boundary; 10 eV = stopping cutoff, ~400 kT at 300 K | main agent |
| 2026-11-01 | Canaries 2%, canary tolerance 3 sd of the reference runs | Convention | main agent |
| 2026-11-01 | Seeds ≤ 899,990,000 | LAMMPS aborts above 900,000,000 (tested) | main agent |
