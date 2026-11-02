# Nuclear@Home — to-do list (highest priority first)

Updated 2026-11-01. "You" = the human; "agent" = Claude Code.

## 1. Blocks every real cascade run

1. **You: check every UNVERIFIED value against its paper.** Each is marked in `docs/interfaces/physics_settings.md` and `config/settings.toml`.
   - Juslin–Wirth EAM: the ZBL join r1/r2 = 1.39/2.6 Å comes from a secondary source (Warrier & Bhardwaj), not the Juslin–Wirth paper.
   - a0 = 3.167 Å at 300 K (Setyawan 2015, Table 1).
   - Box 50³ cells at 5 keV and 75³ at 10 keV; 10 ps equilibration; 20 ps run (Warrier & Bhardwaj).
   - Max displacement 0.005 Å per step (Setyawan 2015).
   - Electronic-stopping cutoff 10 eV (Byggmästar 2025). The papers range from 1 to 100 eV, and Warrier & Bhardwaj don't state theirs.
   - Cluster cutoffs: 3rd-nearest neighbour for interstitials, 4th for vacancies (Setyawan 2015).
2. **You + agent: get the Juslin–Wirth potential file and write `client/potentials/W_EAM_A.mod`, including the ZBL join.** How to splice ZBL is a physics decision. One option is a tabulated spliced pair potential; the other is a hybrid pair style. Not in the repo yet.
3. **Agent (with your OK to download): build LAMMPS with EXTRA-FIX.** Your installed LAMMPS (7 Feb 2024, Ubuntu) has no `fix electron/stopping`. The smoke test skipped that line. Use `client/build_lammps.sh`, which needs the tarball sha256 pinned first.
4. **You: make the electronic-stopping table for W** (SRIM, or the source a paper used), saved as `client/potentials/stopping_W.dat`.
5. **You: confirm what "1760 points" means.** Now: the 5 keV reference WU = 1760 points, and bigger WUs earn more in proportion to atoms × steps, so a 10 keV WU earns about 3.4×. If you want a flat 1760 for every WU, say so: that's a one-line change.
6. **You: decide the remaining physics settings (TODO-DECIDE)**:
   - max timestep `dt_max_ps`
   - thermostat thickness and damping (Warrier: "two layers thermostatted", plus fixed boundary cells, which the template does not do)
   - stop window and tolerance
   - channeling exclusion angle
   - check, checkpoint and snapshot intervals, and the snapshot KE cutoff

## 2. Blocks deploying anywhere (security review)

7. **Agent, after your approval:** fix B1, M1, M2 and M3 from the security review:
   - B1: an upload can exhaust memory or CPU (cap sizes, use the stored WU geometry, limit resources)
   - M1: errors in the wrong class (bad upload means invalid; server problem means transient)
   - M2: generator serials and transaction order
   - M3: canary formatting can be spotted
8. **You + physics-reviewer: decide the outlier release rule (M4).** Today any 2 confirmation runs release a held result, whatever those runs found.
9. **Physics review: remaining items** (its two blockers, plus V5, checkpoint precision, history keying, PKA pick and the thermostat seed after a restart, are already fixed):
   - **You decide (M2):** a run that hits the hard time limit without stabilizing is currently *invalid*. Recommended: count it as valid for credit and trust, but flag it for science, so volunteers aren't punished for physics they can't control.
   - **You decide (M3):** the replica test rejects real rare cascades. Recommended: replicas are "equivalent" whenever both pass V1–V8, and outliers are handled only by the hold.
   - **Agent (M5):** flag cascades whose defects reach the thermostat layer or wrap around the box.
   - **You (M6):** the researched values are live in `config/settings.toml` before you've checked them. If you'd rather the code refuse to run until you sign off, they can be wrapped as `TODO-UNVERIFIED:<value>`.
   - **Agent, minor:**
     - replace V6 (it can never fail when V8 passes) with a check of the client count against the server count
     - V3 cross-checks
     - V2: also bind `potential.mod` and the template
     - fix the `planned_md_steps` docstring
     - canary pool keyed by a settings digest
     - compute the cluster cutoffs from a0
     - filter `bin_population` by campaign

## 3. Needed for valid science

10. **You: fill `validator/plausible_ranges.csv`.** Benchmark counts are in figures only, so digitize them, or derive ranges from your own reference runs. Until then every result fails V7.
11. **You: decide the validator thresholds.**
    - V3 minimum steps; V4 energy tolerance. The smoke test drifted 1–2 × 10⁻⁴ of the PKA energy.
    - outlier sigma, minimum bin size, canary sigma and canary rate
12. **You: calibrate on your laptop.**
    - `ref_work`: run one 5 keV reference WU.
    - BOINC estimates: `fpops_est`, `fpops_bound`, `memory_bytes`, `delay_bound_s`.
    - 10 keV (843,750 atoms) is now a Large-tier WU, with its own BOINC estimates. Measure both tiers.
13. **Physics check: equilibration ensemble.** The benchmarks equilibrate at constant pressure (NPT); the template uses a fixed lattice constant at T. That's fine for 300 K only. Any new temperature needs its own a0.
14. **Agent: Phase 2.** Finalize the interfaces from these decisions; you freeze them (2-step process in the README).

## 4. Before the public alpha

15. **Agent: security M5–M7 and the minor items**:
    - API connection pool and rate limit
    - self-host Three.js and add a content security policy
    - respect BOINC privacy settings
    - separate database roles
    - add `keys/` and `*_private` to `.gitignore`
    - pin dependencies and checksums
16. **You: set up the cloud VM**, HTTPS, backups, and the code-signing ceremony on an offline machine.
17. **Agent + you: run an end-to-end test on a staging BOINC server.** Confirm the `script_validator` / `script_assimilator` argument names and exit codes, and run the SQL against real PostgreSQL and MariaDB.
18. **Docs:** privacy policy, GDPR consent, volunteer FAQ.
19. **You: badge thresholds, `max_in_flight`, `bootstrap_samples`.**
20. **You: find a faculty advisor** before announcing any science result.

## 5. After the alpha

21. Trapping stage (D1, D13), retention model, two-temperature model, screensaver (D5), speed bonus (D2), GPU app version (D10).

## Done this session

- Decisions recorded: EAM potentials; PKA energies of 5 and 10 keV at 300 K from the benchmark papers; reference WU worth 1760 points.
- The LAMMPS template ran in your LAMMPS. The test runs fixed 4 real bugs:
  - missing atom map
  - unsupported `min()` in a variable
  - thermostat energy sign
  - thermostat tally reset by every `run`
- Checkpoint and resume verified by killing LAMMPS and restarting it.
- The server's Wigner–Seitz count matches LAMMPS (3 Frenkel pairs), and real output passes V1–V8.
- Seeds capped below LAMMPS's 900,000,000 limit (the abort was confirmed by test).
