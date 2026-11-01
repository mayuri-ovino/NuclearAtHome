# Statistics specification

Status: DRAFT

BOINC's own MariaDB keeps users, hosts, teams, and credit. Science and extended
stats live in PostgreSQL.

## Tables (PostgreSQL)

| Table | Key columns |
|---|---|
| `wu_results` | wu_id, wu_type, campaign_id, host_id, user_id, material_family, potential_id, temperature_k, pka_energy_ev, validated, points_base, points_awarded, sent_at, reported_at |
| `cascade_stats` | wu_id, n_vacancies, n_interstitials, peak_displaced, cluster_sizes_vac (int[]), cluster_sizes_int (int[]) |
| `trapping_stats` | wu_id, species, n_inserted, n_trapped, n_desorbed |
| `trap_sites` | wu_id, site_type, cluster_size, n_occupants, binding_energy_ev |
| `tpf_samples` | host_id, wu_id, slot_kind (cpu/gpu), tpf_s, recorded_at |
| `host_daily` | host_id, day, points, wus_valid, wus_invalid, est_ppd, actual_ppd_7d |
| `user_daily`, `team_daily` | id, day, points, ppd, rank |
| `badges` | user_id, badge_id, awarded_at |
| `discoveries` | discovery_id, wu_id, user_id, description, confirmed_by, approved_at |
| `retention_estimates` | run_id, material, wall_temp_k, time_s, retained_per_m2, lower, upper, assumptions_version |

## Aggregation jobs
- Hourly: est_ppd per host from recent TPF samples (`stats/ppd.py`).
- Daily: host/user/team daily tables, ranks, badges, BOINC XML stats export.
- Daily: science aggregates per (material, energy bin, temperature bin) with
  mean, standard error, and sample size.
- On demand: retention estimate runs (server model), versioned.

## API (read-only, JSON, versioned)

| Endpoint | Returns |
|---|---|
| `GET /api/v1/hosts/{host_id}` | TPF history, est PPD, actual PPD, WU counts, CPU/GPU type |
| `GET /api/v1/users/{user_id}` | points, PPD, rank, badges, discoveries |
| `GET /api/v1/teams/{team_id}` | points, PPD, rank, members count |
| `GET /api/v1/project/summary` | active hosts, FLOPS estimate, WUs/day, campaign progress |
| `GET /api/v1/science/cascades?material=&energy_bin=&temp_bin=` | defect statistics with error bars and n |
| `GET /api/v1/science/traps?material=&site_type=` | binding energy distributions |
| `GET /api/v1/science/retention?material=&wall_temp_k=` | retained tritium vs time with uncertainty band and assumption list |
| `GET /api/v1/cascades/{wu_id}/snapshots` | snapshot file URLs for the 3D viewer |

Host and user endpoints never expose IP addresses, emails, or anything beyond
what BOINC publicly shows.
