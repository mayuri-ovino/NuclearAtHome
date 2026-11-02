# Nuclear@Home — to-do list (highest priority first)

Updated 2026-11-01. "You" = the human; "agent" = Claude Code.

## 1. Blocks every real cascade run

1. **You: SRIM stopping table for W in W**, saved as `client/potentials/stopping_W.dat` (`docs/literature/PAPERS_TO_OBTAIN.md` #5). Until it exists, the work generator refuses to run.
2. **You: email B. D. Wirth for the Juslin–Wirth W–W potential file** (#1). W_EAM_A is "AT1987 + ZBL core", not JW: its TDE along ⟨100⟩ is ≈ 69 eV against 54.3 for JW, so benchmark comparisons are qualitative until the real file arrives.
3. **You: check the remaining UNVERIFIED values** against papers #2–#4: max displacement 0.005 Å, cluster cutoffs, electronic-stopping cutoff 10 eV.

## 2. Blocks deploying anywhere

4. **Agent, later:** measure TDE the way Warrier does, and SIA dumbbell formation energies, for W_EAM_A (small boxes). Done this round: both re-reviews applied, and BOINC script macros and exit codes checked against the BOINC source.
5. **Agent + you: staging BOINC server.** Install the wrappers from `server/boinc/bin/` and run the SQL against real PostgreSQL and MariaDB. The macros and exit 3 = retry were checked in the BOINC source; still check adaptive replication and the CPU-limit behaviour (SIGXCPU counts as invalid). Size the server for up to 4 GB per concurrent validator.

## 3. Needed for good science (not blocking the alpha)

6. **You: digitize Warrier & Bhardwaj Fig. 2** to replace the sanity-only V7 ranges (#6).
7. **You, when ready: calibrate on your laptop** (postponed at your request). One 5 keV and one 10 keV work unit, to fill the per-tier BOINC estimates: `fpops_est`, `fpops_bound`, `memory_bytes`, `delay_bound_s`.
8. **Physics:** a new temperature needs its own measured a0 (the template has no NPT step).
9. **Agent: Phase 2.** Freeze the interfaces from these decisions; you run the 2-step freeze from the README.

## 4. Before the public alpha

10. **You: operations settings:** `max_in_flight` and badge thresholds (not physics).
11. **You: cloud VM, HTTPS, backups, offline code-signing ceremony.** Use `server/nginx_nah.conf`, and create the database roles listed in `stats/schema.sql`.
12. **Docs:** privacy policy, GDPR consent, volunteer FAQ.
13. **You: find a faculty advisor** before announcing any science result.

## 5. After the alpha

14. Trapping stage, retention model, two-temperature model, screensaver, speed bonus, GPU app version.

## Done

- **Decisions:**
  - EAM potentials; 5 and 10 keV at 300 K; the reference WU is worth 1760 points, and larger WUs scale with work (10 keV ≈ 5,940).
  - Physics and validation decisions made by the main agent at your request, each with its basis, in the `physics_settings.md` decision log.
- **Build:** LAMMPS 29Aug2024 built static with electronic stopping. The tarball matched LAMMPS's published SHA256SUMS.
- **Potential:** W_EAM_A built from the NIST Ackland–Thetford file and validated against LAMMPS's own ZBL. The 300 K a0 (3.1674 Å) was measured.
- **Smoke tests:**
  - The full template runs with the real binary: fixed layer, thermostat and electronic stopping.
  - Energy balances to 1.5e-4 of the PKA energy.
  - Resume works.
  - The client and server defect counts agree.
- **Security (from the first review):**
  - B1: upload caps, server-side geometry, defect cap, resource limits
  - M1: error classes
  - M2: generator ordering, sequence, exclusive record files
  - M3: canaries drawn only for open bins
  - M5: API connection reuse, nginx rate limit, X-Accel file serving
  - M6: self-hosted Three.js plus a CSP
  - M7: privacy gates, day-rounded times, anonymizing deleted accounts
  - minor: key-file ignores, pinned dependencies, lock path, viewer decompression cap, database roles
- **Physics review items:** outliers flagged instead of held (M4 removed), replica rule, V5 for fixed-length runs, V6 client-vs-server cross-check.
