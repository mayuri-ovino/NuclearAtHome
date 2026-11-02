# Validator specification

Status: DRAFT

## Principles
- MD is chaotic: never compare results bit-for-bit.
- Checks fail closed: missing data, malformed data, or a TODO threshold means FAIL.
- Each check is a pure function `(result, workunit, context) -> (passed: bool, reason: str)`.

## Per-result checks (all must pass)

| ID | Check | Rule | Threshold |
|---|---|---|---|
| V1 | Schema | Result validates against `result_schema.json` | — |
| V2 | Integrity | sha256 of every output file matches `integrity.output_sha256`; input hash matches the WU sent | — |
| V3 | Completeness | `md_steps_completed` ≥ the minimum for this WU; stop condition reached | 20,000 steps (20 ps at the 1 fs maximum timestep) |
| V4 | Energy conservation | \|E_total(t) + thermostat_removed(t) + electronic_loss(t) − E_total(0)\| / (PKA energy + \|thermostat_removed(t)\|) ≤ tolerance at every logged sample | 0.01 (physics_settings.md decision log) |
| V5 | Stabilization | The run reached the fixed 20 ps end time (no early stop; physics decision log) | window 20 ps, tolerance 0 pairs |
| V6 | Frenkel balance | n_vacancies == n_interstitials (no atoms created or lost) | exact |
| V7 | Plausible range | Frenkel pairs within the range for (material, energy bin, temperature bin) in `validator/plausible_ranges.csv` | alpha: sanity bounds (NRT); to be replaced by Warrier & Bhardwaj Fig. 2 (TODO-LIT) |
| V8 | Atom count | `n_atoms` equals the WU's expected count | exact |
| V9 | Trapping balance (stage B) | n_trapped_end + n_free_end + n_desorbed == n_inserted | exact |
| V10 | Binding energies (stage B) | All within the plausible range for site type | from table (TODO-LIT) |

## Replication and comparison
- **New hosts:** every WU replicated (quorum 2). Replicas pass if both pass V1–V10 and
  their Frenkel pair counts are consistent with the population distribution for that
  bin (not with each other, since each cascade differs). Population test: none in the alpha;
  replicas are equivalent when both pass V1–V8 (decision log).
- **Trusted hosts:** not in the alpha: every WU is replicated (quorum 2). Adaptive replication
  and its spot-check rate are decided before the public release.
- **Canaries:** hidden known-answer WUs at 2% of WUs (pass within 3 σ). Canaries use a fixed seed and
  platform-specific reference runs; pass if statistics match references within tolerance.
- **Outliers:** results beyond 5 standard deviations from the bin mean (once the bin has at least
  30 results) are flagged in the science database, never rejected or held (physics review).

## Host trust score
- Score in [0, 1]; new hosts start at 0.
- Increases with each consecutive valid result; any invalid result or failed canary
  resets toward 0 and returns the host to full replication.
- Not used in the alpha (every WU is replicated). The update rule is decided with adaptive replication.
- Hosts below a threshold get reduced daily quotas (BOINC built-in).

## Plausible ranges file
`validator/plausible_ranges.csv` columns:
`material,energy_bin_kev_min,energy_bin_kev_max,temp_bin_k_min,temp_bin_k_max,frenkel_min,frenkel_max,source`
Every row needs a source (TODO-LIT) or a reference-cluster run ID.
