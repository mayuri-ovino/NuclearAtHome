# Physics settings

Status: DRAFT

The single source of truth for every physics and analysis choice. Subagents read
values from here and never choose their own. Every number must trace to a verified
source (`TODO-LIT`), a measurement (`TODO-CALIBRATE`), or an explicit decision
(`TODO-DECIDE`) recorded in the decision log at the bottom.

## 1. Interatomic potentials

| potential_id | Material | Type | Short-range treatment | Source | Validated properties | Status |
|---|---|---|---|---|---|---|
| `W_EAM_A` | W | EAM/FS: Juslin-Wirth (J. Nucl. Mater. 432, 61, 2013) modified Ackland-Thetford, built exactly from the paper's Eq. 3 and Table 2 on the NIST AT file (sha256 308e805b…) by `client/potentials/make_jw.py` | ZBL − 10 eV below r1 = 1.391 Å, fifth-order polynomial to r2 = 2.601 Å, AT above (joins agree to 0.1% in value and slope) | measured: ⟨111⟩ dumbbell formation 9.52 eV (paper Table 3: 9.50; plain AT 8.87 vs 8.88); a0 3.1652 Å (0 K), 3.1674 Å (300 K NPT; Setyawan: 3.167) | chosen |
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
| `es_default` | Electronic stopping, `fix electron/stopping` (friction above a cutoff energy) | cutoff 30 eV = E_D^min of W (Hemani et al., arXiv:2005.11940 p.5, the method Warrier & Bhardwaj cite; Byggmästar 2025 uses 10 eV); stopping table SRIM-2013 SR Module, W in W, 19.35 g/cm³ (`client/potentials/srim2013_W_in_W.txt` → `stopping_W.dat`). Known gap: Hemani/Warrier use Lindhard-Scharff stopping, not SRIM | read 2026-11-02 |
| `eph_ttm_A` | Two-temperature model | coupling constant TODO-LIT, electronic heat capacity TODO-LIT | TODO-LIT |
| `none` | No electron–phonon coupling | — | — |

## 3. Simulation setup

| Setting | Value | Notes |
|---|---|---|
| Box size rule | 5 keV: 50³ cells; 10 keV: 75³ cells (Warrier & Bhardwaj Table 1, read 2026-11-01) | Must be confirmed by convergence tests; boundary hits are flagged |
| Boundary conditions | Periodic; outermost 1 unit cell held fixed during the cascade, next 2 cells Langevin-thermostatted at T (Warrier & Bhardwaj Sec. 2) | |
| Thermostat | Edge layer only: 2 unit cells, Langevin damping 0.1 ps (damping is a convention; not given in the benchmark papers) | |
| Timestep | Adaptive (`fix dt/reset`), max displacement 0.005 Å per step (Setyawan 2015 Sec. 2), max timestep 1 fs (Warrier & Bhardwaj) | Smoke runs conserve energy to ~2e-4 of the PKA energy |
| Equilibration before PKA | 10 ps Langevin at T in a box at the lattice constant measured at that T (NPT, 0 bar; table in `config/settings.toml`). Warrier & Bhardwaj use 10 ps NPT; starting from the measured a0(T) is equivalent | |
| Stop condition | Fixed length: every run is 20 ps after the PKA (Warrier & Bhardwaj NVE length), no early stop (decision log) | |
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
| Vacancy cluster cutoff | 4th-nearest neighbour, a0·√11/2 (Setyawan 2015 Sec. 3.2), from each WU's own a0(T), × (1 + 0.001) so exact-shell pairs join (approved by the human 2026-11-03) |
| Interstitial cluster cutoff | 3rd-nearest neighbour, a0·√2 (Setyawan 2015 Sec. 3.2), from each WU's own a0(T), × (1 + 0.001), applied to interstitial atom positions (not their sites; whether Setyawan clustered by site or position is TODO-LIT) (approved by the human 2026-11-03) |
| Uncertainty reporting | Standard error and bootstrap 95% interval (2,000 resamples, fixed seed), with sample size |
| Tail statistics (Campaign 3) | Per bin, one value per independent validated non-canary cascade (outliers included): Frenkel-pair p50/p90/p99 (nearest rank) with order-statistic 95% intervals, shown only if ≥ 10 cascades lie above the quantile; largest of n; share of cascades whose largest interstitial/vacancy cluster is ≥ 5, 10, 20, 50 with Clopper–Pearson 95% intervals; mean clusters ≥ N per cascade with cascade-level bootstrap intervals; boundary-hit count. Intervals are per cell, not simultaneous (approved by the human 2026-11-03). Follow-ups: pooled per-cascade cluster-size CCDF and a maximum-likelihood power-law fit (Clauset–Shalizi–Newman) before any exponent is reported; failed WUs' impacts are retried, not redrawn (done 2026-11-03) |

## 6. Benchmarks to reproduce before launch

| Case | Material | Energy | Temperature | Potential | Published value | Source |
|---|---|---|---|---|---|---|
| B1 | W | 5 keV | 300 K | Juslin-Wirth EAM (W_EAM_A, exact) | defect counts vs arc-dpa (Fig. 2, figure only; digitize) | Warrier & Bhardwaj arXiv:2402.00359 (read; counts figure-only, to digitize) |
| B2 | W | 10 keV | 300 K | Juslin-Wirth EAM (W_EAM_A, exact) | defect counts (Fig. 2) and Setyawan 2015 Fig. 1a power law | Warrier & Bhardwaj; Setyawan JNM 462, 329 (read; counts figure-only, to digitize) |
| B3 | Fe | TODO | TODO | TODO | TODO-LIT | TODO-LIT |

## Decision log

| Date | Decision | Reason | Approved by |
|---|---|---|---|
| 2026-11-01 | EAM potentials only for the alpha | Fast, well studied; benchmark papers use EAM | human |
| 2026-11-01 | PKA energies from benchmark papers: 5 and 10 keV, 300 K | Small tier, direct benchmark comparison | human |
| 2026-11-01 | Reference WU earns 1760 points (`ref_points`) | Credit calibration | human |
| 2026-11-01 | Values marked UNVERIFIED were taken from lit-researcher notes; the human must check each against the paper | Science integrity | done 2026-11-02: human supplied the papers, main agent checked each value on the page |
| 2026-11-01 | Human delegated physics decisions to the main agent; each row below states its basis | Human request | human |
| 2026-11-01 | (superseded 2026-11-02) W_EAM_A = AT1987 + ZBL core with r1/r2 borrowed from JW | JW file not public at the time | main agent |
| 2026-11-02 | W_EAM_A = exact Juslin-Wirth from the paper's Eq. 3 / Table 2 (human supplied the paper) | Matches the benchmark potential; ⟨111⟩ dumbbell 9.52 vs 9.50 eV | main agent |
| 2026-11-02 | Stopping cutoff 30 eV (E_D^min, Hemani et al.); SRIM-2013 table | Matches the benchmark's stopping reference; Hemani found E_D^min best matches NRT losses | main agent |
| 2026-11-02 | V4 tolerance 0.5% of PKA energy (was 0.2%) | Measured (2 keV, JW + SRIM stopping, 30 eV cutoff): drift 4.2e-4 without stopping (JW's published, rounded coefficients leave a 0.08 eV step at r1; kept as published) and 8.8e-4 with stopping (electron/stopping's energy tally); neither is cascade physics | main agent |
| 2026-11-02 | V4 = drift / (E_PKA + thermostat-removed energy) ≤ 1% | 5 keV calibration run: drift 36.6 eV grew with the 3.9 keV the thermostat removed (Langevin tally ~1% inexact), stopping added ~3 eV; drift/flow 4.1e-3. Per PKA energy it was 7.3e-3, which wrongly failed an honest run | main agent |
| 2026-11-02 | GPU app version (core 0xa2): LAMMPS GPU package over OpenCL, full double precision, only pair eam/fs on the GPU | Human chose OpenCL first. Checked on an RTX 4070: perfect-lattice total energy identical to CPU (−142,398.97 eV), V4 drift 9.1e-4 (limit 1e-2), 2.7× faster on a 16,000-atom test while the GPU was shared with Folding@home | main agent |
| 2026-11-02 | GPU version 1.01: neighbour lists on the CPU (`-pk gpu 1 neigh no`) | GPU-built lists crashed (OpenCL -9999) at step ~5,300 of a real 5 keV run, deterministically; with `neigh no` the full run passed V1-V8 (V4 drift/flow 3.9e-3), 34 min vs 97 on CPU. Cost: 13 GB peak host RAM, too much for typical volunteers: must be reduced before public release | main agent |
| 2026-11-02 | Cascade loop runs chunks with `run N pre no post no` | Each `run` re-setup leaked ~17 MB of host RAM in the NVIDIA OpenCL driver (13 GB per cascade). Without re-setup: peak 536 MB, 30 min; same 5 keV WU passes V4 (3.6e-3 vs 3.9e-3 before), 5 FP both. `f_es` then sums from the last full setup, so `elec_loss = off_elec + f_es` (measured); `f_th` still restarts each run. Physics review: approve, dt is no longer recomputed at chunk boundaries (trajectory-level only) | main agent, physics-reviewer |
| 2026-11-02 | Setyawan values verified in the paper (a0 300 K, 0.005 Å, NN3/NN4) | Human supplied the papers | main agent |
| 2026-11-01 | a0 = 3.1674 Å, measured (NPT, 300 K, 0 bar) with this potential | Measurement; matches Setyawan's 3.167 Å for JW at 300 K | main agent |
| 2026-11-02 | Temperatures 300, 600 and 1025 K at 5 and 10 keV (human approved) | 1025 K: Setyawan 2015 benchmark temperature, allowing direct comparison (their potential is AT with a hardened short range; identity with JW is TODO-LIT; their Region-1 fit lines suggest roughly 20% fewer Frenkel pairs than at 300 K, per-energy values TODO-DIGITIZE Fig. 1a). It lies below ITER's reported ~1000 °C (≈1273 K) peak divertor surface temperature, which has no benchmark found. 600 K (327 °C): within the upper part of Stork et al.'s 200–350 °C window for the Cu-alloy substructure of an older water-cooled EU-DEMO divertor concept; the W armour bulk temperature is TODO-LIT. Sources and gaps: `docs/literature/temperatures_W.md` (UNVERIFIED until checked against the originals) | human, main agent |
| 2026-11-02 | a0(T) per temperature: 3.1674 / 3.1726 / 3.1837 Å at 300 / 600 / 1025 K | Measured with `client/potentials/measure_a0.lmp` (NPT 0 bar, 16³ cells, 10 ps + 20 ps average; thermal fluctuation std ≤ 0.0007 Å, single run and seed); 300 K reproduces the earlier value, 1025 K agrees with Setyawan's 3.184 Å (a consistency check: their potential is not confirmed identical). An unmeasured temperature is refused (no interpolation) | main agent |
| 2026-11-02 | V7 sanity bounds (NRT at full PKA energy) extended to 250–1100 K | NRT does not depend on temperature and temperature lowers survivors, so the bound still only catches crashes; benchmark ranges per temperature still TODO-LIT (digitize Setyawan Fig. 1a) | main agent |
| 2026-11-02 | final.dump positions written to 1e-6 Å (`%.6f`), not 17 digits; stored results recompressed losslessly as xz | Measured on stored results: no Wigner–Seitz count changed at 6, 4 or 3 decimals; ~0.3 atoms per result lie within 0.03 Å of a cell boundary, so a flip (and a V6 rejection of valid work, biased toward large cascades) is expected in ~3e-3 of results at 1e-4 Å and ~3e-5 at 1e-6 Å. Upload 7.2 → 3.8 MB, storage → 2.6 MB per result. Checkpoints keep full precision. Physics review: approve at 1e-6 Å | main agent, physics-reviewer |
| 2026-11-02 | Cluster cutoffs computed per WU from its a0(T) with relative tolerance 0.001 (approved by the human 2026-11-03) | Bug: the fixed Å cutoffs were rounded down from the 300 K a0, so vacancies exactly 4NN apart never joined, at every temperature; for interstitials (clustered by atom position, so not exactly at shell distances) the a0(T) correction shifts the cutoff by about 0.5% at 600/1025 K. Found by physics review. Stored results re-analysed with `scripts/reanalyse_clusters.py`: WA-0001-00000031 vacancies [1,1,1] → [2,1]; counts unchanged. The next shell is ≥ 4.4% farther, so 0.1% never reaches it (`cluster_cutoff` refuses a tolerance that would) | main agent, physics-reviewer |
| 2026-11-02 | Tail statistics for Campaign 3 (table above) (approved by the human 2026-11-03) | Physics review of the first version (reject): percentiles were shown at any n, boundary hits hidden, Wilson coverage dips for rare events, settings untraced. Re-review: approve with changes; fixed since: rare-event intervals withheld below 10 cascades, boundary hits per tail cell, percentile rounding gate. Approved by the human 2026-11-03 | human, main agent, physics-reviewer |
| 2026-11-02 | Pooling rule: results of one (potential, energy, temperature) bin are pooled across input-template versions only when the versions are physics-equivalent per this log; the 2026-11-02 template (chunked warm-up for progress, 1e-6 Å final positions) is (identical dynamics measured; rounding analysed above). Done 2026-11-03: each WU records its content-addressed inputs (template, potential, stopping table; `workunits.inputs`), and a failed WU's direction and seed are retried up to 3 times before counting as permanently failed (`work_generator.claim_retry`) | main agent, physics-reviewer |
| 2026-11-01 | Fixed outer cell + 2-cell thermostat, 1 fs max timestep, 10 ps equilibration, 20 ps runs | Warrier & Bhardwaj protocol (read directly) | main agent |
| 2026-11-01 | No early stop; V5 = run reached 20 ps; non-stabilized runs stay valid | Benchmark uses fixed-length runs; volunteers not punished for physics | main agent |
| 2026-11-01 | Replicas equivalent when both pass V1-V8; outliers (>5 sd, bins of ≥30) kept and flagged, never held or rejected | Rare cascades are physics; cheating is handled by replication + canaries | main agent |
| 2026-11-01 | V4 tolerance 0.2% of PKA energy; V3 minimum 20,000 steps | 10× the measured drift (physics review: 1% was loose); 20 ps at ≤1 fs | main agent |
| 2026-11-01 | V7 range 0..NRT(E_PKA, E_d = 42 eV): 47 at 5 keV, 95 at 10 keV | Crash/garbage detector only, never to be cited as a physical range; replace with benchmark-derived ranges | main agent |
| 2026-11-01 | V2 also rejects replays (same final.dump/energy.txt as a stored result) and runs whose PKA did not start on the centre site and move along the WU direction (cos > 0.9 over the first ~0.5 Å) | Replication no longer compares replicas, so these replace that anti-cheat role (physics review) | main agent |
| 2026-11-01 | Flag, not reject, runs where a recoil above 10 eV reaches the thermostat/fixed layers | Channelled PKAs can hit the rigid boundary; 10 eV = stopping cutoff, ~400 kT at 300 K | main agent |
| 2026-11-01 | Canaries 2%, canary tolerance 3 sd of the reference runs | Convention | main agent |
| 2026-11-01 | Seeds ≤ 899,990,000 | LAMMPS aborts above 900,000,000 (tested) | main agent |
