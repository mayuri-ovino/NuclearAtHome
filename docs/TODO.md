# Nuclear@Home — to-do list (highest priority first)

Updated 2026-11-02. "You" = the human; "agent" = Claude Code.

**Campaign 3 gates (physics review 2026-11-03), before any tail result is published:**
- Store each failed result's reason (check ID) in PostgreSQL; define "permanently failed" by the retry chain; publish n_drawn, n_lost and n_in_flight per bin with worst-case tail intervals.
- Run a 10 keV WU with a forced restart through the stock wrapper and the real validator (the calibration's log was overwritten by its harness, so V1–V8 never ran on it).
- Before marking a stale pending row failed, check BOINC has no such WU (else a retry duplicates a live impact); dedupe aggregates on (potential, E, T, direction, seed).
- Do not count WUs that never reached BOINC as attempts; test `create_one` (retry precedence, attempt, retry_of, inputs) against PostgreSQL.
- Record app version / plan class per result for the pooling rule; scale fpops_est and memory by atoms × steps for boxes above 10 keV.

**Direction (2026-11-02):** the project focuses on what volunteers do better than a cluster:
large ensembles and potential comparisons (`docs/scope.md`). Campaign order there:
1 validation (running) → 2 potential uncertainty → 3 distribution tails → 4 higher energies
→ 5 trapping. The most valuable next step is not code: find a fusion-materials researcher
(item 13) and agree Campaign 2's potentials and outputs with them.

## 1. Blocks every real cascade run

Nothing left. The SRIM stopping table, the exact Juslin–Wirth potential and the paper checks were all done 2026-11-02. Remaining physics caveat: Warrier & Bhardwaj use Lindhard–Scharff stopping, and we use SRIM with the same 30 eV cutoff.

## 2. Blocks deploying anywhere

4. **Agent, later:** the full JW Table 3/4 reproduction (⟨110⟩ dumbbell, octahedral site, averaged TDE). The ⟨111⟩ dumbbell already matches: 9.52 vs 9.50 eV. Done this round: both re-reviews applied, and BOINC script macros and exit codes checked against the BOINC source.
5. **Agent + you: staging BOINC server.** Also build the team join codes there (a PHP page in BOINC's web code; it needs BOINC to test). Install the wrappers from `server/boinc/bin/` and run the SQL against real PostgreSQL and MariaDB. The macros and exit 3 = retry were checked in the BOINC source; still check adaptive replication and the CPU-limit behaviour (SIGXCPU counts as invalid). Size the server for up to 4 GB per concurrent validator.

## 3. Needed for good science (not blocking the alpha)

6. **You: digitize Warrier & Bhardwaj Fig. 2** to replace the sanity-only V7 ranges (#6).
7. **Calibration:** 5 keV done (5,800 s on one core, 314 MB, 9 Frenkel pairs; passes V1–V8). 10 keV done (≈24,000 s on one shared core, 1.03 GB, 6 Frenkel pairs, V4 5.5e-3; full validator not run because the calibration's log was overwritten on resume). Still to do: replace the assumed 5e9 FLOPS/core with a BOINC benchmark. Credit note (unconfirmed, contention-confounded: one run each, 10 keV on a core shared with BOINC and extrapolated from its last segment): 10 keV is worth 3.375× a 5 keV WU and may take somewhat longer than that ratio. Measure both energies on a quiet core before deciding whether to adjust credit.
8. **Physics:** a new temperature needs its own measured a0 (the template has no NPT step).
9. **Agent: Phase 2.** Freeze the interfaces from these decisions; you run the 2-step freeze from the README.

## 4. Before the public alpha

10. **You: operations settings:** `max_in_flight` and badge thresholds (not physics).
11. **You: cloud VM, HTTPS, backups, offline code-signing ceremony.** Use `server/nginx_nah.conf`, and create the database roles listed in `stats/schema.sql`.
12. **Docs:** privacy policy, GDPR consent, volunteer FAQ.
13. **You: find a faculty advisor** before announcing any science result.

## 5. After the alpha

14. Trapping stage, retention model, two-temperature model, screensaver, speed bonus.
16. Windows: CPU version 1.02 built (`bash client/build_lammps_windows.sh <dir>`, MinGW in a container, stock wrapper 26019) and registered on staging; small cascades, interrupt/resume and the crash-recovery path pass under Wine. The Windows OpenCL GPU build (`... <dir> gpu`, double precision, LAMMPS's static OpenCL loader) is registered as 1.03 (plan class opencl_nvidia_101); under Wine it runs in CPU mode with identical results, but the GPU path is untested. Still to do: a full 5 keV run on a real Windows PC for CPU and GPU (energy check, memory, time).
15. GPU: the OpenCL build works (core 0xa2, `bash client/build_lammps.sh <dir> gpu`). Still to do on staging: register the opencl_* app versions in BOINC, calibrate GPU work units, test on AMD and Intel GPUs. CUDA and HIP builds are not started.

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
